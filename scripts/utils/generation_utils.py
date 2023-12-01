import json
import re
import openai
import time
import os
from dotenv import load_dotenv

load_dotenv()


def parse_json_response(response):
    try:
        # Regular expression to find a JSON string
        print(response)
        json_match = re.search(r'\{.*\}', response)
        if json_match:
            json_str = json_match.group()
            json_str = re.sub(r"(\w+)'(\w+)", r'\1"\2',
                              json_str.replace("'", '"'))
            # Parse the JSON string
            print(json_str)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON found in the output")
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        # Handle other errors
        print(f"Error: {e}")


def generate_openai_response(model_name, input):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages = [{"role": "user", "content": input}]
    try:
        completion = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            n=1
        )
    except:
        print("Error calling OpenAI API")
        time.sleep(20)
        return generate_openai_response(messages)

    return completion["choices"][0]["message"]["content"]
