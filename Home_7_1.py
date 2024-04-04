import streamlit as st
# from langchain.templates import PromptTemplate

# st.write("hello")
# st.write([1, 2, 3, 4, 5])

# a = [1, 2, 3, 4, 5]
# a

# st.write({"name": "Jesse", "age": 29})
# st.write(PromptTemplate)

# p = PromptTemplate.from_template("xxx")
# st.write(p)

st.selectbox(
    "Choose your model",
    (
        "GPT-3",
        "GPT-4",
    ),
)
