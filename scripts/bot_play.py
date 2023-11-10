import openai
import time
import os
from utils import role_prompts

openai.api_key = ""

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


def chat_loop():
    therapist_messages = []
    patient_messages = []
    therapist_messages.append(
        {"role": "system", "content": role_prompts.therapist_initial_prompt})
    patient_messages.append(
        {"role": "system", "content": role_prompts.patient_initial_prompt})
    therapist_messages.append(
        {"role": "user", "content": role_prompts.therapist_initial_response})
    responses = []

    chat_max_length = 20
    round = 0
    while round < chat_max_length:
        print("Round:{}".format(round))
        completion = generate_response(therapist_messages)
        response = completion["choices"][0]["message"]["content"]
        therapist_messages.append({"role": "assistant", "content": response})
        patient_messages.append({"role": "user", "content": response})
        responses.append(response)
        print(response)

        completion = generate_response(patient_messages)
        response = completion["choices"][0]["message"]["content"]
        patient_messages.append({"role": "assistant", "content": response})
        therapist_messages.append({"role": "user", "content": response})
        responses.append(response)
        print(response)

        round += 1

    # Construct CBT diagram
    therapist_messages[-1]["content"] = role_prompts.cbt_instruction
    completion = generate_response(therapist_messages)
    cbt_dict = completion["choices"][0]["message"]["content"]

    return responses, cbt_dict


def main():
    responses, cbt_dict = chat_loop()
    print(responses)
    print(cbt_dict)


if __name__ == "__main__":
    main()
