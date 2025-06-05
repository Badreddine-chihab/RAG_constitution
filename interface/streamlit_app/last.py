import streamlit as st
import requests
import time

# -------------------- SESSION STATE INIT ------------------------
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "suggestions_visible" not in st.session_state:
    st.session_state.suggestions_visible = True
if "just_clicked_suggestion" not in st.session_state:
    st.session_state.just_clicked_suggestion = False

if st.session_state.current_session is None:
    st.session_state.sessions.append([])
    st.session_state.current_session = 0

# -------------------- PAGE CONFIG ------------------------
st.set_page_config(page_title="Assistant Constitutionnel ٱلْمَغْرِب", layout="wide")

st.markdown(
    """
    <style>
    /* Main background and text */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        padding: 12px 16px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebarNavItems"] {
        padding-top: 20px;
    }
    
    /* Input field */
    .stTextInput input {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTextInput input:focus {
        border-color: #c1272d;
        box-shadow: 0 0 0 2px rgba(193,39,45,0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #c1272d;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #a02026;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Suggestion buttons */
    .stButton>button.suggestion {
        background-color: #ffffff;
        color: #006233;
        border: 2px solid #006233;
        margin-bottom: 8px;
        width: 100%;
        text-align: left;
    }
    .stButton>button.suggestion:hover {
        background-color: #e8f5e9;
        color: #006233;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        background-color: #f8f9fa;
        color: #333;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 8px 16px;
        margin-bottom: 8px;
        width: 100%;
        text-align: left;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #e9ecef;
        border-color: #c1272d;
        color: #c1272d;
    }
    section[data-testid="stSidebar"] .active {
        background-color: #c1272d;
        color: white !important;
    }
    
    /* Chat bubbles */
    .user-message {
        background-color: #c1272d;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin-bottom: 8px;
        max-width: 80%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .assistant-message {
        background-color: #f1f8e9;
        color: #333;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin-bottom: 8px;
        max-width: 80%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #006233;
    }
    .article-reference {
        font-size: 12px;
        color: #666;
        margin-top: 8px;
        font-style: italic;
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #c1272d, #006233);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 24px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# In your Streamlit app code (the first file you shared), look for this section:
st.markdown(
    """
    <style>
    /* Main background and text */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8f9fa;
    }
    /* ... (other existing styles) ... */
    </style>
    """,
    unsafe_allow_html=True
)

# ADD THE NEW STYLE RIGHT AFTER THE EXISTING STYLE BLOCK:
st.markdown(
    """
    <style>
    /* Text input improvements */
    .stTextInput input {
        color: black !important;
        background-color: #ffffff !important;
        border: 2px solid #c1272d !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stTextInput input:focus {
        box-shadow: 0 0 0 2px rgba(193,39,45,0.2) !important;
        border-color: #c1272d !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div class="header">
        <h2 style="margin:0; color:white;">Assistant Constitutionnel <span style="color:#ffcc00">ٱلْمَغْرِب</span> <sup style="color: white;">MA</sup> 📜</h2>
        <p style="margin:0; opacity:0.8;">Votre guide pour la Constitution Marocaine</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------- SIDEBAR ------------------------
st.sidebar.markdown("""
<div style="padding-bottom: 20px; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;">
    <h3 style="color: #c1272d; margin-bottom: 5px;">💬 Conversations</h3>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("➕ Nouvelle conversation", key="new_chat"):
    st.session_state.sessions.append([])
    st.session_state.current_session = len(st.session_state.sessions) - 1
    st.session_state.suggestions_visible = True
    st.session_state.just_clicked_suggestion = False
    st.rerun()

for i, sess in enumerate(st.session_state.sessions):
    summary = sess[0][0] if sess else "Nouvelle conversation"
    btn_class = "active" if i == st.session_state.current_session else ""
    if st.sidebar.button(f"🗨️ {summary[:30]}...", key=f"conv_{i}"):
        st.session_state.current_session = i
        st.rerun()

# -------------------- BACKEND API ------------------------
def get_answer_from_api(question):
    try:
        res = requests.post("http://localhost:8000/query", json={"question": question})
        return res.json()
    except:
        return {"answer": "⚠️ Erreur : API injoignable.", "article": ""}

# -------------------- SUGGESTIONS ------------------------
suggestions = [
    "Quelle est la langue officielle?",
    "Qui nomme le Chef du Gouvernement?",
    "Quels sont les droits fondamentaux des citoyens?"
]

if st.session_state.suggestions_visible:
    st.markdown("<h4 style='color:#006233; margin-bottom:12px;'>Suggestions 💡</h4>", unsafe_allow_html=True)
    cols = st.columns(1)
    for question_text in suggestions:
        if cols[0].button(question_text, key=question_text, type="secondary"):
            st.session_state.sessions[st.session_state.current_session].append(
                (question_text, "💬 Génération de la réponse...", "")
            )
            st.session_state.suggestions_visible = False
            st.session_state.just_clicked_suggestion = True
            st.rerun()

# -------------------- CHAT DISPLAY ------------------------
session = st.session_state.sessions[st.session_state.current_session]
for q, a, art in session:
    # User message
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
        <div class="user-message">
            <b>Vous :</b><br>{q}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Assistant message
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
        <div class="assistant-message">
            <b>Assistant :</b><br>{a}
            {f'<div class="article-reference">{art}</div>' if art else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- QUESTION INPUT ------------------------
if not st.session_state.just_clicked_suggestion:
    question_input = st.text_input("", placeholder="Poser votre question ici...", key="question_input")
    _, col2, col3 = st.columns([6, 1, 1])
    with col3:
        send = st.button("Envoyer", type="primary")

    if send and question_input:
        st.session_state.sessions[st.session_state.current_session].append((question_input, "💬 Génération de la réponse...", ""))
        st.rerun()
else:
    st.session_state.just_clicked_suggestion = False  # Reset for next round

# -------------------- GENERATE ANSWER ------------------------
session = st.session_state.sessions[st.session_state.current_session]

if session and session[-1][1] == "💬 Génération de la réponse...":
    time.sleep(1.5)
    last_question = session[-1][0]
    response = get_answer_from_api(last_question)
    answer = response.get("answer", "OOps! Je ne sais pas répondre à cette question ❓")
    article = response.get("article", "")
    session[-1] = (last_question, answer, article)
    st.rerun()