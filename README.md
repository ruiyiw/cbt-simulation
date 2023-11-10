# cbt-simulation
## Usage
To generate patient profiles and cognitive conceptualization diagrams, run the following command:
```bash
cd scripts
python generate_profile_ccd.py --session_data_dir ../data/therapy_session_data/CBT_therapy-data.json
```
To play around with the prompts, you can modify `scripts/utils/prompt_template.py`
## Stage 1: Simulating patients via prompt engineering
Step 1. Generate patient profiles based on psychotherapy session transcripts
Step 2. Generate cognitive conceptualization diagrams of patients
Step 3. Design prompts to enable LLMs to simulate patients
Step 4. Build a chat interface that allows participants to communicate with prompted models
Step 5. Compare participants' summaries of cognitive conceptualization diagrams with ground-truth diagrams