import streamlit as st
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from langchain.document_loaders import *
import tempfile
from langchain.docstore.document import Document
import dotenv

dotenv.load_dotenv()

st.title("Basic Chatbot")

# Initialize state variables
user_queries = st.text_input("Enter your queries")
external_tool_query = st.text_input("Enter the external tool query")
file_path = st.session_state.get('file_path', None)
uploaded_file_string = ""


# Function to generate responses to user queries
def query_responder(user_queries):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        temperature=0.7
    )
    system_template = """You are an AI assistant trained to respond to user queries.
    Please provide a response to the following user query: '{user_query}'."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = """Please provide a response to the following user query: '{user_query}'."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(user_query=user_queries)
    return result


# Function to load external content from URL or file path
def load_external_content(argument):
    if argument.startswith("http"):
        from langchain.document_loaders import WebBaseLoader
        loader = WebBaseLoader(argument)
    else:
        from langchain.document_loaders import TextLoader
        loader = TextLoader(argument)
    docs = loader.load()
    return docs


# Function to load uploaded file as a document
def load_uploaded_file(file_path):
    if file_path.endswith(".txt"):
        from langchain.document_loaders import TextLoader
        loader = TextLoader(file_path)
    elif file_path.endswith(".pdf"):
        from langchain.document_loaders import UnstructuredPDFLoader
        loader = UnstructuredPDFLoader(file_path, mode="elements", strategy="fast")
    elif file_path.endswith(".pptx"):
        from langchain.document_loaders import UnstructuredPowerPointLoader
        loader = UnstructuredPowerPointLoader(file_path, mode="elements", strategy="fast")
    elif file_path.endswith(".csv"):
        from langchain.document_loaders.csv_loader import UnstructuredCSVLoader
        loader = UnstructuredCSVLoader(file_path, mode="elements")
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        from langchain.document_loaders.excel import UnstructuredExcelLoader
        loader = UnstructuredExcelLoader(file_path, mode="elements")
    else:
        from langchain.document_loaders import WebBaseLoader
        loader = WebBaseLoader(file_path)

    docs = loader.load()
    return docs


# Function to generate responses to external tool query or uploaded file
def response_generator(external_content_string, uploaded_file_string):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    system_template = """You are an assistant that can generate responses to queries or analyze uploaded files."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = """Please provide a response or analysis for the following content: {external_content_string} {uploaded_file_string}."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(external_content_string=external_content_string, uploaded_file_string=uploaded_file_string)
    return result


# ----- Main App -----

if file_path is None:
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            file_path = temp_file.name
            st.session_state['file_path'] = file_path
else:
    st.write("File path already provided:", file_path)

if file_path:
    uploaded_file_string = "".join([doc.page_content for doc in load_uploaded_file(file_path)])

# Button to trigger functionality
if st.button("Generate Responses"):
    if user_queries:
        responses = query_responder(user_queries)
    else:
        responses = ""

    if external_tool_query:
        external_content = load_external_content(external_tool_query)
        external_content_string = "".join([doc.page_content for doc in external_content])
    else:
        external_content_string = ""

    if external_content_string and uploaded_file_string:
        responses_external_tool_or_file = response_generator(external_content_string, uploaded_file_string)
    else:
        responses_external_tool_or_file = ""

    st.markdown(responses_external_tool_or_file)
    st.markdown(responses)
