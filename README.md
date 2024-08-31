# ETUDE DE CAS LIFEN

json
flask
export FLASK_APP=main_server.py
flask run 
running on http://127.0.0.1:5000

Je fais deux approches différentes pour extraire des informations médicales venat d'un rapport : un NER et une heuristique classique que j'ai utilisé sur un site web.
# Heuristique :

si on trouve "Monsieur", "Mr", "Madame" ou "Mme": on prend le mot suivant si le mot suivant est une majusctule, sinon les deux mots suivants
si on trouve : "Nom:" et "Prenom:"  on prend le mot suivant

si on n'a pas le Prenom et le Nom, on va au moins récuperer le nom par une autre méthode:
on récupère la liste avec tous les noms de médecins ( après Docteur ou Dr), puis on recherche tous les noms en majucule
si le nom en majucule n'est pas dans la liste des médecins, on le prend

# Précisions
"For each document we have a json representation that gives us absolute coordinates for each word"
je considère donc qu'on a deja la fonction give_json(pdf_path), qui donne le json à partir du chemin du pdf
pour l'exemple sur le site je prend dans chaque cas le json que vous avez donné sur le github.

# Problèmes :

Mais pour réussir le 1er cas par exemple : pour trouver les noms des médecins, il faudrait une liste avec tous les noms de professions médicales (autres que docteur, comme gynécologue dans l'exemple) pour rechercher le nom qui suit du medecin. 

Il reste les cas ou il y aurait écrit le prenom et le nom et sans majuscule au nom, avec le nom en dessous du prenom sans label "prenom:", "nom:". Pour cela notre heuristique atteint ses limites. Si il y a écrit "Patient:" une ligne en haut, on pourrait réussir à trouver le prenom et le nom. Sinon il n'y a pas d'heuristique simple qui puisse le faire.

De même, l'heuristique ne gère pas bien le cas ou il y a plusieurs Monsieur ou Madame dans le rapport. L'heuristique prend le premier nom et prenom qu'il trouve. Il pourrait même renvoyer prendre un prenom et un nom qui ne correspondent pas.

# Précisions
"For each document we have a json representation that gives us absolute coordinates for each word"
je considère donc qu'on a deja la fonction give_json(pdf_path), qui donne le json à partir du chemin du pdf

# Tests avec linter et formatter sur github
actions github à chaque pull request


