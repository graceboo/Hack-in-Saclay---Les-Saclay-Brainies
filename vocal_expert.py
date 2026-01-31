import streamlit as st
import base64
import os
import time
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text
from agent import initialiser_moteur_rag, poser_question_expert

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Thomas - Agrica Live Expert", layout="wide")

# INITIALISATION DU CLIENT ELEVENLABS (Nouvelle syntaxe)
# Remplacez par votre clé API réelle
client = ElevenLabs(api_key="VOTRE_CLE_ELEVENLABS")

# --- DESIGN PREMIUM DARK & SOUVERAIN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at center, #0f172a, #020617) !important; 
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .agent-container {
        display: flex; justify-content: center; align-items: center; margin-bottom: 20px;
    }

    .avatar-glow {
        width: 300px; height: 300px;
        border-radius: 50%;
        border: 4px solid #3b82f6;
        box-shadow: 0 0 50px rgba(59, 130, 246, 0.5);
        background: url('https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400') center/cover;
    }

    .source-tag {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        padding: 8px 15px;
        border-radius: 12px;
        font-size: 0.8rem;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: inline-block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DU MOTEUR RAG ---
@st.cache_resource
def load_db():
    return initialiser_moteur_rag()

db = load_db()

# --- MOTEUR VOCAL ELEVENLABS (CORRIGÉ) ---
def generer_voix_humaine(text):
    try:
        # Utilisation de la méthode correcte pour ElevenLabs SDK v1.0+
        audio_generator = client.generate(
            text=text,
            voice="Antoni", 
            model="eleven_multilingual_v2",
            voice_settings={"stability": 0.5, "similarity_boost": 0.75}
        )
        
        # Conversion du générateur en bytes
        audio_bytes = b"".join(list(audio_generator))
        return audio_bytes
    except Exception as e:
        st.error(f"Erreur vocale : {e}")
        return None

# --- INTERFACE ---
col_avatar, col_content = st.columns([1, 1], gap="large")

with col_avatar:
    st.markdown('<div class="agent-container"><div class="avatar-glow"></div></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Thomas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Expert Agrica - Santé & Prévoyance</p>", unsafe_allow_html=True)

with col_content:
    st.markdown("<h1 style='color:#3b82f6;'>Conseiller IA Agrica</h1>", unsafe_allow_html=True)
    st.write("Posez votre question à voix haute. Je consulte vos contrats en temps réel.")
    
    # Micro recorder
    question = speech_to_text(language='fr', start_prompt="🎙️ PARLER", stop_prompt="✅ ENVOYER", key='final_vocal')

    if question:
        st.chat_message("user").write(question)
        
        with st.spinner("Analyse souveraine des documents..."):
            # Recherche RAG locale
            reponse_texte = poser_question_expert(question, db)
            
            with st.chat_message("assistant"):
                st.write(reponse_texte)
                st.markdown('<div class="source-tag">🛡️ Information certifiée Agrica - Mode Local</div>', unsafe_allow_html=True)
            
            # Génération et lecture audio
            audio_data = generer_voix_humaine(reponse_texte)
            if audio_data:
                st.audio(audio_data, format="audio/mp3", autoplay=True)