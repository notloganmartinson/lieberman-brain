import os
from google import genai

client = genai.Client()

for model in client.models.list():
    if "flash" in model.name.lower():
        print(model.name)
