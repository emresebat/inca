import os
from smolagents import Tool,  ToolCallingAgent,  OpenAIServerModel


class DistanceCalculatorTool(Tool):
    name = "distance_calculator"
    description = "A tool to calculate the distance between two locations."
    inputs = {
        "location1": {
            "type": "string",
            "description": "The first location.",
        },
        "location2": {
            "type": "string",
            "description": "The second location.",
        },
    }
    output_type = "string"

    def forward(self, location1, location2):
        # Simulate a distance calculation
        distances = {
            ("Lima", "Cusco"): 1100,
            ("Cusco", "Machu Picchu"): 112,
            ("Lima", "Machu Picchu"): 1120,
            ("Cusco", "Arequipa"): 500,
            ("Arequipa", "Lima"): 1000,
            ("Arequipa", "Cusco"): 500,
            ("Lima", "Arequipa"): 1000,
            ("Machu Picchu", "Arequipa"): 600,
            ("Machu Picchu", "Lima"): 1120,
        }
        return {"distance": distances.get((location1, location2), "Unknown")}


class GreetTool(Tool):
    name = "greet_tool"
    description = "Greet a specific person. Requires the person's name so if needs to be asked."
    inputs = {
        "name": {
            "type": "string",
            "description": "The name of the person to greet.",
        },
    }
    output_type = "string"

    def forward(self, name):
        return {"greeting": f"Hello, {name}! How can I assist you today?"}


# model = LiteLLMModel(
#     # Can try diffrent model here I am using qwen2.5 7B model
#     model_id="ollama_chat/qwen2.5:7b",
#     api_base="http://127.0.0.1:11434",
#     num_ctx=8192,
# )

# model = HfApiModel()

model = OpenAIServerModel(
    model_id="gemini-2.0-flash-exp",
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.7
)
incaAgent = ToolCallingAgent(
    tools=[DistanceCalculatorTool(), GreetTool()], model=model)
