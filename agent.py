from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# 1. Ingestion des PDF
def initialiser_moteur_rag():
    print("Analyse des PDF d'Agrica...")
    loader = PyPDFDirectoryLoader("./Corpus_Offres-Produits_AGRICA/", glob="**/*.pdf")
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory="./db_agrica"
    )
    return vector_db

# 2. Fonction de réponse
def poser_question_expert(query, vector_db):
    docs_pertinents = vector_db.similarity_search(query, k=3)
    contexte = "\n\n".join([doc.page_content for doc in docs_pertinents])
    
    llm = Ollama(model="mistral")
    
    prompt = f"""Tu es l'Expert Agrica. Réponds à la question en utilisant UNIQUEMENT le contexte suivant. 
    Si tu ne trouves pas, propose de parler à un conseiller.
    
    CONTEXTE: {contexte}
    QUESTION: {query}"""
    
    return llm.invoke(prompt)

# 3. Lancement
if __name__ == "__main__":
    db = initialiser_moteur_rag()
    print("Base Agrica prête !")
    while True:
        user_q = input("\nPosez votre question (ou 'quit') : ")
        if user_q.lower() == 'quit': break
        reponse = poser_question_expert(user_q, db)
        print(f"\nEXPERT AGRICA : {reponse}")