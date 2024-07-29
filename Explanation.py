import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Gemini model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the SentenceTransformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

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

    # Embed documents using SentenceTransformer
    embeddings = embedding_model.encode(texts, convert_to_tensor=False)
    
    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, texts

# Initialize the document search with the PDF content
pdf_file = "Some Debates.pdf"
document_index, texts = process_pdf(pdf_file)

# Function to search for similar documents
def similarity_search(query, index, texts, k=5):
    query_embedding = embedding_model.encode([query], convert_to_tensor=False)
    distances, indices = index.search(query_embedding, k)
    results = [texts[i] for i in indices[0]]
    return results

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
        docs = similarity_search(user_input, document_index, texts)
        pdf_content = " ".join(docs)

        # Generate response
        response = generate_response(user_input, pdf_content)
        st.session_state.chat_history.append(f"User: {user_input}")
        st.session_state.chat_history.append(f"Assistant: {response}")

        st.text_area("Assistant:", value=response, height=200)
        user_input = ""

    st.text_area("Chat History", value="\n".join(st.session_state.chat_history), height=300)

if __name__ == "__main__":
    main()
