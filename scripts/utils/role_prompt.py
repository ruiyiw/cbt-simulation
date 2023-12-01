import os
import json
from utils.generation_utils import generate_openai_response


class RolePrompt():
    def __init__(self, generated_data_dir, blank_data_dir, max_turn_num):

        def read_profile_ccd(data_dir):
            with open(os.path.join(data_dir, "profile.json"), "r") as f:
                profile_json = json.loads(f.read())
            with open(os.path.join(data_dir, "ccd.json"), "r") as f:
                ccd_json = json.loads(f.read())
            patient_name = profile_json["name"]
            return patient_name, profile_json, ccd_json

        self.patient_name, self.profile_json, self.ccd_json = read_profile_ccd(
            generated_data_dir)
        _, self.blank_profile_json, self.blank_ccd_json = read_profile_ccd(
            blank_data_dir)

        self.model_name = "gpt-4-1106-preview"  # We use GPT-4-turbo by default
        self.max_turn_num = max_turn_num

    def gen_therapist_initial_prompt(self):
        return """
        You are a skilled psychotherapist well-versed in Cognitive Behavioral Therapy (CBT) principles. Your task is to simulate a therapeutic conversation with a patient named {patient_name} who is experiencing anxiety and stress. Remember to incorporate key CBT techniques such as identifying and challenging cognitive distortions, using behavioral experiments, and problem-solving strategies. Address the interplay between thoughts, feelings, and behaviors, and assist {patient_name} in developing coping strategies to manage their symptoms. Your responses should demonstrate empathy, foster a supportive atmosphere, and encourage reflection and self-exploration. Your goal is to figure the cognitive conceptualization diagram after the session ends. The format of the diagram that you need to fill in is as follows:\n\n{dictionary}. Be sure to fully utilize {max_turn_num} turns to access the patient, but you should not exceed {max_turn_num} turns.
        """.format(patient_name=self.patient_name, dictionary=str(self.blank_ccd_json), max_turn_num=self.max_turn_num)

    def gen_therapist_initial_response(self):
        return """
        Now you will meet patient {patient_name}. Please start the therapy session:
        """.format(patient_name=self.patient_name)

    def gen_patient_initial_prompt(self):

        profile_prompt = """
        You will be given a JSON dictionary of a patient's intake records from cognitive behavioral therapy sessions. Please write a paragraph incorporating all fields in the JSON dictionary. Please keep the paragraph as original to the JSON dictionary as possible. However, you are allowed rephrase the text.\n\n Here's the JSON dictionary:\n{profile_json}
        """.format(profile_json=str(self.profile_json))
        profile_paragraph = generate_openai_response(
            self.model_name, profile_prompt)

        ccd_prompt = """
        Strictly following the concepts of cognitive behavioral therapy, figure out the cognitive behavioral model in the following JSON dictionary. You should make your text organized and structured. You should not output a JSON dictionary.\n\nHere's the JSON dictionary:\n{ccd_json}
        """.format(ccd_json=str(self.ccd_json))
        ccd_paragraph = generate_openai_response(
            self.model_name, ccd_prompt)

        return """
        Imagine you are {patient_name}, who has been suffering from (potential) mental health issues. Your task is to act and speak as Abe would with a therapist. Abe's background information is in the 'Patient's history' field. Abe's cognition modeling is provided in the 'Cognitive Conceptualization Diagram' field.\n\n 'Patient's history':\n\n {profile_paragraph}\n\n 'Cognitive Conceptualization Diagram': \n\n {ccd_paragraph}\n\n
        In the following conversation, you should start simulating Abe during therapy session, and the user is a therapist. 

        You must follow the following rules:
        1. Natural Presentation:
            - The LLM should emulate the demeanor and responses of a genuine patient, ensuring authenticity in its interactions.
        2. Subtlety in Conversations:
            - A real patient often requires extensive dialogue before delving into core issues. It's challenging for therapists to pinpoint the patient's genuine thoughts and emotions. Thus, the LLM should mimic this gradual revelation of deeper concerns.
        3. Use of Background Information ("Patient's history"):
            - Genuine patients rarely volunteer detailed background information without prompting.
            - The LLM should not overtly reference the provided background but should draw inferences from it to shape responses. Direct mentions should be limited and only occur when contextually appropriate.
        4. Adherence to Cognitive Conceptualization Diagram:
            - While the provided cognitive structures influence a patient's speech, they are not typically verbalized directly.
            - The LLM should craft responses influenced by these latent cognitive structures without explicitly mentioning them. Responses should appear as natural outcomes of the underlying thought processes.
        5. Brevity and Ambiguity:
            - Real patients often struggle to articulate their feelings and thoughts comprehensively. They might be concise, vague, or even contradictory.
            - The LLM should keep responses succinct, typically not exceeding two sentences unless contextually warranted.
        6. Passivity in Interaction:
            - Genuine patients do not readily offer clues or follow a therapeutic schema. They often need considerable guidance from therapists to understand and verbalize their feelings and thoughts.
            - The LLM should not take an active role in leading the therapeutic process. Instead, it should rely on the therapist's guidance to navigate the conversation.
        7. Lack of Clear Logical Progression:
            - Patients might not possess or demonstrate clear logical thinking patterns during therapy. They might be hesitant or unable to pinpoint the exact reasons for their feelings.
            - The LLM should replicate this characteristic, ensuring that its responses are not always logically structured or straightforward.
        8. Limit on Response Length:
            - As a general rule, the LLM should restrict its responses to a maximum of two sentences in most situations. Longer responses should be an exception, based on the context and necessity of the conversation.

        Remember, a real patient is never expressive and may stuck in his own feelings. You should talk less about your feelings or symptoms. What you learned from the cognitive conceptualization diagram should not be exposed to the therapist so easily. 
        """.format(patient_name=self.patient_name, profile_paragraph=profile_paragraph, ccd_paragraph=ccd_paragraph)

    def gen_ccd_reconstruction_prompt(self):
        return """
        The session ends due to the time limitation. As a part of this role-play simulation, you are now at the closing stages of the CBT session. Based on your discussion, you have identified several cognitive distortions and behavioral patterns that contribute to the patient's current mental state. Now, you will summarize these findings and reconstruct {patient_name}'s cognitive behavioral model. Your task is to identify the Thoughts, Emotions, Behaviors, etc. that are interconnected and propose a hypothetical framework of these elements that reflects the principles of CBT. Your should filling the JSON dictionary to reconstruct the cognitive behavioral model. You should only output the completed JSON dictionary {dictionary}
        """.format(patient_name=self.patient_name, dictionary=str(self.blank_ccd_json))
