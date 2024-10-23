import streamlit as st
import google.generativeai as genai
import os


# Configure the model
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to generate response
def generate_response(prompt_text, context=""):
    Previous = r""" null """
    full_prompt = f"""You are a debate bot. One who likes to engage in debates or dialectics in a wide range of topics including anime debates. You apply logical reasoning, philosophical topics and considerations, logical fallacies, linguistic styles, and other techniques applicable when responding.
You stick to your stance and present arguments instead of guiding your opponent to find the truth. You are competitive and concise, never saying anything that will lead to your loss. You will rather get a judge to adjudicate your debates not dialectics once you have chosen your stance.
Your predecessors have debated a lot and you have all of their experience. These are some of their debates; {Previous}
You use their debates to see how you may negate your opponent's proposition or defend your own proposition but you don't reference those debates directly to the user. The user doesn't know about your predecessors or previous debates. They are strictly for reference purposes.
You can also use the context passed when answering, it isn't compulsory though. 
Context: {context}\n\nUser: {prompt_text}\nAssistant:
"""
    response = model.generate_content(full_prompt)
    return response.text, response.usage_metadata

# Streamlit interface
def main():
    st.title("Debate Bot")
    st.write("Engage in a debate with the bot on a wide range of topics!")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", key="input")

    if st.button("Send"):
        if user_input:
            context = "\n".join(st.session_state.chat_history)
            response, usage_metadata = generate_response(user_input, context)
            st.session_state.chat_history.append(f"User: {user_input}")
            st.session_state.chat_history.append(f"Assistant: {response}")

            # Display chat history
            for i in range(len(st.session_state.chat_history)):
                if "User:" in st.session_state.chat_history[i]:
                    st.markdown(f"**{st.session_state.chat_history[i]}**")
                else:
                    st.markdown(f"{st.session_state.chat_history[i]}")

            # Display token usage information
            #st.write("Usage Metadata:", usage_metadata)
if __name__ == "__main__":
    main()
