import openai
import time
import os
import argparse
from dotenv import load_dotenv
from utils.role_prompt import RolePrompt
from utils.generation_utils import generate_openai_response
import json

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

model_name = "gpt-4"


def generate_response(messages):
    try:
        completion = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            n=1
        )
    except:
        print("Retrying due to an error...")
        time.sleep(20)
        return generate_response(messages)

    return completion


def construct_messages(messages, curr_response):
    messages.append({"role": "user", "content": curr_response})
    return messages


def construct_context(prev_context, curr_turn, turn_num):
    if curr_turn["role"] == "therapist":
        context = prev_context + \
            "Turn #{turn_num}: Therapist said: \"{response}\"\n\n".format(
                turn_num=turn_num, response=curr_turn["response"])
    else:
        context = prev_context + \
            "Turn #{turn_num}: Patient said: \"{response}\"\n\n".format(
                turn_num=turn_num, response=["response"])
    return context


def chat_loop(role_prompt, max_turn_num):
    therapist_messages = []
    patient_messages = []
    therapist_messages.append(
        {"role": "system", "content": role_prompt.gen_therapist_initial_prompt()})
    patient_messages.append(
        {"role": "system", "content": role_prompt.gen_patient_initial_prompt()})
    therapist_messages.append(
        {"role": "user", "content": role_prompt.gen_therapist_initial_response()})

    initial_system_prompts = {
        "therapist_system_msg": therapist_messages[0]["content"],
        "patient_system_msg": patient_messages[0]["content"]
    }
    responses = []

    round = 0
    while round < max_turn_num:
        response_dict = {
            "round": round // 2,
            "therapist": "",
            "patient": ""
        }

        print("Round:{}".format(round))
        completion = generate_response(therapist_messages)
        response = completion["choices"][0]["message"]["content"]
        therapist_messages.append({"role": "assistant", "content": response})
        patient_messages.append({"role": "user", "content": response})
        response_dict["therapist"] = response
        print(response)

        round += 1

        completion = generate_response(patient_messages)
        response = completion["choices"][0]["message"]["content"]
        patient_messages.append({"role": "assistant", "content": response})
        therapist_messages.append({"role": "user", "content": response})
        response_dict["patient"] = response
        print(response)
        responses.append(response_dict)

        round += 1

    # Construct CBT diagram
    therapist_messages[-1]["content"] = role_prompt.gen_ccd_reconstruction_prompt()
    completion = generate_response(therapist_messages)
    ccd_dict = completion["choices"][0]["message"]["content"]

    return initial_system_prompts, responses, ccd_dict


def main():
    parser = argparse.ArgumentParser(
        description="Self-defined parameters for bot play")
    parser.add_argument("--patient-model", default="gpt-4",
                        help="Model of patient agent")
    parser.add_argument("--therapist-model", default="gpt-4",
                        help="Model of therapist agent")
    parser.add_argument("--profile-dir", required=True,
                        help="Directory of patient profile and CCD")
    parser.add_argument("--blank-dir", default="../data/blank_template/",
                        help="Blank directory of patient profile and CCD")
    parser.add_argument("--max-turn", type=int, default=20)
    parser.add_argument("--output-dir", default="../reconstruction_results/")
    args = parser.parse_args()

    role_prompt = RolePrompt(generated_data_dir=args.profile_dir,
                             blank_data_dir=args.blank_dir, max_turn_num=args.max_turn)
    initial_system_prompts, responses, ccd_dict = chat_loop(
        role_prompt=role_prompt, max_turn_num=args.max_turn)

    session_dir = args.profile_dir.split("/")[-1]
    if not os.path.exists(os.path.join(args.output_dir, session_dir)):
        os.makedirs(os.path.join(args.output_dir, session_dir))

    with open(os.path.join(args.output_dir, session_dir, "system_prompts.json "), "w") as f:
        f.write(json.dumps(initial_system_prompts, indent=4))

    with open(os.path.join(args.output_dir, session_dir, "conversations.json "), "w") as f:
        f.write(json.dumps(responses, indent=4))

    with open(os.path.join(args.output_dir, session_dir, "reconstructed_ccd.json "), "w") as f:
        f.write(json.dumps(ccd_dict, indent=4))

    print(responses)
    print(ccd_dict)


if __name__ == "__main__":
    main()
