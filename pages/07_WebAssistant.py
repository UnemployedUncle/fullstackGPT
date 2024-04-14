import json
import streamlit as st
import openai as client
import os

from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(
    page_title="WebAssistant",
    page_icon="🤖",
)

st.title("WebAssistant")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key")
    os.environ["OPENAI_API_KEY"] = openai_api_key
    # assistant_id = st.text_input("assistant_id")

# Given the query(search term) find it on Wikipedia
def wiki_search(inputs):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    query = inputs["query"]
    return wikipedia.run(query)

# Given the query(search term) find it on Duckduckgo and return the url of it
# def duckduckgo_search(inputs):
#     ddg = DuckDuckGoSearchAPIWrapper()
#     query = inputs["query"]
#     return ddg.run(f"Tell me information of {query}")
def duckduckgo_search(inputs):
    ddg = DuckDuckGoSearchAPIWrapper()
    query = inputs["query"]
    results = ddg.results(f"{query}", max_results=1)
    # print(results)
    url = results[0]['link']
    # print(url)
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    f = open('homework14.txt','w', encoding='utf-8')
    f.write(str(r.content))
    f.close()
    return url

functions_map = {
    "wiki_search": wiki_search,
    "duckduckgo_search": duckduckgo_search,
}

functions = [
    {
        "type": "function",
        "function": {
            "name": "wiki_search",
            "description": "Given the query, search it on Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query of the search term",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_search",
            "description": "Given the query, search it on Duckduckgo and save the file",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query of the search term",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

#%%
def get_run(run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )


def send_message(thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=content
    )


def get_messages(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()
    for message in messages:
        print(f"{message.role}: {message.content[0].text.value}")
        for annotation in message.content[0].text.annotations:
            print(f"Source: {annotation.file_citation}")


def get_tool_outputs(run_id, thread_id):
    run = get_run(run_id, thread_id)
    outputs = []
    for action in run.required_action.submit_tool_outputs.tool_calls:
        action_id = action.id
        function = action.function
        print(f"Calling function: {function.name} with arg {function.arguments}")
        outputs.append(
            {
                "output": functions_map[function.name](json.loads(function.arguments)),
                "tool_call_id": action_id,
            }
        )
    return outputs


def submit_tool_outputs(run_id, thread_id):
    outpus = get_tool_outputs(run_id, thread_id)
    return client.beta.threads.runs.submit_tool_outputs(
        run_id=run_id,
        thread_id=thread_id,
        tool_outputs=outpus,
    )

#%%
import openai as client
assistant = client.beta.assistants.create(
    name="WebAssistant",
    instructions="You will find information on the web(Wiki, DuckDuckGo) for the users and return the contents of it.",
    model="gpt-4-1106-preview",
    tools=functions,
)
# assistant_id = assistant.id
# st.write(assistant)

def start_thread(message):
    thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": message,
        }
    ]
    )
    return thread

def run_thread(thread, assistant):
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    )
    return run

#%%
def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)

def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )

st.session_state["messages"] = []

import time

send_message("I'm ready! Ask away!", "ai")
paint_history()
message = st.chat_input("Ask anything...")
thread = start_thread(message)
run = run_thread(thread, assistant)

if message:
    send_message(message, "human")
    while get_run(run.id, thread.id).status == 'requires_action' or get_run(run.id, thread.id).status == 'completed':
        time.sleep(1)
        if get_run(run.id, thread.id).status == 'requires_action':
            submit_tool_outputs(run.id, thread.id)
            run = run_thread(thread, assistant)
        else:
            st.write(get_messages(thread.id))
