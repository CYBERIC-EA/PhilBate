import streamlit as st
import google.generativeai as genai
import os

# Configure the model with your Gemini API key
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

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

# Streamlit app layout
def main():
    st.title("Competitive Debate Bot")
    st.write("Engage with the debate bot! It responds assertively and logically to arguments, while keeping casual conversation light and polite.")

    # Initialize chat history in session state if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", key="input")

    if st.button("Send"):
        if user_input:
            # Only keep the last 8 messages in the history
            recent_history = "\n".join(st.session_state.chat_history[-8:])

            # Generate response using the limited history
            response = generate_response(user_input, recent_history)
            
            # Update chat history with the new entries
            st.session_state.chat_history.append(f"User: {user_input}")
            st.session_state.chat_history.append(f"Assistant: {response}")

            # Print the recent history to the console
            print("=== Conversation History ===")
            for message in st.session_state.chat_history[-8:]:
                print(message)
            print("===========================")

            # Display only the latest Assistant response in Streamlit
            st.markdown(f"**Assistant:** {response}")

# Run the app
main()
