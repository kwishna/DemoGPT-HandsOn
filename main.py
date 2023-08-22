import os
from time import time_ns
from demogpt import DemoGPT
import dotenv

dotenv.load_dotenv()

agent = DemoGPT(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Enter 'instruction' and 'title' as per your need.
# Run this file to generate code.

instruction = """Create a chat application using GPT-3 which has the following features:
1/ It should be able to use external too to access real time internet content for the queries.
2/ Output must be formatted in markdown.
3/ user should be able to upload a text, pdf, csv file and user should be query for the output.
"""
title = "Basic Chatbot"
code = ""
for phase in agent(instruction=instruction, title=title):
    print(phase)
    if phase["done"]:
        code = phase["code"]
print(code)

with open(f"./{time_ns()}.py", "w") as f:
    f.write(code)

# run:// streamlit run generated_code.py