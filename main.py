import streamlit as st
import google.generativeai as genai
import os
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import gc

# Configure the model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the Sentence Transformer model for embeddings
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# STEP 1: Read text from PDF with memory optimization
def load_pdf_text(file_path, max_pages=5):
    pdfreader = PdfReader(file_path)
    raw_text = ''
    for i, page in enumerate(pdfreader.pages[:max_pages]):  # Limit to max_pages
        content = page.extract_text()
        if content:
            raw_text += content
    return raw_text

# Load and split the text with optimized chunk size
def split_text(raw_text, chunk_size=1000, chunk_overlap=200):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
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

    # Free memory after use
    del passage_embeddings
    gc.collect()

    # Find the most similar passage
    most_similar_index = np.argmax(similarities)
    most_similar_passage = text_chunks[most_similar_index]
    
    return most_similar_passage, similarities[most_similar_index]

# Function to generate response
def generate_response(user_input, most_relevant_passage, context=" " ):
    full_prompt = f"""
        You are a versatile AI assistant with a dual purpose:
        1. **Conversational Mode**: Engage in polite and helpful responses to general questions and casual exchanges.
        2. **Debate Mode**: If the user’s prompt is argumentative or contains debating cues, respond competitively, defending a stance with well-reasoned points and relevant references to provided context.

        ### Guidelines:
        - **For General or Casual Inputs**: Respond simply and directly, keeping your answer polite and helpful.
        - **For Debate or Argumentative Inputs**: Present a clear stance and logical argumentation, avoiding neutral or vague statements.

        ### Contextual Information:
        Use the following passage for any supporting information in your response if relevant: {most_relevant_passage}

        ### Prior Response (if any): {context}

        User: {user_input}
        Assistant:
    """
    response = model.generate_content(full_prompt)
    return response.text, response.usage_metadata

# Streamlit interface
def main():
    st.title("Debate Bot with Document Retrieval")
    st.write("Engage in a debate with the bot on a wide range of topics! The bot can also reference information from the uploaded document.")

    # Load document text with a maximum of 5 pages
    pdf_path = 'pb.pdf'
    raw_text = load_pdf_text(pdf_path, max_pages=5)  # Limit to 5 pages
    text_chunks = split_text(raw_text, chunk_size=1000, chunk_overlap=200)  # Use larger chunk size

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

            # Free memory after each response
            gc.collect()

main()
