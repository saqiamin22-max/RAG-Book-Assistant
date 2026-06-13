import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate


def process_pdf(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name

        # 1. Load PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # 2. Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)

        # 3. Create Embeddings & Vector Store
        embedding_model = MistralAIEmbeddings()
        persist_dir = f"chroma_db/{uploaded_file.name}"
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_dir
        )

        # Clean up the temporary file path safely
        try:
            os.unlink(file_path)
        except OSError:
            pass

        return vectorstore, len(docs), len(chunks)

    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")


def query_document(vectorstore, user_query):
    """Vector store se relevant context nikal kar LLM se answer generate karta hai."""
    try:
        # MMR search standard retrieval ke liye best hai
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.5}
        )

        docs = retriever.invoke(user_query)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Initialize Mistral AI LLM
        llm = ChatMistralAI(model="mistral-small-2506")

        # Chat prompt construction
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant specialized in answering questions from documents.

IMPORTANT RULES:
1. Use ONLY the provided context - never add external information
2. Detect the user's language and respond in the SAME language
3. Format your response clearly with:
   - Headings for main points
   - Bullet points for lists
   - Short paragraphs
   - Code blocks if needed
4. Be concise and direct

If the answer is NOT found in the document, respond EXACTLY with:
"I could not find this information in the document."

Always prioritize accuracy and context relevance."""),
            ("human", """Document Context:
{context}

User Question: {question}

Please provide a helpful answer based ONLY on the context above.""")
        ])

        final_prompt = prompt.invoke({"context": context, "question": user_query})
        response = llm.invoke(final_prompt)
        return response.content

    except Exception as e:
        raise Exception(f"Error generating answer: {str(e)}")