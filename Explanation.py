import streamlit as st
from langchain.chains import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama.llms import OllamaLLM

# Initialize the model and prompt template
model = OllamaLLM(model="mistral")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a debate bot. One who likes to engage in debates or dialectics in a wide range of topics including anime debates. You apply logical reasoning, philosophical topics and considerations, logical fallacies, linguistic styles and other techniques applicable when responding. You may also utilise context passed when answering, it isn't compulsory though {context}"),
    ("user", "{input}")
])

chain = create_stuff_documents_chain(
    llm=model,
    prompt=prompt
)

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "context": "",  # Add any relevant context here or leave as an empty string
        "chat_history": chat_history,
        "input": question,
    })
    return response["text"]

# Streamlit app
def main():
    st.title("Debate Bot")

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You: ", key="input")

    if st.button("Send"):
        if user_input:
            # Process the user input
            response = process_chat(chain, user_input, st.session_state.chat_history)
            st.session_state.chat_history.append(HumanMessage(content=user_input))
            st.session_state.chat_history.append(AIMessage(content=response))

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            st.write(f"You: {message.content}")
        elif isinstance(message, AIMessage):
            st.write(f"Assistant: {message.content}")

if __name__ == "__main__":
    main()
