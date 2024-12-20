import streamlit as st
from ollama import chat

st.title("Local Rag")

#import a file
st.file_uploader("Please enter a file to augment the model", type=["csv", "pdf", "json", "txt"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages from chat history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#FIXME - mke the user upload a file

# Accept user input
if prompt := st.chat_input("Ask something"):
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare the message history for the API call
    ollama_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    #FIXME - process file from user and pass it to model

    # Get the model's response from Ollama
    response = chat(model="llama3.1", messages=ollama_messages)

    # Debug the response structure (uncomment the next line to display the response)
    # st.write(response)

    # Safely handle the assistant's response from the "message" key
    try:
        assistant_response = response['message']['content']
    except KeyError:
        assistant_response = "Sorry, I couldn't process that request."

    # Display assistant's response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
