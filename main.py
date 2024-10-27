import streamlit as st
import google.generativeai as genai
import os
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configure the model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the Sentence Transformer model for embeddings
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# STEP 1: Read text from PDF
def load_pdf_text(file_path):
    pdfreader = PdfReader(file_path)
    raw_text = ''
    for i, page in enumerate(pdfreader.pages):
        content = page.extract_text()
        if content:
            raw_text += content
    return raw_text

# Load and split the text
def split_text(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_text(raw_text)

# Function to find the most relevant passage
def find_most_similar_passage(query, text_chunks):
    # Encode the query and the passages
    query_embedding = embedding_model.encode(query).reshape(1, -1)
    passage_embeddings = np.array(embedding_model.encode(text_chunks))

    # Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, passage_embeddings)[0]

    # Find the most similar passage
    most_similar_index = np.argmax(similarities)
    most_similar_passage = text_chunks[most_similar_index]
    
    return most_similar_passage, similarities[most_similar_index]

# Function to generate response
def generate_response(prompt_text, most_relevant_passage, context=""):
    full_prompt = f"""You are a debate bot—one who likes to engage in debates or dialectics on a wide range of topics including anime debates. You apply logical reasoning, philosophical topics and considerations, logical fallacies, linguistic styles, and other techniques applicable when responding.
You stick to your stance and present arguments instead of guiding your opponent to find the truth. You are competitive and concise, never saying anything that will lead to your loss. You will rather get a judge to adjudicate your debates.
Negate your opponent's proposition or defend your own proposition. You may use the following argument sequence to strengthen your position if it isn't applicable in this context, ignore it; {most_relevant_passage}
You can also use the context passed when answering, it isn't compulsory though. 
Context: {context}\n\nUser: {prompt_text}\nAssistant:
"""
    response = model.generate_content(full_prompt)
    return response.text, response.usage_metadata

# Streamlit interface
def main():
    st.title("Debate Bot with Document Retrieval")
    st.write("Engage in a debate with the bot on a wide range of topics! The bot can also reference information from the uploaded document.")

    # Load document text
    pdf_path = 'pb.pdf'
    raw_text = load_pdf_text(pdf_path)
    text_chunks = split_text(raw_text)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", key="input")

    if st.button("Send"):
        if user_input:
            # Find the most relevant passage
            most_similar_passage, similarity_score = find_most_similar_passage(user_input, text_chunks)
            st.write(f"Relevant context from the document (similarity: {similarity_score:.2f}):")
            st.write(most_similar_passage)

            # Use chat history as context, and the most relevant passage in the prompt
            context = "\n".join(st.session_state.chat_history)
            response, usage_metadata = generate_response(user_input, most_similar_passage, context)
            
            # Update chat history
            st.session_state.chat_history.append(f"User: {user_input}")
            st.session_state.chat_history.append(f"Assistant: {response}")

            # Display chat history
            for i in range(len(st.session_state.chat_history)):
                if "User:" in st.session_state.chat_history[i]:
                    st.markdown(f"**{st.session_state.chat_history[i]}**")
                else:
                    st.markdown(f"{st.session_state.chat_history[i]}")

            # Optionally display token usage information
            # st.write("Usage Metadata:", usage_metadata)

main()
