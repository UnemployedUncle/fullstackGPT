import json
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
import streamlit as st
from langchain.retrievers import WikipediaRetriever
from langchain.schema import BaseOutputParser, output_parser


class JsonOutputParser(BaseOutputParser):
    def parse(self, text):
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)

output_parser = JsonOutputParser()

st.set_page_config(
    page_title="QuizGPT",
    page_icon="❓",
)

st.title("QuizGPT")

@st.cache_data(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = f"./.cache/quiz_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    return docs

@st.cache_data(show_spinner="Searching Wikipedia...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    docs = retriever.get_relevant_documents(term)
    return docs

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key")

with st.sidebar:
    level = None
    choice = st.selectbox(
        "Choose the level of the quiz.",
        (
            "Hard",
            "Easy",
        ),
    )
    if choice == "Hard":
        level = "hard"
    else:
        level = "easy"

with st.sidebar:
    docs = None
    topic = None
    choice = st.selectbox(
        "Choose what you want to use.",
        (
            "File",
            "Wikipedia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file)
    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            docs = wiki_search(topic)

@st.cache_data(show_spinner="Making quiz...")
def run_quiz_chain(level, _docs, topic):
    # chain = {"context": questions_chain} | formatting_chain | output_parser
    chain = questions_prompt | question_llm
    return chain.invoke({"level": level, "context": format_docs(_docs)})
# .additional_kwargs["function_call"]["arguments"]

function = {
    "name": "create_quiz",
    "description": "function that takes a list of questions and answers and returns a quiz",
    "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                        },
                        "answers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "answer": {
                                        "type": "string",
                                    },
                                    "correct": {
                                        "type": "boolean",
                                    },
                                },
                                "required": ["answer", "correct"],
                            },
                        },
                    },
                    "required": ["question", "answers"],
                },
            }
        },
        "required": ["questions"],
    },
}

question_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-3.5-turbo-1106",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    openai_api_key = openai_api_key
).bind(
    function_call={
        "name": "create_quiz",
    },
    functions=[
        function,
    ],
)

# llm = ChatOpenAI(
#     temperature=0.1,
#     model="gpt-3.5-turbo-1106",
#     streaming=True,
#     callbacks=[StreamingStdOutCallbackHandler()],
#     openai_api_key = openai_api_key
# )

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

#%%

# def get_weather(lon, lat):
#     print("Call an api...")

# schema = {
#     "name": "get_weather",
#     "description": "function that takes a longitude and latitude to find the weather of a place",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "lon": {"type": "string", "description": "longitude of the place"},
#             "lat": {"type": "string", "description": "latitude of the place"},
#         },
#     }
#     "required": ["lon", "lat"],
# }

# llm = ChatOpenAI(
#     temperature=0.1,
# ).bind(
#     function_call={
#         "name": "create_quiz",
#     },
#     functions=[
#         function,
#     ],
# )

# prompt = PromptTemplate.from_template("Make a quiz about {city}")
# chain = prompt | llm
# response = chain.invoke({"city": "rome"})
# response = response.additional_kwargs["function_call"]["arguments"]
# response


#%%

questions_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 10 (TEN) {level} questions to test the user's knowledge about the text.
         
    Your turn!
         
    Context: {context}
""",
        )
    ]
)

# questions_chain = {"context": format_docs, "level": level} | questions_prompt | question_llm

# prompt = PromptTemplate.from_template("Make a quiz about {city}")
# questions_chain = prompt | llm
# response = chain.invoke({"city": "rome"})
# response = response.additional_kwargs["function_call"]["arguments"]
# response

# formatting_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             """
#     You are a powerful formatting algorithm.
     
#     You format exam questions into JSON format.
#     Answers with (o) are the correct ones.
     
#     Example Input:

#     Question: What is the color of the ocean?
#     Answers: Red|Yellow|Green|Blue(o)
         
#     Question: What is the capital or Georgia?
#     Answers: Baku|Tbilisi(o)|Manila|Beirut
         
#     Question: When was Avatar released?
#     Answers: 2007|2001|2009(o)|1998
         
#     Question: Who was Julius Caesar?
#     Answers: A Roman Emperor(o)|Painter|Actor|Model
    
     
#     Example Output:
     
#     ```json
#     {{ "questions": [
#             {{
#                 "question": "What is the color of the ocean?",
#                 "answers": [
#                         {{
#                             "answer": "Red",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Yellow",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Green",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Blue",
#                             "correct": true
#                         }}
#                 ]
#             }},
#                         {{
#                 "question": "What is the capital or Georgia?",
#                 "answers": [
#                         {{
#                             "answer": "Baku",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Tbilisi",
#                             "correct": true
#                         }},
#                         {{
#                             "answer": "Manila",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Beirut",
#                             "correct": false
#                         }}
#                 ]
#             }},
#                         {{
#                 "question": "When was Avatar released?",
#                 "answers": [
#                         {{
#                             "answer": "2007",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "2001",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "2009",
#                             "correct": true
#                         }},
#                         {{
#                             "answer": "1998",
#                             "correct": false
#                         }}
#                 ]
#             }},
#             {{
#                 "question": "Who was Julius Caesar?",
#                 "answers": [
#                         {{
#                             "answer": "A Roman Emperor",
#                             "correct": true
#                         }},
#                         {{
#                             "answer": "Painter",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Actor",
#                             "correct": false
#                         }},
#                         {{
#                             "answer": "Model",
#                             "correct": false
#                         }}
#                 ]
#             }}
#         ]
#      }}
#     ```
#     Your turn!

#     Questions: {context}

# """,
#         )
#     ]
# )

# formatting_chain = formatting_prompt | llm


if not docs:
    st.markdown(
        """
    Welcome to QuizGPT.
                
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
                
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    response = run_quiz_chain(level, docs, topic if topic else file.name)
    st.write(response)
    # response = run_quiz_chain(level, docs, topic if topic else file.name)
    # with st.form("questions_form"):
    #     for question in response["questions"]:
    #         st.write(question["question"])
    #         value = st.radio(
    #             "Select an option.",
    #             [answer["answer"] for answer in question["answers"]],
    #             index=None,
    #         )
    #         if {"answer": value, "correct": True} in question["answers"]:
    #             st.success("Correct!")
    #         elif value is not None:
    #             st.error("Wrong!")
    #     button = st.form_submit_button("Submit Answers")
