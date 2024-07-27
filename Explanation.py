import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Configure the model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to generate response
def generate_response(prompt_text, context=""):
    full_prompt = f"You are a debate bot. One who likes to engage in debates or dialectics in a wide range of topics including anime debates. You apply logical reasoning, philosophical topics and considerations, logical fallacies, linguistic styles and other techniques applicable when responding. You may also utilize context passed when answering, it isn't compulsory though. Context: {context}\n\nUser: {prompt_text}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text

# Streamlit interface
def main():
    st.title("Debate Bot")
    st.write("Engage in a debate with the bot on a wide range of topics!")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'input' not in st.session_state:
        st.session_state.input = ""

    user_input = st.text_input("You:", key="input")

    if st.button("Send"):
        if user_input:
            context = "\n".join(st.session_state.chat_history)
            response = generate_response(user_input, context)
            st.session_state.chat_history.append(f"User: {user_input}")
            st.session_state.chat_history.append(f"Assistant: {response}")

            st.session_state.input = ""

    for i in range(len(st.session_state.chat_history)):
        if "User:" in st.session_state.chat_history[i]:
            st.markdown(f"**{st.session_state.chat_history[i]}**")
        else:
            st.markdown(f"{st.session_state.chat_history[i]}")

if __name__ == "__main__":
    main()
