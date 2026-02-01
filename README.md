Voilà l'essentiel de notre code que nous avons produit lors de ce Hackhathon. 

Pour faire tourner les codes de RAG, il faut mettre les dossiers CCN52, CCPMA santé ODA et Régime d'adhésion dans le dossier de racine du projet. 

Il faut également un environnement virtuel avec les librairies utilisés. En particulier, il faut avoir téléchargé Ollama puis Mistral AI en local sur son ordinateur. 

Les fichiers clés sont: 

expert_new.py (relié à agent.py qui fait le RAG, agent.py est le fichier à lancer pour avoir l'interface)
app_agrica_multiple_pdf_RAG_py


Ils utilisent mistral AI local qui fait du RAG avec les pdf mis à disposition pour répondre aux questions de l'utilisateur, à l'oral comme à l'écrit. Il y a quelque varriation d'interface mais l'idée est similaire.

Enfin, nous avons un fichier qui simule l'interface (sans chatbot fonctionnel):
hackaton.html


