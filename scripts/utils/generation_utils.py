import json
import re


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
