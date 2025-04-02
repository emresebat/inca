from enum import Enum, auto
import os
import re
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from prompts import initial_prompt_template


class SupportInfo(BaseModel):
    raw_response: Optional[str] = None
    order_number: Optional[str] = None
    problem_category: Optional[str] = None


class ConversationState(Enum):
    COLLECTING_ORDER_NUMBER = auto()
    COLLECTING_PROBLEM_CATEGORY = auto()
    FINISHED = auto()


class SupportStateMachine:
    def __init__(self):
        self.state = ConversationState.COLLECTING_ORDER_NUMBER
        self.support_info = SupportInfo()

    def validate_order_number(self, input: str) -> str:
        """
        Extracts a 6-digit order number from the provided text.
        Adjust the regex if your order number format differs.
        """
        if not input:
            return None
        match = re.search(r'\b\d{6}\b', input)
        return match.group(0) if match else None

    def update_state(self, parsed_support_info: SupportInfo) -> str:
        """
        Updates the state machine based on user input.
        Returns an appropriate response prompt.
        """
        self.support_info = parsed_support_info
        if self.state == ConversationState.COLLECTING_ORDER_NUMBER:
            order = self.validate_order_number(
                parsed_support_info.order_number)
            if order:
                self.state = ConversationState.COLLECTING_PROBLEM_CATEGORY

        elif self.state == ConversationState.COLLECTING_PROBLEM_CATEGORY:
            # Here we simply assume that any non-empty input is the problem category.
            if parsed_support_info.problem_category is not None and parsed_support_info.problem_category.strip():
                self.problem_category = parsed_support_info.problem_category.strip()
                self.state = ConversationState.FINISHED



# Create an output parser that expects the above JSON structure.
parser = PydanticOutputParser(pydantic_object=SupportInfo)

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=initial_prompt_template,
)

# Set up conversation memory to maintain context
memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True
)

# Setup with system message conversion
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',  api_key=os.environ["GEMINI_API_KEY"])

state_machine = SupportStateMachine()


def generate_response(user_input: str) -> str:
    # Create a prompt that instructs the LLM to output a JSON with orderNumber and problemCategory

    # Load conversation history from memory
    memory_vars = memory.load_memory_variables({})
    # Prepare input for prompt
    chain_input = {"history": memory_vars.get(
        "history", ""), "input": user_input}
    # Compose the chain using the RunnableSequence syntax
    chain = prompt | llm

    # Invoke the chain with the prompt
    raw_response = chain.invoke(chain_input)

    # Save the conversation context
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
        # Now you have access to support_info.orderNumber and support_info.problemCategory
        # You can use these values as needed in your code.
        state_machine.update_state(support_info)
        return support_info.raw_response
    except Exception as e:
        return raw_response_text


# def generate_response(user_input: str) -> str:
#     """
#     Generates a response from the agent based on user input using LangChain.
#     """
#     # Prepare input for prompt
#     chain_input = [SystemMessage(
#         name="Customer Support Role",
#         content="You are a customer support agent. Your goal is to help the customer by gathering the necessary informationby getting the {orderNumber} and {problemCategory} "),
#         HumanMessage(content=user_input)]
#     # Get the response from the chain
#     response = llm.invoke(chain_input)
#     return response
