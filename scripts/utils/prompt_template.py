import json
import os

current_script_dir = os.path.dirname(os.path.abspath(__file__))


def gen_profile_prompt(session_data):

    with open(os.path.join(current_script_dir, "../../data/patient_sample_data/abe_sample_profile.json"), 'r') as f:
        one_shot_profile = json.loads(f.read())

    with open(os.path.join(current_script_dir, "../../data/blank_template/patient_profile.json"), 'r') as f:
        profile_json_format = json.loads(f.read())

    profile_prompt = """
    I am a researcher working on simulating patients with mental health issues for training novice therapists. I expect you to assist me to analyze a Cognitive Bahavioral Therapy session transcript and extract and summarize key information for the patient profile.
    Your ultimate goal is to generate a patient profile that strictly follow the below JSON format string, and there should be no blanks:

    {profile_json_format}

    Below is the patient profile template that you should generate based on the therapy session transcript.

    {one_shot_profile}

    Below is the raw therapy session transcript. Keep in mind that the patient is the "[Client]" in the transcript.

    {session_data}

    When generating patient profile based on the therapy session transcript, please follow the below instructions:
    1. Follow CBT concepts: Your generated profile should resemble the standard patient profile for Cognitive Behavioral Therapy.
    2. Proper Imagination of the patient: If some parts of the profile cannot be filled out based on the therapy transcript, you are expected to make up those content but make sure the content is consistent with the existing information.
    3. Anonymize Data: Please confirm that all personal identifiers have been removed from the data before proceeding with the summary. You are expected to create an alias of the patient.
    4. Identify Key Themes: Review the session data and identify the key themes discussed during the therapy session, such as progress with specific issues, coping strategies being employed, and any new concerns raised by the patient.
    5. Summarize Goals and Plans: Outline the therapeutic goals discussed in the session, including short-term and long-term objectives, as well as any action plans agreed upon by the therapist and the patient.
    6. Record Patient's Self-Reported State: Include a brief description of the patient's self-reported mental and emotional state, as discussed in the session.
    7. Therapist Observations: Provide insights from the therapist's observations that were not explicitly stated by the patient but are relevant to their treatment and progress.

    Your output should only be the JSON string. Do not include identifier such as "```json```" any introductory sentences. Make sure that the keys and values are enclosed in double quotes.
    """.format(profile_json_format=profile_json_format, one_shot_profile=one_shot_profile, session_data=session_data)

    return profile_prompt


def gen_ccd_prompt(session_data, patient_profile):

    with open(os.path.join(current_script_dir, "../../data/blank_template/patient_ccd.json"), 'r') as f:
        ccd_json_format = json.loads(f.read())

    ccd_prompt = """
    You should follow the concepts of cognitive behavioral therapy and figure out the cognitive behavioral model of the patient from a therapy session.
    Your ultimate goal is to generate the cognitive behavioral model that strictly follow the below JSON format string, and there should be no blanks. Note that the "behavorial_models" list can have flexible list length.

    {ccd_json_format}

    Below is the raw therapy session transcript. Keep in mind that the patient is the "[Client]" in the transcript.

    {session_data}

    Below is the patient profile for you reference:

    {patient_profile}

    Your output should only be the JSON string. Do not include identifier such as "```json```" or any introductory sentences. Make sure that the keys and values are enclosed in double quotes.
    """.format(ccd_json_format=ccd_json_format, session_data=session_data, patient_profile=patient_profile)

    return ccd_prompt
