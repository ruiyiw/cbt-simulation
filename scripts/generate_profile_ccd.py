import argparse
import json
import os
from utils.openai_call import generate_response
from utils.prompt_template import gen_profile_prompt, gen_ccd_prompt
from utils.generation_utils import parse_json_response


def preprocess(session_dict: str) -> str:
    template = """{role}: {content}\n"""
    conv_str = ""
    for utterance in session_dict["conversations"]:
        conv_str += template.format(
            role=utterance["role"], content=utterance["content"])
    return conv_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session_data_dir', type=str, required=True,
                        help="Therapy session data with JSON format.")
    parser.add_argument('--output_dir', type=str, default="../tmp/",
                        help="Output directory of generated patient profile")
    parser.add_argument('--model', type=str, default="gpt-4-1106-preview")
    args = parser.parse_args()

    with open(args.session_data_dir, 'r') as f:
        session_dict_list = json.loads(f.read())

    for i in range(len(session_dict_list)):
        session_dict = session_dict_list[i]
        session_data = preprocess(session_dict)
        profile_prompt = gen_profile_prompt(session_data)
        profile = generate_response(
            args.model, profile_prompt)
        ccd_prompt = gen_ccd_prompt(session_data, profile)
        ccd = generate_response(args.model, ccd_prompt)

        file_folder = os.path.join(
            args.output_dir, f'{session_dict["id"]}/')
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

        with open(os.path.join(file_folder, "profile.json"), "w") as f:
            f.write(json.dumps(json.loads(profile), indent=4))

        with open(os.path.join(file_folder, "CCD.json"), "w") as f:
            f.write(json.dumps(json.loads(ccd), indent=4))


if __name__ == "__main__":
    main()
