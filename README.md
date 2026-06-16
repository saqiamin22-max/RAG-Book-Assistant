# RAG Book Assistant

An interactive AI-powered application that allows users to upload PDF books and have context-aware, semantic conversations with the content. Built using the RAG (Retrieval-Augmented Generation) architecture, this tool ensures accurate answers grounded directly in the book's text.

## 🚀 Features
- **PDF Ingestion:** Upload any PDF book and process its text automatically.
- **Smart Chunking & Embeddings:** Splits text into optimal chunks and converts them into vector embeddings for semantic search.
- **Efficient Retrieval:** Uses FAISS as a local vector database for lightning-fast context retrieval.
- **Context-Grounded Answers:** Leverages LLMs via LangChain to answer queries based strictly on the retrieved book context, minimizing hallucinations.
- **User-Friendly UI:** Clean and responsive chat interface built with Streamlit.

## 🛠️ Tech Stack
- **Language:** Python
- **Framework:** LangChain
- **Vector Database:** FAISS
- **Frontend/UI:** Streamlit

## 📦 How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/saqiamin22-max/YOUR_REPO_NAME.git](https://github.com/saqiamin22-max/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
