### Setup instructions
* Clone the repo to a folder, example inca
* Inside inca folder create a venv and activate
    ```
    python -m venv .venv
    source source .venv/bin/activate
    ```
* Install dependencies inside the venv
    ```
    python -m pip install -r requirements.txt
    # or just
    pip install -r requirements.txt
    ```
* Copy env.example as .env and enter your tokens, currently only uses GEMINI_API_KEY
* Run the app
    ```
    python main.py
    ```

* (Optional) Or run with Docker
    ```
     docker build -t inca:latest -f ./Dockerfile ./
     docker run -it --name inca  -e GEMINI_API_KEY=<TOKEN> inca:latest
    ```

### System Architecture & Design

It's a basic console app without additional services. I've tried to keep it simple without using Milvus or Faiss for keeping vector store. I've used langchain for parsing the messages and extracting the data using PydanticOutputParser (langchain_solution.py). 

I've also tried another scenario using only smolagents (smolagent_solution_.py) but even it's promising it needs work.
I've later added a RAG example using smolagent custom tool to simulate getting data from a data store, it decides which tool to use.

I've used a state machine to decide if the agent had the required information or not, until correct data is received the agent keeps askind order number and problem details.

After receiving these inputs it calls the RAG agent to check order status using another prompt.

Finally the conversation history is dumped to a file.

conversation_history folder has some examples.

### Potential Improvements

Currently all data is kept for a single run and the agent exits, I could have setup another persistent storage, keep session information and provide more details for the user.

Could add a simple UI using streamlit or niceui