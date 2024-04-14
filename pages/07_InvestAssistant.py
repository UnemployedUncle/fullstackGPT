import json
import streamlit as st

st.set_page_config(
    page_title="InvestAssistant",
    page_icon="🤖",
)

st.title("InvestAssistant")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key")

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

send_message("I'm ready! Ask away!", "ai", save=False)
paint_history()

# message = st.chat_input("Ask anything about your file...")
# if message:
#     send_message(message, "human")
#     with st.chat_message("ai"):
#         chain.invoke(message)

# st.session_state["messages"] = []