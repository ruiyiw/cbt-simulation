from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import json

search_string = "client"
init_resource_url = f"https://search-alexanderstreet-com.proxy.lib.umich.edu/search?searchstring={search_string}&sort_by=search_api_relevance&sort_order=DESC&showall=1&f%5B0%5D=therapies_facet%3ACognitive%20behavioral%20therapy"
# page_range = (0, 10)
page_end = 22
timeout = 60

def process_sentence(span):
    sentence = ""
    for i in range(len(span)):
        sentence += span[i].text

    role, content = "", ""
    word_list = sentence.rstrip().split(":", 1)
    if len(word_list[0].split()) == 1:
        role = word_list[0]
        content = " ".join(word_list[1:])
    else:
        content = sentence
    content = content.strip().replace(u"\ufffd", "'").replace(u"\u2014", "-").replace('\"', "'").replace(u"\u2019", "'")
    return role, content


def truncate_title(title):
    # title_list = title.split(":", 1)
    # title = title_list[0]
    return title.replace('\"', "'")


def write_to_jsonl(json_dict):
    with open("CBT_utterance.jsonl", "a") as f:
        json.dump(json_dict, f)
        f.write('\n')


def convert_utterances_to_dict(text_list, title, document_id):
    role_list, content_list = [], []

    for i in range(len(text_list)):
        span = text_list[i].find_elements(By.CSS_SELECTOR, 'span')
        # span = text_list[i].find_elements(By.XPATH, './/span')
        if len(span) > 0:
            role, content = process_sentence(span)
            if role == "":
                if len(role_list) > 0:
                    role = role_list[-1]
                else:
                    continue
            role_list.append(role)
            content_list.append(content)

    sub_dict = {
        'title' : title,
        'document_id' : document_id,
        'dialogue_len' : len(role_list),
        'role' : role_list,
        'content' : content_list
    }
    write_to_jsonl(sub_dict)


def update_url(page_id):
    if page_id == 0:
        return init_resource_url
    else:
        return f"https://search-alexanderstreet-com.proxy.lib.umich.edu/search?searchstring={search_string}&sort_by=search_api_relevance&sort_order=DESC&page={page_id}&showall=1&f%5B0%5D=therapies_facet%3ACognitive%20behavioral%20therapy"


def init_driver():
    o = webdriver.ChromeOptions()
    o.add_argument(r'--user-data-dir=/Users/pamela/Documents/research/code/therapy-data/Chrome/')
    o.add_argument(r'--profile-directory=Profile 6')
    o.add_argument('--no-sandbox')
    # o.add_argument('--headless')
    o.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=o)
    wait = WebDriverWait(driver, timeout)
    return driver, wait


def write_log(count_id, page_end):
    with open("log.txt", 'w') as f:
        f.write(str(count_id))
        f.write('\n')
        f.write(str(page_end))
        f.write('\n')


def read_log():
    with open("log.txt", 'r') as f:
        lines = f.readlines()
        count_id = int(lines[0])
        page_start = int(lines[1])
    return count_id, page_start


def automate(driver, wait):
    home_window = driver.current_window_handle
    assert len(driver.window_handles) == 1

    # count_id, page_start = read_log()
    count_id = 0
    page_start = 0
    
    for page_id in range(page_start, page_end):
        driver.get(update_url(page_id))
        search_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-result-item-info')))
        link_list = []
        for row in search_elements:
            link = row.find_element(By.TAG_NAME, 'a').get_attribute('href')
            link_list.append(link)

        for link in link_list:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)

            _ = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'title')))
            # Filter irrelevant entries
            try:
                assert driver.title.split()[0] == "Client"
            except:
                driver.close()
                driver.switch_to.window(home_window)
                continue

            access_check = driver.find_elements(By.XPATH, '//*[@id="entity-viewer"]/div[2]/div[2]/div[1]/div[1]')
            if len(access_check) > 0:
                with open("CBT_unaccessible_list.txt", 'a') as f:
                    title = truncate_title(driver.title)
                    f.write(title)
                    f.write('\n')
            else:
                try:
                    text_list = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ucv-page-0"]/div[2]/div[1]/div/text'))).find_elements(By.CSS_SELECTOR, 'p')
                    raw_title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ucv-page-0"]/div[1]'))).text
                    title = truncate_title(raw_title)
                    print(title)
                    convert_utterances_to_dict(text_list, title, count_id)
                    count_id += 1
                except:
                    driver.close()
                    driver.switch_to.window(home_window)
                    continue

            driver.close()
            driver.switch_to.window(home_window)

    write_log(count_id, page_end)


def main():
    driver, wait = init_driver()
    automate(driver, wait)

    driver.quit()


if __name__ == "__main__":
    main()

# row_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-result-item-info')))
# link_list = []
# for row in row_elements:
#     link = row.find_element(By.TAG_NAME, 'a').get_attribute('href')
#     link_list.append(link)


# df = pd.DataFrame(columns=["title", "document_id", "utterance_id", "role", "utterance"])
# create json file
# json_dict = {}
# count_id = 0
# for link in link_list:
# for i in range(2):
#     link = link_list[i]
#     driver.execute_script("window.open('');")
#     driver.switch_to.window(driver.window_handles[1])
#     driver.get(link)

#     text_list = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ucv-page-0"]/div[2]/div[1]/div/text'))).find_elements(By.CSS_SELECTOR, 'p')
#     raw_title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ucv-page-0"]/div[1]'))).text
#     title = truncate_title(raw_title)
#     print(title)
#     json_dict[title] = convert_utterances_to_dict(text_list, title, count_id)

#     count_id += 1

    # print(text_list)

    # print_selection_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ucv-viewer"]/div/div/div[2]/div[1]/div/div[8]/div/button[1]')))
    # print_selection_button.click()
    # time.sleep(3)
    # radio_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="radio"][value="document"]')))
    # # radio = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ucv-viewer"]/div/div/div[2]/div[1]/div/div[8]/div[2]/div/div/div/label[2]/input[@value="document"]')))
    # radio_button.click()
    # time.sleep(3)
    # print_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ucv-viewer"]/div/div/div[2]/div[1]/div/div[8]/div[2]/div/div/div/div/div/button')))
    # print_button.click()


    # driver.close()
    # driver.switch_to.window(home_window)

# with open('utterance_dict.json', 'w') as outfile:
#     json.dump(json_dict, outfile)

# driver.quit()