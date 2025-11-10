# YouTube AI Assistant

> **Interact intelligently with YouTube videos using AI.**  
> Ask open-ended questions, get instant answers, and summarize long videos — directly from a Chrome extension powered by FastAPI, LangChain, and Groq’s `moonshotai/kimi-k2-instruct-0905` model.

---

## Overview

**YouTube AI Assistant** is an intelligent browser extension that allows users to engage with YouTube videos conversationally.  
By leveraging **LangChain**, **FAISS**, **Hugging Face embeddings**, and **Groq inference**, it enables:
- Question-answering about any YouTube video content
- Semantic search across transcripts
- Instant video summarization  

The extension combines:
- **Frontend:** Chrome extension built using **React + Vite**  
- **Backend:** Python **FastAPI** service with **Groq API**, **LangChain**, and **FAISS**  
- **Model:** `moonshotai/kimi-k2-instruct-0905` for ultra-fast, deterministic inference  

---

## Key Features

Ask open-ended questions about YouTube videos  
Get instant, AI-generated answers  
View relevant video timestamps (optional extension)  
Summarize lengthy videos into concise points  
Semantic understanding via FAISS-based retrieval  
Low-latency responses using Groq’s high-speed inference API  
Privacy-first design — local embeddings, transcript processing  

---

##  How to Run

### 1. Backend (FastAPI Server)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on macOS/Linux
    source venv/bin/activate

    # Activate on Windows
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set your API Key:**
    * In the `backend` folder, create a file named `.env`
    * Add your Groq API key to this file:
    ```plaintext
    GROQ_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    > **Note:** Leave this terminal running. The server must be active for the extension to work.

### 2. Frontend (Chrome Extension)

1.  **Open a new terminal.**

2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

3.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

4.  **Build the extension:**
    ```bash
    npm run build
    ```
    > This will create a `dist` folder inside the `frontend` directory. This `dist` folder is your complete extension.

### 3. Load the Extension in Chrome

1.  Open Google Chrome and navigate to `chrome://extensions`.
2.  Enable **"Developer mode"** using the toggle in the top-right corner.
3.  Click the **"Load unpacked"** button.
4.  In the file dialog, select the **`frontend/dist`** folder.
5.  The extension will appear in your list. Pin it to your toolbar for easy access.

### 4. Usage

1.  Ensure your backend server (from Step 1) is still running.
2.  Go to any YouTube video page.
3.  Click the extension's icon in your Chrome toolbar.
4.  Click the **"Start Q&A"** button to process the video.
5.  Once processed, ask any question about the video in the chat box.

