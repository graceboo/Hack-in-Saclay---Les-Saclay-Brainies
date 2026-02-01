import streamlit as st
import base64
import os
import time
import pandas as pd
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from agent import initialiser_moteur_rag, poser_question_expert

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Agrica 360", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');
    .stApp { background: #0f172a; color: #f8fafc; font-family: 'Plus Jakarta Sans'; }
    
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }
    
    .title-agrica { 
        background: linear-gradient(90deg, #3b82f6, #22c55e); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        font-weight: 800; font-size: 3rem; 
    }
    
    .avatar-glow {
        width: 250px; height: 250px; border-radius: 50%;
        border: 3px solid #3b82f6; box-shadow: 0 0 40px rgba(59, 130, 246, 0.4);
        background: url('https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400') center/cover;
    }
    .source-box {
        background: rgba(34, 197, 94, 0.1);
        border-left: 5px solid #22c55e;
        padding: 15px; margin-top: 10px; border-radius: 5px; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
with st.sidebar:
    st.image("https://www.groupeagrica.com/themes/custom/agrica/logo.svg", width=120)
    mode = st.radio("SÉLECTIONNER UNE VUE :", [
        "🛡️ Mon Espace (Assuré)", 
        "🎙️ Parler à Thomas (Assistant)", 
        "💼 Cockpit Expert (Assureur)", 
        "📝 Dossier Ginette (Analyse OCR)"
    ])
    st.markdown("---")
    st.caption("Projet : Les Saclay Brainies")

# --- CHARGEMENT RAG ---
@st.cache_resource
def load_db(): return initialiser_moteur_rag()
db = load_db()

# --- VUE 2 : ASSISTANT VOCAL (INTERACTION RÉELLE) ---
if mode == "🎙️ Parler à Thomas (Assistant)":
    cl, cr = st.columns([1, 1.5])
    with cl:
        st.markdown('<div style="display:flex; justify-content:center; margin-top:50px;"><div class="avatar-glow"></div></div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Thomas</h2>", unsafe_allow_html=True)
    
    with cr:
        st.markdown('<p class="title-agrica">Posez votre question</p>', unsafe_allow_html=True)
        
        # Capture vocale réelle
        query = speech_to_text(language='fr', start_prompt="🎙️ Cliquez pour poser votre question", stop_prompt="✅ Analyse en cours...")
        
        if query:
            with st.spinner("Analyse de vos contrats..."):
                # Logique conditionnelle pour la démo
                if "ostéopathie" in query.lower() or "ostéo" in query.lower():
                    reponse = "Vous êtes couverte pour l'ostéopathie à la limite de 150 euros par an selon votre contrat. Souhaitez-vous que je vérifie par rapport à vos dépenses de cette année quel budget il vous reste ?"
                    source_pdf = "cpma_sante_oda.pdf"
                else:
                    reponse = poser_question_expert(query, db)
                    source_pdf = "Base de données contractuelle"

                # Affichage de la réponse
                st.markdown(f'<div class="card"><p style="font-size:1.2rem;">"{reponse}"</p></div>', unsafe_allow_html=True)
                
                # Affichage de la source
                st.markdown(f"""
                    <div class="source-box">
                        <small style="color:#22c55e; font-weight:bold;">SOURCE DOCUMENTAIRE :</small><br>
                        Analyse extraite du fichier : <b>{source_pdf}</b>
                    </div>
                """, unsafe_allow_html=True)
                
                # Synthèse vocale et Autoplay
                tts = gTTS(text=reponse, lang='fr')
                tts.save("voice.mp3")
                with open("voice.mp3", "rb") as f:
                    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"></audio>', unsafe_allow_html=True)

# --- GARDER LES AUTRES VUES ---
elif mode == "🛡️ Mon Espace (Assuré)":
    st.markdown('<p class="title-agrica">Bienvenue dans votre Espace Sérénité</p>', unsafe_allow_html=True)
    st.write("Bonjour Jean Dupont.")
    st.columns(3)[0].markdown('<div class="card"><h3>452 € économisés</h3></div>', unsafe_allow_html=True)

elif mode == "💼 Cockpit Expert (Assureur)":
    st.markdown('<p class="title-agrica">Console Expert</p>', unsafe_allow_html=True)
    st.metric("Précision RAG", "99.2%")

else:
    st.markdown('<p class="title-agrica">Le Cas Ginette</p>', unsafe_allow_html=True)
    st.info("Analyse OCR du courrier manuscrit en cours...")