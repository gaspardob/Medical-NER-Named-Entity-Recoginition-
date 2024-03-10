from flask import Flask, render_template, request
import json

app = Flask(__name__)

test_json = """
{
  "pages": [
    {
      "words": [
        {"text": "hanche", "bbox": {"x_min": 0.75, "x_max": 0.81, "y_min": 0.09, "y_max": 0.1}},
        {"text": "JACQUES", "bbox": {"x_min": 0.74, "x_max": 0.83, "y_min": 0.16, "y_max": 0.17}},
        {"text": "pour", "bbox": {"x_min": 0.57, "x_max": 0.61, "y_min": 0.09, "y_max": 0.1}},
        {"text": "la", "bbox": {"x_min": 0.73, "x_max": 0.75, "y_min": 0.09, "y_max": 0.1}},
        {"text": "en", "bbox": {"x_min": 0.23, "x_max": 0.26, "y_min": 0.09, "y_max": 0.1}},
        {"text": "bien", "bbox": {"x_min": 0.15, "x_max": 0.19, "y_min": 0.09, "y_max": 0.1}},
        {"text": "consultation", "bbox": {"x_min": 0.26, "x_max": 0.36, "y_min": 0.09, "y_max": 0.1}},
        {"text": "Monsieur", "bbox": {"x_min": 0.36, "x_max": 0.44, "y_min": 0.09, "y_max": 0.1}},
        {"text": "Jean", "bbox": {"x_min": 0.44, "x_max": 0.48, "y_min": 0.09, "y_max": 0.1}},
        {"text": "à", "bbox": {"x_min": 0.72, "x_max": 0.73, "y_min": 0.09, "y_max": 0.1}},
        {"text": "droite.", "bbox": {"x_min": 0.82, "x_max": 0.87, "y_min": 0.09, "y_max": 0.1}},
        {"text": "revu", "bbox": {"x_min": 0.19, "x_max": 0.23, "y_min": 0.09, "y_max": 0.1}},
        {"text": "DUPONT", "bbox": {"x_min": 0.49, "x_max": 0.57, "y_min": 0.09, "y_max": 0.1}},
        {"text": "douleur", "bbox": {"x_min": 0.65, "x_max": 0.71, "y_min": 0.09, "y_max": 0.1}},
        {"text": "J’ai", "bbox": {"x_min": 0.12, "x_max": 0.15, "y_min": 0.09, "y_max": 0.1}},
        {"text": "une", "bbox": {"x_min": 0.61, "x_max": 0.65, "y_min": 0.09, "y_max": 0.1}},
        {"text": "Nicolas", "bbox": {"x_min": 0.67, "x_max": 0.73, "y_min": 0.16, "y_max": 0.17}},
        {"text": "Docteur", "bbox": {"x_min": 0.6, "x_max": 0.67, "y_min": 0.16, "y_max": 0.17}}
      ]
    }
  ],
  "original_page_count": 1,
  "needs_ocr_case": "no_ocr"
}
"""


def give_json(pdf_path):
    # ... "For each document we have a json representation that gives us absolute coordinates for each word"
    # je considère qu'on a deja cette fonction qui donne le json à partir du chemin du pdf
    return test_json


def give_text(json_data):  # renvoie le texte dans une liste dans l'odre de lecture
    data = json.loads(json_data)
    all_texts = []
    for word in data["pages"][0]["words"]:
        all_texts.append(word)  # on récupere les mots du texte (text + position)

    # Tri des mots par ordre de lecture en utilisant les coordonnées x et y
    for i in range(1, len(all_texts)):
        current_word = all_texts[i]
        current_box = current_word["bbox"]
        j = i - 1
        while j >= 0 and (
            current_box["y_min"] < all_texts[j]["bbox"]["y_min"]
            or (
                current_box["y_min"] == all_texts[j]["bbox"]["y_min"]
                and current_box["x_min"] < all_texts[j]["bbox"]["x_min"]
            )
        ):
            all_texts[j + 1] = all_texts[j]
            j -= 1
        all_texts[j + 1] = current_word

    text = []
    for word in all_texts:
        text.append(word["text"])
    return text


def extract_name(text):  # TROUVONS LE PRENOM ET LE NOM DU PATIENT
    nombre_mots = len(text)
    prenom = []
    nom = []

    for i in range(nombre_mots):
        if (
            text[i] == "Monsieur"
            or text[i] == "Mr"
            or text[i] == "Madame"
            or text[i] == "Mme"
        ):
            if text[i + 1].isupper():  # si c'est une majuscule, on a juste le NOM
                nom.append(text[i + 1])
            else:
                prenom.append(text[i + 1])
                nom.append(text[i + 2])
        if text[i] == "Nom:":
            nom.append(text[i + 1])
        if text[i] == "Prénom":
            prenom.append(text[i + 1])

    if (
        len(prenom) == 0 and len(nom) == 0
    ):  # si on n'a pas le prenom et le nom du patient, on va au moins récuperer son nom (si il est présent en majuscule dans le texte)
        for i in range(nombre_mots):
            prenoms_docteurs = []
            noms_docteur = []
            if text[i] == "Docteur" or text[i] == "Dr":
                if text[i + 1].isupper():
                    nom.append(text[i + 1])
                else:
                    prenoms_docteurs.append(text[i + 1])
                    noms_docteur.append(text[i + 2])
        for j in range(nombre_mots):
            if (
                text[j].isupper() and text[j] not in noms_docteur
            ):  # si le nom en majuscule n'est pas un nom de docteur
                nom.append(text[j])
    return prenom[0], nom[0]  # ou return prenom[-1], nom[-1]


@app.route("/", methods=["GET", "POST"])
def index():
    prenom = None
    nom = None

    if request.method == "POST":
        pdf_file = request.files["pdf_file"]
        pdf_path = "rapport.pdf"
        pdf_file.save(pdf_path)
        json_data = give_json(pdf_path)
        text = give_text(json_data)
        prenom, nom = extract_name(text)

    return render_template("lifen.html", prenom=prenom, nom=nom)


if __name__ == "__main__":
    app.run(debug=True)
