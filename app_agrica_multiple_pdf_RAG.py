import streamlit as st
import ollama
import os
import json
import base64
import time
from gtts import gTTS
from io import BytesIO
from streamlit_mic_recorder import speech_to_text

# Bibliothèques pour le RAG Professionnel
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="AGRICA - Expert RAG Pro", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');
    
    /* On cible les textes pour garder la police sans casser les icônes système */
    html, body, .stMarkdown, p, span, h1, h2, h3, label, .stButton, .stChatInputContainer {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    html, body {
        background-color: #F8FBF8 !important;
        color: #1A3C15 !important;
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-top: 5px solid #2D5A27;
    }
    
    .stChatMessage { 
        border-radius: 15px !important; 
        border: 1px solid #E0E0E0 !important;
        background-color: white !important;
        margin-bottom: 10px;
    }

    .gain-value {
        font-size: 28px;
        font-weight: 600;
        color: #2D5A27;
        background: #E8F5E9;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
            
    /* Masque le triangle natif du summary (WebKit + standard) */
    details > summary::-webkit-details-marker { display: none; }
    details > summary::marker { display: none; }

    /* garde le comportement d'expansion et un curseur clair */
    details > summary { cursor: pointer; }

    /* Masque les icônes ou texte placés avant le label de l'expander (garde le dernier enfant, le label) */
    .stExpander summary { display: flex; align-items: center; padding-left: 0 !important; }
    .stExpander summary > *:not(:last-child) { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION : ARCHITECTURE RAG PRO AVEC PERSISTANCE ---

@st.cache_resource
def initialiser_rag_professionnel():
    """Initialise le moteur RAG avec sauvegarde locale pour éviter l'attente au redémarrage."""
    index_path = "faiss_index_agrica"
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Récupération systématique des fichiers PDF présents pour l'affichage UI
    fichiers_physiques = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pdf"):
                fichiers_physiques.append(file)
    
    # Si l'index existe déjà, on le charge instantanément
    if os.path.exists(index_path):
        with st.status("🚀 Chargement de la base de données locale...", expanded=False) as status:
            vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            status.update(label="✅ Base de données chargée !", state="complete")
            return vectorstore, fichiers_physiques if fichiers_physiques else ["Documents archivés en local"]

    # Sinon, on crée l'index (c'est cette étape qui est longue la première fois)
    try:
        with st.status("🏗️ Création de la base de connaissances (Premier lancement)...", expanded=True) as status:
            st.write("📖 Lecture des fichiers PDF (cela peut prendre quelques minutes)...")
            loader = DirectoryLoader(".", glob="**/*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()
            
            if not docs:
                status.update(label="Erreur : Aucun PDF trouvé", state="error")
                return None, []

            st.write(f"✂️ Découpage de {len(docs)} pages en blocs sémantiques...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150
            )
            splits = text_splitter.split_documents(docs)

            st.write("🧠 Génération des vecteurs (Embeddings) via Ollama...")
            st.info("Note : Cette étape utilise votre CPU/GPU. Patientez environ 5-10 minutes.")
            vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
            
            st.write("💾 Sauvegarde de l'index sur le disque...")
            vectorstore.save_local(index_path)
            
            noms_fichiers = list(set([os.path.basename(doc.metadata.get('source', '')) for doc in docs if doc.metadata.get('source')]))
            status.update(label="✅ Indexation terminée et sauvegardée !", state="complete")
            
        return vectorstore, noms_fichiers
    except Exception as e:
        st.error(f"Erreur d'initialisation RAG : {e}")
        return None, []

# --- FONCTIONS MULTIMÉDIA ---

def play_audio(text):
    """Synthèse vocale avec double sécurité (autoplay HTML + lecteur visible)."""
    try:
        sound_file = BytesIO()
        tts = gTTS(text=text, lang='fr')
        tts.write_to_fp(sound_file)
        
        # On affiche le lecteur Streamlit natif (visible, utile si autoplay échoue)
        st.audio(sound_file.getvalue(), format="audio/mp3")
        
        # Tentative de lecture automatique via HTML/JS
        b64 = base64.b64encode(sound_file.getvalue()).decode()
        audio_html = f"""
            <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de la lecture audio : {e}")

def update_smiley(state_url, label=""):
    """Met à jour l'avatar du conseiller"""
    avatar_placeholder.markdown(f"""
        <div style="text-align: center; background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <img src="{state_url}" width="150" style="border-radius: 10px;">
            <p style="margin-top: 10px; font-weight: 600; color: #2D5A27;">{label}</p>
        </div>
        """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1998/1998614.png"

STATE_SOURIT = get_b64("sourit.png")
STATE_REFLEXION = get_b64("reflexion.png")
STATE_PARLE = get_b64("parle.png")

# Démarrage du moteur RAG
vector_db, liste_fichiers = initialiser_rag_professionnel()

# --- INTERFACE ---
st.image("https://www.comparateur-dependance-senior.com/wp-content/uploads/2019/05/logo-agrica.jpg", width=180)

col_side, col_chat = st.columns([1, 2.2])

with col_side:
    avatar_placeholder = st.empty()
    # État initial
    update_smiley(STATE_SOURIT, "Conseiller AGRICA")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("📊 **Tableau de bord**")
    st.markdown('<div class="gain-value">+ 420 € / an</div>', unsafe_allow_html=True)
    st.caption("Optimisation détectée.")
    st.markdown('</div>', unsafe_allow_html=True)

    if liste_fichiers:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"📂 **Base Documentaire**")
        with st.expander(f"Documents indexés ({len(liste_fichiers)})"):
            for f in sorted(liste_fichiers):
                st.write(f"📄 {os.path.basename(f)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("### 🎤 Parler à l'expert")
    vocal_text = speech_to_text(language='fr', start_prompt="Lancer l'écoute", stop_prompt="Arrêter", key='speech')

with col_chat:
    st.write("### 💬 Espace Expert Conseil")
    
    container = st.container(height=480)
    with container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="🚜" if m["role"]=="assistant" else "👤"):
                st.markdown(m["content"])

    prompt = vocal_text if vocal_text else st.chat_input("Posez votre question...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with container:
            with st.chat_message("user", avatar="👤"): 
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🚜"):
                # 1. État REFLEXION
                update_smiley(STATE_REFLEXION, "Analyse sémantique...")
                
                with st.spinner("Recherche dans la base..."):
                    if vector_db:
                        docs_pertinents = vector_db.similarity_search(prompt, k=5)
                        context = "\n\n".join([f"Source: {os.path.basename(d.metadata['source'])}\n{d.page_content}" for d in docs_pertinents])
                    else:
                        context = "Aucun document indexé."

                    full_prompt = f"""Tu es l'Expert assureur AGRICA. Réponds en utilisant ce contexte :
                    {context}
                    
                    Question : {prompt}
                    Réponse détaillée mais concise (10 phrases max). Cite impérativement la source."""
                    
                    try:
                        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': full_prompt}])
                        answer = response['message']['content']
                        
                        # 2. État PARLE
                        update_smiley(STATE_PARLE, "Je vous réponds...")
                        st.markdown(answer)
                        play_audio(answer)
                        
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                        answer = "Désolé, une erreur est survenue."
                
                # 3. Retour à l'état SOURIT après un court délai
                time.sleep(2)
                update_smiley(STATE_SOURIT, "Prêt pour la suite.")
        
        st.session_state.messages.append({"role": "assistant", "content": answer})