from scripts.utils.openai_generation import generate_response
import uuid


# messages = [{"role": "user",
#              "content": "I'm a researcher on prompt engineering LLMs. Can you think of a list of instructions for LLMs to summarize a successful patient profile from a therapy session data?"}]
# response = generate_response(
#     model_name="gpt-4-1106-preview", messages=messages)
# print(response)

import json
with open("data/therapy_session_data/CBT_therapy-data.json", 'r') as f:
    dict_list = json.loads(f.read())
    for dic in dict_list:
        dic["id"] = str(uuid.uuid4())

with open("data/therapy_session_data/CBT_therapy-data.json", 'w') as f:
    f.write(json.dumps(dict_list, indent=4))
