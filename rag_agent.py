import os
from smolagents import Tool, HfApiModel, ToolCallingAgent, LiteLLMModel, OpenAIServerModel

class OrderStatusCheckTool(Tool):
    name = "order_status_check"
    description = "A tool to check an order status."
    inputs = {
        "order_number": {
            "type": "string",
            "description": "The order number ",
        },
    }
    output_type = "string"

    def forward(self, order_number,):
        # Simulate a distance calculation
        orders = {
            ("O123456"): "Delivered",
            ("O654321"): "On Distribution",
            ("O125634"): "Delayed on processing"
        }
        return {"status": orders.get((order_number), None)}


model = OpenAIServerModel(
    model_id="gemini-2.0-flash-exp",
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.7
)
incaAgent = ToolCallingAgent(
    tools=[OrderStatusCheckTool()], model=model)
