import time
import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)

st.title("DocumentGPT")

#%%
# # chat_message로 대화형식으로 보여줄 수 있음
# with st.chat_message("humman"):
#     st.write("Hello")

# with st.chat_message("ai"):
#     st.write("how are you?")

# # expanded로 단계별로 보여줄 수 있음
# with st.status("Embedding file...", expanded=True) as status:
#     time.sleep(3)
#     st.write("Getting the file")
#     time.sleep(3)
#     st.write("Embedding the file")
#     time.sleep(3)
#     st.write("Caching the file")
#     status.update(label="Erorr", state="error")

# st.chat_input("Send a message to the ai")

#%%

# messages = []

# 처음 messages가 없으면 빈 리스트로 만들어줌, 이미 있으면 패스
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    # st.write(messages)
    if save: # painting할 떄는 표현하지 않게 함
        st.session_state["messages"].append({"message": message, "role": role})

# st.write(st.session_state["messages"])

# 각각의 저장된 메시지를 표현해줌
for message in st.session_state["messages"]:
    send_message(
        message["message"],
        message["role"],
        save=False,
    )

message = st.chat_input("Send a message to the ai ")

if message:
    send_message(message, "human")
    time.sleep(2)
    send_message(f"You said: {message}", "ai")

    with st.sidebar:
        st.write(st.session_state)