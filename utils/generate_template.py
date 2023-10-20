import json
import os
import openai

DATA_DIR = "data/"
INTAKE_FILE = "profile_data/abe_sample_intake_info.json"
HISTORICAL_FILE = "profile_data/abe_sample_historical_info.json"
CCD_FILE = "ccd_data/abe_sample_traditional.json"

def get_patient_name():
    with open(os.path.join(DATA_DIR, INTAKE_FILE), "r") as f:
        intake_dict = json.loads(f.read())
    return intake_dict["name"]


def gen_intake_paragraph():
    with open(os.path.join(DATA_DIR, INTAKE_FILE), "r") as f:
        intake_dict = json.loads(f.read())
    intake_dict_str = str(intake_dict)

    prompt = """You will be given a JSON dictionary of a patient's intake records from cognitive behavioral therapy sessions. Please write a paragraph incorporating all fields in the JSON dictionary.  You must use "{key from the dictionary}" to represent text as long as it fits in the text. You can rephrase the values from the dictionary when you feel necessary, but try to use "{key from the dictionary}" as much as possible. Be sure to include everything from the dictionary.\n\nHere's an example:\n{name} is a {identifying_info[age]}-year-old {identifying_info[gender]} who identifies as {identifying_info[sexual_orientation]}. He has a {identifying_info[cultural_heritage]} background\n\n""" + """JSON dictionary:\n{intake_dict_str}""".format(intake_dict_str=intake_dict_str)

    completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role" : "user", "content" : prompt}]
    )

    intake_para = """The following paragraph include {name}'s session intake information:\n\n""".format(**intake_dict)
    intake_para += completion["choices"][0]["message"]["content"].format(**intake_dict)
    # intake_para += """{name} is a {identifying_info[age]}-year-old male who identifies as heterosexual. He has an {identifying_info[cultural_heritage]} background. His religious affiliation is with the {identifying_info[religion]}, and he currently resides in a {identifying_info[living_environment]}. Professionally, Abe is {identifying_info[employment_status]} and falls under the {identifying_info[socioeconomic_status]} category. He approached therapy with a {chief_complaint}. Upon further evaluation, several major symptoms were identified. Emotionally, he has been experiencing {major_symptoms[emotional][0]}, {major_symptoms[emotional][1]}, as well as {major_symptoms[emotional][2]} and {major_symptoms[emotional][3]}. Cognitively, Abe faces {major_symptoms[cognitive][0]} and {major_symptoms[cognitive][1]}. Behaviorally, there's a noticeable {major_symptoms[behavioral][0]} and he has shown signs of {major_symptoms[behavioral][1]}. Physiologically, Abe reported feeling {major_symptoms[physiological][0]}, {major_symptoms[physiological][1]}, and has a {major_symptoms[physiological][2]}. Additionally, he finds {major_symptoms[physiological][3]} difficult and has a {major_symptoms[physiological][4]}. During his evaluation, {mental_status}. The primary diagnosis given was {diagnosis}. In terms of psychiatric treatment, Abe is on {current_psychiatric_treatment[medication]} and there are {current_psychiatric_treatment[adherence_and_side_effects]} to report. Concerning his social ties, {current_significant_relationships}.""" # example result from gpt-4
    return intake_para


def gen_historical_paragraph():
    with open(os.path.join(DATA_DIR, HISTORICAL_FILE), "r") as f:
        historical_dict = json.loads(f.read())
    
    historical_para = """The following sections include {name}'s historical information.\n\n{name}'s best lifetime functioning (including strengths, assets, and resources):\n {best_lifetime_functioning} \n\n{name}'s history of present illness:\n{history_of_present_illness} \n\n{name}'s history of psychiatric, psychological or substance use problems and impact on functioning:\n{history_of_psychological_problem_impact} \n\n{name}'s history of psychiatric, psychological or substance abuse treatment, type, level of care, and response:\n{history_of_psychological_care} \n\n{name}'s personal, social, educational, and vocational history:\n{personal_history} \n\n{name}'s medical history and limitations:\n{medical_history_and_limitations}""".format(**historical_dict)
    
    if historical_dict["current_non_psychiatric_treatment"]["medication"] != "none":
        historical_para += """\n\nThis is {name}'s current non-psychiatric medications:\n{current_non_psychiatric_treatment[medication]}""".format(**historical_dict)
        if historical_dict["current_non_psychiatric_treatment"]["adherence_and_side_effects"] != "none":
            historical_para += """\n{name} experience adherence and side effects:{current_non_psychiatric_treatment[adherence_and_side_effects]}""".format(**historical_dict)
    
    return historical_para


def gen_ccd_text():
    with open(os.path.join(DATA_DIR, CCD_FILE), 'r') as f:
        ccd_dict = json.loads(f.read())
    ccd_dict_str = str(ccd_dict)
    
    prompt = """Strictly following the concepts of cognitive behavioral therapy, figure out the cognitive behavioral model in the following JSON dictionary. You should make your text organized and structured. You should not output a JSON dictionary.\n\nTarget JSON dictionary:\n{ccd_dict_str}""".format(ccd_dict_str=ccd_dict_str)

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role" : "user", "content" : prompt}]
    )

    ccd_text = completion["choices"][0]["message"]["content"]
    return ccd_text


def gen_full_prompt():
    name = get_patient_name()
    intake_para = gen_intake_paragraph()
    historical_para = gen_historical_paragraph()
    ccd_text = gen_ccd_text()

    prompt = """Imagine you are {name}, a patient who has been suffering from (potential) mental health issues. You have been attending sessions for several weeks. Your task is to act and speak as {name} would with a therapist during a cognitive behavioral therapy (CBT) session. You should try your best to align with {name}'s session notes and background information in the 'Patient's history' field. Your thought process should strictly follow the cognitive conceptualization diagram provided in the 'Cognitive Conceptualization Diagram' field. However, you must not directly dispose any text from the diagram because a real patient cannot structure the underlying thought processes. Additionally, you should try your best to act like a real patient with mental health issues, maintaining the conversation's naturalness and realism.\n\nPatient's history:\n{intake_para}\n\n{historical_para}\n\nCognitive Conceptualization Diagram will be provided in the next prompt.""".format(name=name, intake_para=intake_para, historical_para=historical_para, ccd_template=name)

    print(prompt)

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role" : "user", "content" : prompt}]
    )
    
    prompt = """Cognitive Conceptualization Diagram:\n{ccd_text}\n\nIn the following conversation, you should start simulating {name} during a cognitive behavioral therapy session, and the user is a therapist. Remember, a real patient is never expressive and may stuck in his own feelings. You should talk less about your feelings or symptoms. What you learned from the cognitive conceptualization diagram should not be exposed to the therapist so easily. Only respond "Yes, now I am {name}" if you understand.""".format(ccd_text=ccd_text, name=name)

    print(prompt)

# def main():
#     gen_ccd_text()

# if __name__ == "__main__":
#     main()
