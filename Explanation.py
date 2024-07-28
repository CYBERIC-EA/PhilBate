import google.generativeai as genai
import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from get_embedding_function import get_embedding_function
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms.ollama import Ollama
from dotenv import load_dotenv
import os

load_dotenv()

# Configure the Gemini model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to process the PDF and extract relevant content
def process_pdf(pdf_file):
    # Read text from PDF
    pdfreader = PdfReader(pdf_file)
    raw_text = ''
    for page in pdfreader.pages:
        content = page.extract_text()
        if content:
            raw_text += content

    # Split text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)

    # Embed documents using FAISS
    embeddings = get_embedding_function()
    document_search = FAISS.from_texts(texts, embeddings)

    return document_search

# Initialize the document search with the PDF content
document_search = process_pdf("Some Debates.pdf")

# Define a function to interact with the model
def generate_response(prompt_text, context=""):
    full_prompt = f"You are a debate bot. One who likes to engage in debates or dialectics in a wide range of topics including anime debates. You apply logical reasoning, philosophical topics and considerations, logical fallacies, linguistic styles, and other techniques applicable when responding. You may also utilize context passed when answering, it isn't compulsory though. Context: {context}\n\nUser: {prompt_text}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text

# Streamlit interface
def main():
    st.title("Debate Bot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You: ", "")
    if user_input:
        # Combine chat history for context
        context = "\n".join(st.session_state.chat_history)
        
        # Get relevant content from the PDF based on the query
        docs = document_search.similarity_search(user_input)
        pdf_content = " ".join([doc.page_content for doc in docs])

        # Generate response
        response = generate_response(user_input, pdf_content)
        st.session_state.chat_history.append(f"User: {user_input}")
        st.session_state.chat_history.append(f"Assistant: {response}")

        st.text_area("Assistant:", value=response, height=200)
        user_input = ""

    st.text_area("Chat History", value="\n".join(st.session_state.chat_history), height=300)

if __name__ == "__main__":
    main()
