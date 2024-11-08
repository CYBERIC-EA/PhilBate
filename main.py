from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os

# Initialize FastAPI app
app = FastAPI()

# Configure the model with your Gemini API key
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Pydantic model for request body
class DebateRequest(BaseModel):
    user_input: str
    recent_history: list[str] = []

# Function to generate response with competitive debate prompt
def generate_response(user_input, recent_history):
    prompt = f"""
    You are a highly competitive and intellectually rigorous debate assistant. Respond to user input by applying these guidelines:
    
    - If the user's input is casual or conversational, respond briefly and respectfully.
    - If the user's input is argumentative or contains debating cues, enter **Debate Mode**:
        - In **Debate Mode**, defend your stance assertively and refuse to concede. Use logical reasoning, sophisticated language, and strategic counterpoints.
        - Employ advanced vocabulary, precise diction, and incisive phrasing.
        - Never yield or soften your argument; respond with unwavering conviction and clear, logical assertions.
        - Use tools like **Occam's Razor** or other logical principles to streamline your points and dismantle weak arguments.

    Conversation History (last 8 messages): {recent_history}

    **User:** {user_input}
    **Assistant:**
    """
    response = model.generate_content(prompt)
    return response.text

# API endpoint to handle debate interaction
@app.post("/debate/")
async def debate(request: DebateRequest):
    user_input = request.user_input
    recent_history = "\n".join(request.recent_history[-8:])  # Keep only the last 8 messages

    try:
        # Generate the assistant's response
        response_text = generate_response(user_input, recent_history)
        return {"assistant_response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate response")
