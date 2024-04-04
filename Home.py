import streamlit as st

# st.title("Hello world!")
# st.sidebar.title("FullstackGPT")
# st.sidebar.text_input("What is your name?")

# # pattern that streamlit use
# with st.sidebar:
#     st.title("Hello world!")
#     st.sidebar.title("FullstackGPT")

# tab_one, tab_two, tab_three = st.tabs(["A", "B", "C"])

# with tab_one:
#     st.write("A")

# with tab_two:
#     st.write("A")

# with tab_three:
#     st.write("A")

# # page tab 부분에 이모지 추가
# st.set_page_config(
#     page_title="FullstackGPT Home",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# st.title("FullstackGPT Home")

# st.set_page_config(
#     page_title="FullstackGPT Home",
#     page_icon="🤖",
# )

st.markdown(
    """
# Hello!
            
Welcome to my FullstackGPT Portfolio!
            
Here are the apps I made:
            
- [ ] [DocumentGPT](/DocumentGPT)
- [ ] [PrivateGPT](/PrivateGPT)
- [ ] [QuizGPT](/QuizGPT)
- [ ] [SiteGPT](/SiteGPT)
- [ ] [MeetingGPT](/MeetingGPT)
- [ ] [InvestorGPT](/InvestorGPT)
"""
)