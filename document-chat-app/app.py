import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
import shutil

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
CHROMA_PERSIST_DIR = 'chroma_db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# Global variables
vectorstore = None
qa_chain = None
chat_history = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global vectorstore, qa_chain, chat_history

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF and TXT files are allowed'}), 400

    try:
        # Clear previous uploads and vector store
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

        # Reset chat history
        chat_history = []

        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Load and process the document
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(filepath)
        else:
            loader = TextLoader(filepath)

        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)

        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )

        # Create the conversational chain
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            verbose=False
        )

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'filename': filename,
            'chunks': len(chunks)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global qa_chain, chat_history

    if qa_chain is None:
        return jsonify({'error': 'Please upload a document first'}), 400

    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        # Get response from the chain
        result = qa_chain({
            "question": question,
            "chat_history": chat_history
        })

        # Update chat history
        chat_history.append((question, result['answer']))

        # Keep only last 5 exchanges to avoid context getting too long
        if len(chat_history) > 5:
            chat_history = chat_history[-5:]

        return jsonify({
            'answer': result['answer'],
            'sources': [doc.page_content[:200] + '...' for doc in result['source_documents']]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    global vectorstore, qa_chain, chat_history

    vectorstore = None
    qa_chain = None
    chat_history = []

    # Clean up files
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    if os.path.exists(CHROMA_PERSIST_DIR):
        shutil.rmtree(CHROMA_PERSIST_DIR)
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

    return jsonify({'message': 'Session reset successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
