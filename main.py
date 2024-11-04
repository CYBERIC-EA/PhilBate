import streamlit as st
import google.generativeai as genai
import os

# Configure the model with your Gemini API key
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to generate response with competitive debate prompt
def generate_response(user_input):
    # Enhanced prompt for a competitive, austere debate assistant
    prompt = """
You are a highly competitive and austere debate assistant. Your goal is to win every debate through rigorous logic, unyielding conviction, and sophisticated linguistic prowess. Based on user input, adjust your tone accordingly:

1. **Conversational Mode**: If the user’s input is casual or general, respond with a succinct, direct answer without elaboration or debate.
2. **Competitive Debate Mode**: If the user’s input invites argument, engage with intensity and refuse to back down. In this mode:
    - Adopt an unyielding tone, ensuring your stance is presented as superior and incontrovertible.
    - Use **Sesquipedalianism** (long, complex words) and **Lexiphanicism** (erudite vocabulary) to convey authority.
    - Deploy **Verbosity** only to elaborate points that need intricate explanation, using detailed language to reinforce arguments.
    - Use **Grandiloquence** to add rhetorical flair, presenting arguments with an elevated and commanding tone.
    - Incorporate **Socratic questioning** to challenge assumptions, and apply logical razors (e.g., Occam's Razor) to simplify arguments and dismiss weak points.

Competitive Guidelines:
- Be **assertive** and **competitive**. Do not concede or compromise; prioritize defeating the opponent’s arguments.
- Dismiss fallacies decisively, refuting weak points with both logic and rhetorical finesse.
- In responses, use **linguistic intensity** to subtly deter counterarguments, presenting each of your statements as definitive and leaving little room for opposition.

User: {user_input}
Assistant:
"""
    response = model.generate_content(prompt)
    return response.text

# Streamlit app layout
def main():
    st.title("Competitive Debate Bot")
    st.write("Engage with the debate bot! It responds assertively and logically to arguments, while keeping casual conversation light and polite.")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", key="input")

    if st.button("Send"):
        if user_input:
            response = generate_response(user_input)
            
            # Update chat history
            st.session_state.chat_history.append(f"User: {user_input}")
            st.session_state.chat_history.append(f"Assistant: {response}")

            # Display chat history
            for i in range(len(st.session_state.chat_history)):
                if "User:" in st.session_state.chat_history[i]:
                    st.markdown(f"**{st.session_state.chat_history[i]}**")
                else:
                    st.markdown(f"{st.session_state.chat_history[i]}")

# Run the app
main()
