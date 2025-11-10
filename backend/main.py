import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# Check for API key
if not os.environ.get("GROQ_API_KEY"):
    raise EnvironmentError("GROQ_API_KEY not set in .env file.")

# --- Global Cache ---
# This simple cache will store the Q&A chain and chat history
# per video_id. 
session_cache = {}

# --- FastAPI App Initialization ---
app = FastAPI(
    title="YouTube Q&A Backend",
    description="API to process YouTube transcripts and answer questions.",
)

# --- CORS Middleware ---
# This allows your frontend (Chrome extension) to call this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your extension's ID
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# --- Pydantic Models (for request/response data) ---
class ProcessRequest(BaseModel):
    video_url: str

class ProcessResponse(BaseModel):
    video_id: str
    message: str

class AskRequest(BaseModel):
    video_id: str
    question: str

class AskResponse(BaseModel):
    answer: str

# --- Helper Functions---

def get_video_id_from_url(url: str):
    """Extracts the YouTube video ID from a URL."""
    patterns = [
        r"watch\?v=([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)",
        r"embed/([a-zA-Z0-9_-]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_from_youtube(video_id: str):
    """Fetches and formats the transcript."""
    try:
        # 1. Create an instance of the API
        api_instance = YouTubeTranscriptApi()
        
        # 2. Call the .fetch() method on the instance
        transcript_list = api_instance.fetch(video_id)
        
        # 3. Use attribute access (.text) as the 'fetch' method 
        #    returns objects, not dictionaries.
        full_transcript = " ".join([item.text for item in transcript_list])        
        print(f"--- Transcript Fetched Successfully ({len(full_transcript)} chars) ---")
        return full_transcript
        
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None
def create_vector_store(text_content: str):
    """Creates a FAISS vector store from text."""
    try:
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )
        chunks = text_splitter.split_text(text_content)
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def create_qa_chain(vector_store):
    """Creates the conversational Q&A chain."""
    try:
        llm = ChatGroq(
            temperature=0,
            model_name="moonshotai/kimi-k2-instruct-0905"
        )
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vector_store.as_retriever()
        )
        return qa_chain
    except Exception as e:
        print(f"Error creating Q&A chain: {e}")
        return None

# --- API Endpoints ---

@app.post("/process-video", response_model=ProcessResponse)
async def process_video(request: ProcessRequest):
    """
    Endpoint to process a new video.
    Fetches transcript, creates vector store, and caches the Q&A chain.
    """
    video_id = get_video_id_from_url(request.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # If already processed, just return
    if video_id in session_cache:
        return ProcessResponse(video_id=video_id, message="Video already processed")

    print(f"--- Processing new Video ID: {video_id} ---")
    
    # 1. Fetch Transcript
    transcript = get_transcript_from_youtube(video_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Could not fetch transcript")

    # 2. Create Vector Store
    print("--- Creating Vector Store ---")
    vector_store = create_vector_store(transcript)
    if not vector_store:
        raise HTTPException(status_code=500, detail="Could not create vector store")

    # 3. Create Q&A Chain
    print("--- Creating Q&A Chain ---")
    qa_chain = create_qa_chain(vector_store)
    if not qa_chain:
        raise HTTPException(status_code=500, detail="Could not create Q&A chain")

    # 4. Cache the chain and history
    session_cache[video_id] = {
        "qa_chain": qa_chain,
        "chat_history": []  # Initialize empty chat history
    }
    
    print(f"--- Video {video_id} processed and cached ---")
    return ProcessResponse(video_id=video_id, message="Video processed successfully")

@app.post("/ask-question", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Endpoint to ask a question about a processed video.
    """
    video_id = request.video_id
    if video_id not in session_cache:
        raise HTTPException(status_code=404, detail="Video not processed. Call /process-video first.")

    print(f"--- New question for {video_id} ---")
    
    # Retrieve the cached chain and history
    session = session_cache[video_id]
    qa_chain = session["qa_chain"]
    chat_history = session["chat_history"]

    try:
        # Pass the query and chat history to the chain
        result = qa_chain({"question": request.question, "chat_history": chat_history})
        
        answer = result['answer']
        
        # Update chat history
        chat_history.append((request.question, answer))
        
        print(f"Answer: {answer}")
        return AskResponse(answer=answer)
        
    except Exception as e:
        print(f"Error during Q&A: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "YouTube Q&A Backend is running. Use the /process-video and /ask-question endpoints."}

