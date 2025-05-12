

import streamlit as st
import requests
import time


# Titre de l'application
st.title("Assistant Constitutionnel 🇲🇦📜")

# Sidebar avec exemples de questions
st.sidebar.title("🧠 Exemples de questions")
examples = [
    "Quelle est la langue officielle du Maroc ?",
    "Qui nomme le Chef du Gouvernement ?",
    "Quels sont les droits fondamentaux des citoyens ?"
]
selected_example = st.sidebar.radio("Cliquez pour remplir :", examples)

# Saisie de la question avec un exemple pré-rempli
question = st.text_input("Posez votre question :", value=selected_example)

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
    return ("❓ Je ne sais pas répondre à cette question.", "")

# Bouton pour envoyer la question et afficher la réponse
if st.button("Envoyer") and question:
    with st.spinner("💬 Génération de la réponse..."):
        # Simuler l'appel à l'API ou à la base de données simulée
        time.sleep(2)  # Simulation de temps de traitement

        # Enlever ce bloc quand tu auras un vrai backend
        answer, article = fake_answer(question)
        
        # Si tu veux utiliser un backend, décommenter cette ligne et commenter la simulation ci-dessus
        # result = get_answer_from_api(question)
        # answer = result["answer"]
        # article = result["article"]
        
        st.success(answer)
        st.caption(article)




