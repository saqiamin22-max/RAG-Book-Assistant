import streamlit as st
from RAG_chatbot_backend import process_pdf, query_document

# Page initialization - Pure application layout setup
st.set_page_config(
    page_title="RAG Book Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 🎨 EXCLUSIVE CHATGPT UI CSS (Input Fixed at Bottom)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Fira+Code:wght@400;600&display=swap');

        * { font-family: 'Poppins', sans-serif; }

        /* Main Application Layout Styling */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 100%) !important;
            color: white;
        }

        /* Top sticky or static header design */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            text-align: center;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            margin-bottom: 1.5rem;
        }
        .header-container h1 { color: white !important; font-weight: 800; font-size: 2rem; margin:0; }
        .header-container p { color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-top: 5px; }

        /* Beautiful Chat Custom Bubbles */
        .message-user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.2rem; border-radius: 15px; color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            margin-bottom: 1rem; max-width: 75%; float: right; clear: both;
        }
        .message-assistant {
            background: linear-gradient(135deg, #1e293b 0%, #2d3748 100%);
            border: 1px solid rgba(102, 126, 234, 0.3);
            padding: 1.2rem; border-radius: 15px; color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            margin-bottom: 1rem; max-width: 75%; float: left; clear: both;
        }

        /* Custom formatting rules inside conversational blocks */
        .message-assistant h1, .message-assistant h2, .message-assistant h3 { color: #667eea !important; }
        .message-user code, .message-assistant code { background-color: #0a0e27; color: #00ff88; padding: 0.2rem 0.4rem; border-radius: 4px; font-family: 'Fira Code', monospace; }

        /* Fixed Sidebar Component design wrappers */
        .sidebar-header {
            color: white; font-size: 1.2rem; font-weight: 700; padding: 0.8rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.02) 100%);
            border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-align: center;
        }
        .stat-card {
            background: #1e293b; padding: 1rem; border-radius: 8px;
            text-align: center; border: 1px solid rgba(102, 126, 234, 0.2); margin: 0.5rem 0;
        }
        .stat-number { font-size: 1.6rem; font-weight: 800; color: #667eea; }
        .stat-label { color: #a0aec0; font-size: 0.8rem; text-transform: uppercase; }

        /* Dynamic Status Feedback Cards */
        .success-box { background: #064e3b; padding: 1rem; border-radius: 8px; color: #86efac; border-left: 4px solid #10b981; margin: 1rem 0; }
        .error-box { background: #7f1d1d; padding: 1rem; border-radius: 8px; color: #fca5a5; border-left: 4px solid #ef4444; margin: 1rem 0; }

        /* CRITICAL FIX: Pin the Chat Input block securely to screen bottom viewport */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 55%;
            z-index: 999;
            background-color: transparent !important;
        }

        /* Adjust layouts to adapt safely alongside fixed components without masking */
        div[data-testid="stVerticalBlock"] {
            padding-bottom: 60px;
        }
    </style>
    """, unsafe_allow_html=True)

# Application Header Injection
st.markdown(
    '<div class="header-container"><h1>📚 RAG Book Assistant</h1><p>Upload your PDF document and talk to your books contextually</p></div>',
    unsafe_allow_html=True)

# Session state data layers synchronization
if "vectorstore" not in st.session_state: st.session_state.vectorstore = None
if "messages" not in st.session_state: st.session_state.messages = []
if "current_file" not in st.session_state: st.session_state.current_file = None
if "file_stats" not in st.session_state: st.session_state.file_stats = None

# 📊 SIDEBAR COMPONENT
with st.sidebar:
    st.markdown('<div class="sidebar-header">📖 Document Metadata</div>', unsafe_allow_html=True)

    if st.session_state.current_file:
        st.markdown(
            '<div class="stat-card"><div class="stat-number">✅</div><div class="stat-label">Status: Active</div></div>',
            unsafe_allow_html=True)
        st.markdown(f"**Loaded File:** `{st.session_state.current_file}`")

        if st.session_state.file_stats:
            c1, c2 = st.columns(2)
            with c1: st.markdown(
                f'<div class="stat-card"><div class="stat-number">{st.session_state.file_stats["pages"]}</div><div class="stat-label">Pages</div></div>',
                unsafe_allow_html=True)
            with c2: st.markdown(
                f'<div class="stat-card"><div class="stat-number">{st.session_state.file_stats["chunks"]}</div><div class="stat-label">Chunks</div></div>',
                unsafe_allow_html=True)

        if st.button("🗑️ Remove Document", use_container_width=True):
            st.session_state.vectorstore = None
            st.session_state.current_file = None
            st.session_state.messages = []
            st.session_state.file_stats = None
            st.rerun()
    else:
        st.markdown(
            '<div class="stat-card" style="padding:2rem 1rem;"><h4 style="color:#a0aec0; margin:0;">📂 No Document Active</h4><p style="font-size:0.85rem; color:#718096; margin:5px 0 0 0;">Upload a PDF file to begin interaction</p></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("💡 Pro Tips", expanded=False):
        st.markdown(
            "- **Clear PDFs:** Avoid scanned files with poor contrast.\n- **Be Specific:** Frame your question focusing on keywords.\n- **Language Sync:** Assistant matches the language of your prompt input automatically.")

# MAIN INTERFACE VIEW MANAGEMENT
if not st.session_state.vectorstore:
    # 1. State: Upload Form View
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<div style="text-align:center; padding: 2rem 0;"><h3 style="font-weight:700;">📤 Upload Your Document</h3><p style="color:#a0aec0;">Select any standard PDF ebook or document</p></div>',
            unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["pdf"], key="pdf_upload", label_visibility="collapsed")

        if uploaded_file is not None and uploaded_file.name != st.session_state.current_file:
            with st.spinner("🔄 Deep parsing file structures and setting vectors..."):
                try:
                    v_store, total_pages, total_chunks = process_pdf(uploaded_file)
                    st.session_state.vectorstore = v_store
                    st.session_state.current_file = uploaded_file.name
                    st.session_state.file_stats = {'pages': total_pages, 'chunks': total_chunks}
                    st.session_state.messages = []
                    st.markdown('<div class="success-box">✅ Database Synced! Document processed cleanly.</div>',
                                unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ {str(e)}</div>', unsafe_allow_html=True)
else:
    # 2. State: Chat Workspace View
    # Independent scrollable conversational arena layout
    chat_container = st.container()

    with chat_container:
        if len(st.session_state.messages) == 0:
            st.markdown(
                '<div style="text-align:center; padding:5rem 0; color:#a0aec0;"><h3>👋 Vector Engine Ready</h3><p>Ask anything related to the document contents below.</p></div>',
                unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="message-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="message-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

            # Clear float breaks to maintain clean grid flows inside HTML segments
            st.markdown('<div style="clear:both;"></div>', unsafe_allow_html=True)

    # 🎯 STICKY BOTTOM INPUT COMPONENT
    # (Pinned cleanly to screen base using CSS viewport injectors above)
    if user_input := st.chat_input("Ask something from the book... 💭"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # Automatic evaluation trigger if current prompt trace is flagged user-end
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest_query = st.session_state.messages[-1]["content"]

        with st.spinner("🤔 Searching vector contexts..."):
            try:
                ai_response = query_document(st.session_state.vectorstore, latest_query)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ {str(e)}</div>', unsafe_allow_html=True)