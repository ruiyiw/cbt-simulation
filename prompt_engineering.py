import os
import openai
import json
from utils.generate_template import gen_full_prompt

openai.api_key = os.getenv("OPENAI_API_KEY")

gen_full_prompt()

