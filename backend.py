
from fastapi import FastAPI, Request, HTTPException
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load the Sentence Transformer model for embeddings
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# Function to read text from PDF
def load_pdf_text(file_path):
    pdfreader = PdfReader(file_path)
    raw_text = ''
    for i, page in enumerate(pdfreader.pages):
        content = page.extract_text()
        if content:
            raw_text += content
    return raw_text

# Function to split the text into chunks
def split_text(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_text(raw_text)

# Function to find the most relevant passage based on the query
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

# Preload the PDF text and split it into chunks
pdf_path = 'pb.pdf'  # Path to PDF file
raw_text = load_pdf_text(pdf_path)
text_chunks = split_text(raw_text)

@app.post("/find_relevant_passage/")
async def find_relevant_passage(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    # Find the most relevant passage
    most_similar_passage, similarity_score = find_most_similar_passage(query, text_chunks)

    return {
        "most_relevant_passage": most_similar_passage,
        "similarity_score": similarity_score
    }
