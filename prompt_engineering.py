import os
import openai
import json
from utils.generate_template import gen_full_prompt

openai.api_key = os.getenv("OPENAI_API_KEY")

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages={"role": "user", "content": "Hello world!"},
    n=1
)
