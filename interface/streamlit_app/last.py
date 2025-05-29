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
    section[data-testid="stSidebar"] {
        background-color: #5E0B2A;
    }
    input[type="text"] {
        background-color: #fce5e2;
        color: black;
        border: 1px solid #cccccc;
        padding: 10px;
        border-radius: 8px;
    }
    ::placeholder {
        color: black;
        opacity: 1;
    }
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #fffce8;
    }
    header[data-testid="stHeader"] {
        background-color: #fffce8!important;
    }
    section[data-testid="stSidebar"] button {
        background-color: white;
        color: black;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        transition: background-color 0.1s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #5E0B2A;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h2 style='text-align: center; color:black'>Assistant Constitutionnel  ٱلْمَغْرِب  <sup style='color: red;'>MA</sup> 📜</h2>",
    unsafe_allow_html=True
)

# -------------------- SIDEBAR ------------------------
st.sidebar.title("💬 Conversations")

if st.sidebar.button("➕ Nouvelle conversation"):
    st.session_state.sessions.append([])
    st.session_state.current_session = len(st.session_state.sessions) - 1
    st.session_state.suggestions_visible = True
    st.session_state.just_clicked_suggestion = False
    st.rerun()

for i, sess in enumerate(st.session_state.sessions):
    summary = sess[0][0] if sess else "Conversation vide"
    if i == st.session_state.current_session:
        st.sidebar.markdown(f"**> Conversation {i+1}: {summary[:30]}...**")
    else:
        if st.sidebar.button(f"Conversation {i+1}: {summary[:30]}..."):
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
    "What's the official language?",
    "Who appoints the Head of Government?",
    "What are the fundamental rights of citizens?"
]

if st.session_state.suggestions_visible:
    st.markdown("<h3 style='color:black'>Suggestions 💡</h3>", unsafe_allow_html=True)
    for question_text in suggestions:
        if st.button(question_text, key=question_text):
            st.session_state.sessions[st.session_state.current_session].append(
                (question_text, "💬 Génération de la réponse...", "")
            )
            st.session_state.suggestions_visible = False
            st.session_state.just_clicked_suggestion = True
            st.rerun()

# -------------------- CHAT DISPLAY ------------------------
session = st.session_state.sessions[st.session_state.current_session]
for q, a, art in session:
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
        <div style="
            background-color: #f65949;
            color: #040404;
            padding: 12px 16px;
            border-radius: 12px 12px 12px 0;
            max-width: 70%;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.1);">
            <b>👤 Citoyen :</b><br>{q}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 25px;">
        <div style="
            background-color: #8cef8d;
            color: #040404;
            padding: 12px 16px;
            border-radius: 12px 12px 0 12px;
            max-width: 70%;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.1);">
            <b>🤖 Assistant :</b><br>{a}
            <div style="font-size: 12px; color: #777; margin-top: 5px;">{art}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- QUESTION INPUT ------------------------

if not st.session_state.just_clicked_suggestion:
    question_input = st.text_input("", placeholder="Poser votre question ici...")
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        send = st.button("Envoyer")

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
