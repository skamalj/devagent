import json
from tools import tool_list

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
import os


model = ChatOpenAI(model=os.getenv("MODEL_NAME"), temperature=0)
tools = tool_list
tool_node = ToolNode(tools=tools)
model_with_tools  = model.bind_tools(tools)

    
def should_continue(state: MessagesState) -> str:
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        return END
    return 'tools'

# Function to call the supervisor model
def call_model(state: MessagesState): 
    with open("agent_prompt.txt", "r", encoding="utf-8") as file:
        system_message = file.read()
        messages = state["messages"]
        system_msg = SystemMessage(content=system_message)

        if isinstance(messages[0], SystemMessage):
            messages[0]=system_msg
        else:
            messages.insert(0, system_msg)
            
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

def init_graph():
        graph = StateGraph(MessagesState)
        graph.add_node("agent", call_model)
        graph.add_node("tools", tool_node)

        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", should_continue, ["tools", END])
        graph.add_edge("tools", "agent")
        app = graph.compile()
        return app

app = init_graph()

def lambda_handler(event, context):

    messages = []
    for record in event["Records"]:
        body = json.loads(record["body"])  # SQS message body
                
        print(f"Message recieved from supervisor:  {body}")
        input_message = {
            "messages": [
                ("human", f"Story ID recieved from supervisor:  {body}"),
            ]
        }
        response = app.invoke(input_message)
        print(response)
        return





