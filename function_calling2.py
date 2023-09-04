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
    {"role": "user", "content": "Find the current price of ethereum in Euros"}
]

# need a function to interact with our database or API
def bitcoin_price(name, currency):
    response = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}")
    data = response.json()
    for crypto in data:
        if crypto['id'] == name:
            current_price = crypto["current_price"]
            return f"{name} is currently worth {current_price} {currency}"

# a function has three main parameters: name, description, and parameters
# name is used to call the function
# description is used by the model to determine when and how to call the function
# parameters is JSON that describes the parameter the functions accepts
functions= [  
    {
        "name": "bitcoin_price",
        "description": "Retrieves current price of cryptocurrency based on the parameters provided",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the cryptocurrency"
                },
                # note that we can use the description to format the parameter
                "currency": {
                    "type": "string",
                    "description": "The type of currency for defining the price of bitcoin. We can only use usd, gbp, or eur"
                }
            },
            "required": ["name", "currency"],
        },
    }
]  

response = openai.ChatCompletion.create(
    engine="GPT-4",
    messages=messages,
    functions=functions,
    function_call="auto", 
)

response_message = response["choices"][0]["message"]

# check if the model wants to call a function
if response_message.get("function_call"):

    # call the function, the JSON response may not always be valid so be sure to handle errors
    function_name = response_message["function_call"]["name"]

    available_functions = {
        "bitcoin_price": bitcoin_price,
    }
    function_to_call = available_functions[function_name]

    function_args = json.loads(response_message["function_call"]["arguments"])
    
    # ** allows you to pass keyworded variable length of arguments to a function
    function_response = function_to_call(**function_args)

    # Add the assistant response and function response to the messages
    messages.append( # adding assistant response to messages
        {
            "role": response_message["role"],
            "function_call": {
                "name": function_name,
                "arguments": response_message["function_call"]["arguments"],
            },
            "content": None
        }
    )
    messages.append( # adding function response to messages
        {
            "role": "function",
            "name": function_name,
            "content": function_response,
        }
    ) 

    second_response = openai.ChatCompletion.create(
        engine="GPT-4",
        messages=messages
    )

    # Fetch the content of the assistant's last message.
    final_message_content = second_response['choices'][0]['message']['content']


    print(final_message_content)
