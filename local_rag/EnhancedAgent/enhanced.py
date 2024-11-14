from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from uuid import uuid4
import streamlit as st
import loaders
import faiss

st.title("Llama3.2 Local Rag with Ollama")

#initialize model
ollama_model = Ollama(
    base_url='http://localhost:11434',
    model="llama3.2"
)

#intialize doc store to hold loaded documents
doc_store = []

# Upload a file
uploaded_files = st.file_uploader("Upload a file (csv, json, pdf, txt)", type=["csv", "pdf", "json", "txt"], accept_multiple_files=True)

if uploaded_files:
    #Load uploaded file
    for file in uploaded_files:
        loaders.load(file, doc_store)

#print(f"Doc Store: {doc_store}")

#initialize a function to embed documents and queries
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

#set up an index that everything will be stored and retrieved with
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

#initialize vector store
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

if len(doc_store) > 0:
    #set up ids for documents
    uuids = [str(uuid4()) for _ in range(len(doc_store))]

    #embed documents and add them to vector store
    vector_store.add_documents(documents=doc_store, ids=uuids)
    #print(f"Vector Store: {vector_store}")


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "Context:" in message["content"]:
                content_list = message["content"].split()
                #print("\nLIST:\n", content_list)
                i = content_list.index("Context:")
                st.markdown(" ".join(content_list[:i]))
            else:
                st.markdown(message["content"])
    
    # Accept user input and respond
    if user_input := st.chat_input("Ask something about the file"):
        # Show user's input
        with st.chat_message("user"):
            st.markdown(user_input)

        # Add user input to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        #set up a retriever from the vector store
        retriever = vector_store.as_retriever()
        
        #retrieve top 20 relevant Documents (text chunks) according to the user input
        relevant_docs = retriever.invoke(user_input, top_k=20)

        #add docuemnt text to vault
        vault = [doc.page_content for doc in relevant_docs]
            
        #turn vault content into one string
        vault_content = "\n".join(vault)

        #augment user input with vault content
        #TESTING SWITCHING BETWEEN FILE AND CONTEXT:WQ
        augmented_input = f"{user_input}\nContext:\n{vault_content}"


        #set up a chain for the model
        qachain = RetrievalQA.from_chain_type(llm=ollama_model, retriever=retriever)

        #pass augmented user prompt through the chain
        augmented_answer = qachain.invoke({"query": augmented_input})
        #extract model response
        augmented_response = augmented_answer['result']
        
        #get answer directly from llama3.2, without file augmentation
        direct_answer = ollama_model.invoke(user_input)
        direct_response = direct_answer

        print("AUG: ", augmented_response)
        print("DIR: ", direct_response)

        eval_prompt = f"""
User asked: '{user_input}'.

Option 1: {augmented_response}
Option 2: {direct_response}

Evaluate both options. Please choose the better response based on:
1. Relevance to the user's question.
2. Do not responses that include phrases like "I don't know," "I have no context, or that otherwise imply that answer is not known, or there is not a file or context"

Respond by repeating the best choice word for word. 
"""
        eval_tool = Tool(name="EvaluateResponses", func=lambda _: ollama_model.invoke(eval_prompt), description="Given two query responses, the agent picks the better response by considering relevance, completeness, and avoiding uncertain answers."
)

        template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

        #create prompt from template
        prompt = PromptTemplate.from_template(template)

        #initialize empty scratchpad so agent can keep track of intermediate steps
        agent_scratchpad = ""

        #store list of tools
        tools = [eval_tool]

        #create the agent using the llm_with_prompt
        agent = create_react_agent(tools=tools, llm=ollama_model, prompt=prompt)

        #create agent executor, have it try again if it gets a parsing error
        agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)

        #have agent decide which tool/response to use
        agent_decision = agent_executor.invoke({"input": user_input, "agent_scratchpad":agent_scratchpad})['output']
        print("AGENT", agent_decision)

        #display proper response based on agent's default, falling back on the augmented decision in edge cases
        #if "Option 2" in agent_decision:
            #best_response = direct_response
        #else:
            #best_response = augmented_response
        
        best_response = agent_decision

        # Show the assistant's response
        with st.chat_message("assistant"):
            st.markdown(best_response)

        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": best_response})


