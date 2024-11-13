import streamlit as st
import ollama
import PyPDF2
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the SentenceTransformer model for creating embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() if page.extract_text() else ''
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {e}")
        return ""

# Function to create embeddings for the extracted PDF text
def create_embeddings(text):
    sentences = text.split('\n')  # Split text into sentences or chunks
    embeddings = embedder.encode(sentences)  # Generate embeddings for each sentence
    return embeddings, sentences

# Function to search for relevant information from PDF based on the user's question
def search_pdf_embeddings(query, pdf_embeddings, pdf_sentences):
    query_embedding = embedder.encode([query])  # Embed the query
    index = faiss.IndexFlatL2(pdf_embeddings.shape[1])
    index.add(pdf_embeddings)
    D, I = index.search(np.array(query_embedding).astype(np.float32), k=1)  # Top-1 similarity
    return pdf_sentences[I[0][0]]

# Set up the Streamlit interface
st.title("Chat with PDF Bot using RAG")
st.write("Upload your PDF and ask questions about it.")

# Check if the PDF and embeddings are already stored in session_state
if 'pdf_embeddings' not in st.session_state:
    st.session_state.pdf_embeddings = None
    st.session_state.pdf_sentences = None

# Upload PDF
pdf_file = st.file_uploader("Upload your PDF file", type="pdf")

if pdf_file:
    # Extract text from the uploaded PDF
    pdf_text = extract_text_from_pdf(pdf_file)
    
    if pdf_text.strip() == "":  # Check if PDF extraction was successful
        st.error("Failed to extract text from the PDF. Please upload a different file.")
    else:
        # Create embeddings for the PDF text
        pdf_embeddings, pdf_sentences = create_embeddings(pdf_text)
        
        # Store the PDF info in session state for later use
        st.session_state.pdf_text = pdf_text
        st.session_state.pdf_embeddings = pdf_embeddings
        st.session_state.pdf_sentences = pdf_sentences

        st.write("PDF successfully loaded. You can now ask questions about it.")

# Handle user messages and responses
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to get response from Ollama LLaMA3 model
def get_response_from_ollama(context, user_message):
    response = ollama.chat(
        model='llama3', 
        messages=[
            {'role': 'system', 'content': f"Provide detailed responses based on the following context: {context}"},
            {'role': 'user', 'content': user_message}
        ]
    )
    return response['message']['content']

# Display the chat history
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.write(f"**You**: {message['content']}")
    else:
        st.write(f"**Bot**: {message['content']}")

# Input box for user messages
user_input = st.text_input("Ask me a question about the PDF:")

# If the user sends a message
if user_input:
    # Append the user's message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # If PDF data exists in session state, retrieve context from it
    if st.session_state.pdf_embeddings is not None:
        # Search the PDF content for relevant information
        relevant_context = search_pdf_embeddings(user_input, 
                                                 st.session_state.pdf_embeddings, 
                                                 st.session_state.pdf_sentences)
        # Get the response from Ollama LLaMA3 model using the retrieved context
        bot_response = get_response_from_ollama(relevant_context, user_input)
    else:
        bot_response = "No PDF loaded yet. Please upload a PDF first."
    
    # Append the bot's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Show bot's response
    st.write(f"**Bot**: {bot_response}")
