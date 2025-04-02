# main.py
import getpass
import json
import os
from dotenv import load_dotenv


def try_langchain():
    from langchain_solution import generate_response, state_machine
    print("Starting the INCA with LangChain...")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while state_machine.state != "FINISHED":
        user_input = input("Customer: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = generate_response(user_input)
        print("Agent:", response)


def try_smolagents():
    from smolagents_solution import incaAgent
    history = []
    print("Starting the INCA with smolagents...")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    print("Type 'summary' or 'history' to see the conversation history.\n")
    print("INCA:", incaAgent.run(
        "Ask my name and tell me what you can do omitting the greet tool."))
    while True:

        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input.lower() in ["history", "summary"]:
            print(json.dumps(history, indent=4))
        response = incaAgent.run(user_input)
        print("INCA:", response)
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


def main():
    load_dotenv()  # Load environment variables from .env file
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = getpass.getpass(
            'Provide your Gemini API Key: ')

    try_langchain()


if __name__ == "__main__":
    main()
