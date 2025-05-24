import streamlit as st
import requests
import time
#best version
# cest elle qui marche final 
#à ajouter apres: supprimer historique +barre box delete
if "sessions" not in st.session_state:
    st.session_state.sessions = []  # liste de conversations (sessions)
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# Créer une première session vide si aucune
if st.session_state.current_session is None:
    st.session_state.sessions.append([])
    st.session_state.current_session = 0


if "suggestions_visible" not in st.session_state:
    st.session_state.suggestions_visible = True
 
# Titre de l'application
st.set_page_config(page_title="Assistant Constitutionnel", layout="wide")
st.markdown(
    """
    <h2 style='text-align: center;'>Assistant Constitutionnel 📜</h2>
    """,
    unsafe_allow_html=True
)
#initialisation de l historique 
if "history" not in st.session_state:
    st.session_state.history = []



# Sidebar avec exemples de questions

st.sidebar.title("💬 Conversations")
st.markdown(
    """
    <style>
        /* Couleur du sidebar */
        section[data-testid="stSidebar"] {
            background-color: #fce5e2;  /* Change ici si tu veux une autre couleur */
        }

        /* Changer couleur du champ de saisie */
        input[type="text"] {
            background-color: #fce5e2;  /* Fond */
            color: #000000;             /* Texte */
            border: 1px solid #cccccc;  /* Bord */
            padding: 10px;
            border-radius: 8px;
        }

        /* Placeholder (texte gris par défaut) */
        ::placeholder {
            color: #fce5e2;
            opacity: 1;
        }
/* Changer la couleur de fond générale sur toute la page */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #fffce8;  /* Choisis ta couleur ici */
}
   header[data-testid="stHeader"] {
        background-color: #fffce8!important;
    }
    /* Boutons dans la sidebar */
section[data-testid="stSidebar"] button {
    background-color: #bed7bb; /* Vert */
    color: black;
    border-radius: 8px;
    border: none;
    padding: 8px 16px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

section[data-testid="stSidebar"] button:hover {
    background-color: #bed7bb; /* Vert plus foncé au hover */
}

    </style>
    """,
    unsafe_allow_html=True
)


# Bouton nouvelle conversation
if st.sidebar.button("➕ Nouvelle conversation"):
    st.session_state.sessions.append([])
    st.session_state.current_session = len(st.session_state.sessions) - 1
    st.session_state.suggestions_visible = True  # Réafficher les suggestions
    

# Liste des conversations
for i, sess in enumerate(st.session_state.sessions):
    summary = sess[0][0] if sess else "Conversation vide"
    if i == st.session_state.current_session:
        st.sidebar.markdown(f"**> Conversation {i+1}: {summary[:30]}...**")
    else:
        if st.sidebar.button(f"Conversation {i+1}: {summary[:30]}..."):
            st.session_state.current_session = i
            st.stop()

#------------------
        
        
        


#-------------

# Fonction pour simuler l'appel à une API (futur backend)
def get_answer_from_api(question):
    try:
        # Simuler une requête API (fonction à remplacer avec un backend réel)
        res = requests.post("http://localhost:8000/query", json={"question": question})
        return res.json()
    except Exception as e:
        return {"answer": "⚠️ Erreur : API injoignable.", "article": ""}

# Base de données simulée de réponses
simulated_db = {
    "langue": ("La langue officielle du Maroc est l'arabe.", "📖 Article 5"),
    "chef": ("Le Roi nomme le Chef du Gouvernement.", "📖 Article 47"),
    "droits": ("Tous les citoyens jouissent des libertés fondamentales.", "📖 Article 19"),
}

# Fonction pour générer une réponse simulée
def fake_answer(question):
    for key in simulated_db:
        if key in question.lower():
            return simulated_db[key]
    return ("❓ Je ne sais pas répondre à cette question ❓", "")
#fonction historique 
def add_to_history(question, answer, article):
    st.session_state.history.append((question, answer, article))

#                  suggestions
suggestions = [ "Quelle est la langue officielle du Maroc ?",
    "Qui nomme le Chef du Gouvernement ?",
    "Quels sont les droits fondamentaux des citoyens ?"]

# Suggestions cliquables (dans le corps principal, pas la sidebar)
if st.session_state.suggestions_visible:
    st.markdown("###  Suggestions 💡")
    for question_text in suggestions:
        if st.button(question_text):
          st.session_state.sessions[st.session_state.current_session].append(
           (question_text, "💬 Génération de la réponse...", "")
              )
          st.session_state.suggestions_visible = False        #visibilité des suggestions apres click :non 
          st.session_state.last_question = question_text
          st.rerun()



# Affichage du chat (discussion)


session = st.session_state.sessions[st.session_state.current_session]

for q, a, art in session:
    # Question à gauche
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
        <div style="
            background-color: #f65949;
            color: #040404;
            padding: 12px 16px;
            border-radius: 12px 12px 12px 0;
            max-width: 70%;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.1);
            ">
            <b>👤 Citoyen :</b><br>{q}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Réponse à droite
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 25px;">
        <div style="
            background-color: #8cef8d;
            color: #040404;
            padding: 12px 16px;
            border-radius: 12px 12px 0 12px;
            max-width: 70%;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.1);
            ">
            <b>🤖 Assistant :</b><br>{a}
            <div style="font-size: 12px; color: #777; margin-top: 5px;">{art}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)






# Saisie de la question avec un exemple pré-rempli
question_input = st.text_input("", placeholder="Poser votre question ici...")

# Bouton pour envoyer la question
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    send = st.button(" Envoyer")

# Traitement de la question saisie
if send and question_input:
    st.session_state.sessions[st.session_state.current_session].append((question_input, "💬 Génération de la réponse...", ""))
    st.rerun()


# Si la dernière entrée est une "génération" en cours, remplacer par la vraie réponse
session = st.session_state.sessions[st.session_state.current_session]

if session and session[-1][1] == "💬 Génération de la réponse...":
    time.sleep(2)
    last_question = session[-1][0]
    answer, article = fake_answer(last_question)
    session[-1] = (last_question, answer, article)
    if "last_question" in st.session_state:
        del st.session_state["last_question"]
    st.rerun()


