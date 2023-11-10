import openai
import time
import os


def generate_response(model_name, input):
    openai.api_key = os.getenv("OPENAI_API_KEY")
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
        return generate_response(messages)

    return completion["choices"][0]["message"]["content"]
