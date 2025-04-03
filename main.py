# main.py
import getpass
import json
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

console = Console()
inca_icon = ":crystal_ball:"
user_icon = ":blond-haired_person:"


def langchain_flow():
    from langchain_flow import generate_response, is_collecting, thanks, check_order_status, save_history

    console.print(inca_icon, generate_response("Hi"))

    exiting = False

    while is_collecting():
        user_input = Prompt.ask(user_icon)
        if user_input.lower() in ["exit", "quit"]:
            exiting = True
            break
        response = generate_response(user_input)
        console.print(inca_icon, response)

    if not exiting:
        # try to check order status
        console.print(inca_icon, check_order_status())
        console.print(inca_icon, thanks())

    save_history()


def smolagents_flow():
    from smolagents_flow import incaAgent
    history = []
    console.print(
        "Type 'summary' or 'history' to see the conversation history.\n")
    console.print(inca_icon, incaAgent.run(
        "Ask my name and tell me what you can do omitting the greet tool."))
    while True:

        user_input = Prompt.ask(user_icon)
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input.lower() in ["history", "summary"]:
            print(json.dumps(history, indent=4))
        response = incaAgent.run(user_input)
        console.print(inca_icon, response)
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


def main():
    load_dotenv()  # Load environment variables from .env file
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = getpass.getpass(
            'Provide your Gemini API Key: ')

    console.rule("[bold red]-")
    console.print(
        "[bold pink]INCA[/bold pink]!", inca_icon, justify="center")
    console.print(
        "Type 'exit' or 'quit' to end the conversation.", justify="center")
    console.rule("[bold red]-")
    console.print()

    langchain_flow()


if __name__ == "__main__":
    main()
