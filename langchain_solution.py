from datetime import datetime
from enum import Enum, auto
import json
import os
import re
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
# from langchain.schema import messages_to_dictm, messages_from_dict
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from textblob import TextBlob
from prompts import greeting_prompt, user_prompt_template, thanks_prompt_template


class SupportInfo(BaseModel):
    message: Optional[str] = None
    order_number: Optional[str] = None
    problem_category: Optional[str] = None


class ConversationState(Enum):
    COLLECTING = auto()
    COLLECTED = auto()


class SupportStateMachine:
    def __init__(self):
        self.state = ConversationState.COLLECTING
        self.support_info = SupportInfo()

    def validate_order_number(self, input: str) -> bool:
        """
        Extracts a 7 char order number from the provided text.
        Adjust the regex if your order number format differs.
        """
        if not input:
            return False
        match = re.search(r'\bO\d{6}\b', input)
        return match.group(0) != None

    def validate_problem_category(self, input: str) -> bool:
        """
        Just check if the input is not empty.
        """
        invalid_values = ["none", "null", "n/a", "", "problem", "issue"]
        return input is not None and input.strip().lower() not in invalid_values

    def update_state(self, parsed_support_info: SupportInfo) -> str:
        """
        Updates the state machine based on user input.
        Returns an appropriate response prompt.
        """
        self.support_info = parsed_support_info
        if self.state == ConversationState.COLLECTING:
            # Check if both data is collected
            if self.validate_order_number(parsed_support_info.order_number) and self.validate_problem_category(parsed_support_info.problem_category):
                self.state = ConversationState.COLLECTED


# Create an output parser that expects the above JSON structure.
parser = PydanticOutputParser(pydantic_object=SupportInfo)

input_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=user_prompt_template,
)

thanks_prompt = PromptTemplate(
    input_variables=["history"],
    template=thanks_prompt_template,
)

# Set up conversation memory to maintain context
memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True
)

# Extra dict array to store the conversation history
structured_history = []


def append_history(role: str, input: str, response: str, error: Optional[str] = None):
    """
    Appends the conversation history to the structured history.
    """
    structured_history.append({
        "role": role,
        "input": input,
        "output": response,
        "orderNumber": state_machine.support_info.order_number,
        "problemCategory": state_machine.support_info.problem_category,
        "error": error
    })


# Setup with system message conversion
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',  api_key=os.environ["GEMINI_API_KEY"])

state_machine = SupportStateMachine()


def greet() -> str:
    """
    Greets the user
    """
    # Prepare input for prompt
    chain_input = [SystemMessage(
        name="Customer Support Role",
        content=greeting_prompt),
        HumanMessage(content="Hi")]
    # Get the response from the chain
    response = llm.invoke(chain_input)

    memory.save_context({"input": ""}, {"output": response.content})

    append_history("ai", greeting_prompt, response.content)

    return response.content


def generate_response(user_input: str) -> str:
    # Create a prompt that instructs the LLM to output a JSON with orderNumber and problemCategory

    # Load conversation history from memory
    memory_vars = memory.load_memory_variables({})
    # Prepare input for prompt
    chain_input = {"history": memory_vars.get(
        "history", ""), "input": user_input}
    # Compose the chain using the RunnableSequence syntax
    chain = input_prompt | llm

    # Invoke the chain with the prompt
    raw_response = chain.invoke(chain_input)

    memory.save_context({"input": user_input}, {
                        "output": raw_response.content})

    # Ensure we extract the text from the AIMessage (if that's what is returned)
    if hasattr(raw_response, "content"):
        raw_response_text = raw_response.content
    else:
        raw_response_text = str(raw_response)

    # Parse the LLM response using the parser
    try:
        support_info = parser.parse(raw_response_text)
        # Now we have access to support_info.orderNumber and support_info.problemCategory
        state_machine.update_state(support_info)
        # Save the conversation context
        append_history("user", user_input, raw_response_text)
        return support_info.message
    except Exception as e:
        append_history("user", user_input, raw_response_text, error=str(e))
        return raw_response_text


def thanks() -> str:

    # Load conversation history from memory
    memory_vars = memory.load_memory_variables({})
    # Prepare input for prompt
    chain_input = {"history": memory_vars.get(
        "history", ""), "order_number": state_machine.support_info.order_number, "problem_category": state_machine.support_info.problem_category}
    # Compose the chain using the RunnableSequence syntax
    chain = thanks_prompt | llm

    # Invoke the chain with the prompt
    raw_response = chain.invoke(chain_input)

    # Save the conversation context
    memory.save_context({"input": "None"}, {
                        "output": raw_response.content})

    append_history("ai", thanks_prompt_template, raw_response.content)

    return raw_response.content


def dump_conversation_history_to_json_file():
    """
    Dumps the conversation history to a JSON file.
    """
    # Load conversation history from memory
    # memory_vars = memory.load_memory_variables({})
    # Get the conversation history
    # chat_history = memory_vars.get("history", [])

    # Retrieve the full conversation history as a single string
    conversation_text = "\n".join([hist['input']
                                  for hist in structured_history])

    blob = TextBlob(conversation_text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    detailed_summary = {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "conversation_history": structured_history
    }

    # # Convert the chat history to a structured format
    # structured_history = messages_to_dict(chat_history)

    # Save to a JSON file
    # Ensure the directory exists
    os.makedirs(".conversation_history", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f".conversation_history/{timestamp}.json", "w") as f:
        json.dump(detailed_summary, f, indent=4)
