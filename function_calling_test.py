import openai
import requests
import json
import os

# this model will detect when a function needs to be called, depending on the input
# the model will respond with JSON, matching what the function expects as parameters
# the model does not execute the call, they provide a structured output that your program can utilise to 
# initiate the function call

# THREE STEPS
# 1. call chat completion API with your question
# 2. use the model's response to call your API or function
# 3. call chat completion again, including the response from function or API for the final answer

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")

# the initial question from a user
messages= [
    {"role": "user", "content": "Find beachfront hotels in San Diego for less than $300 a month with free breakfast."}
]

# a function has three main parameters: name, description, and parameters
# name is used to call the function
# description is used by the model to determine when and how to call the function
# parameters is JSON that describes the parameter the functions accepts
functions= [  
    {
        "name": "search_hotels",
        "description": "Retrieves hotels from the search index based on the parameters provided",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location of the hotel (i.e. Seattle, WA)"
                },
                "max_price": {
                    "type": "number",
                    "description": "The maximum price for the hotel"
                },
                "features": {
                    "type": "string",
                    "description": "A comma separated list of features (i.e. beachfront, free wifi, etc.)"
                }
            },
            "required": ["location"],
        },
    }
]  

response = openai.ChatCompletion.create(
    engine="GPT-4",
    messages=messages,
    functions=functions,
    function_call="auto", 
)

print(response['choices'][0]['message'])