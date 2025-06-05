import fasttext

# Chargement du modèle FastText
model = fasttext.load_model("../data/models/lid.176.ftz")

# Lecture des fichiers alignés
with open("../data/aligned/spanish/fr.txt", "r", encoding="utf-8") as fr_file, \
     open("../data/aligned/spanish/es.txt", "r", encoding="utf-8") as es_file:

    print("\n--- Vérification des prédictions FastText pour les 50 premières paires ---\n")

    for i in range(50):
        fr_line = fr_file.readline().strip()
        es_line = es_file.readline().strip()

        fr_label, fr_prob = model.predict(fr_line)
        es_label, es_prob = model.predict(es_line)

        print(f"[{i+1}]")
        print(f"FR: {fr_line}")
        print(f"→ détecté : {fr_label[0]} (probabilité : {fr_prob[0]:.2f})")
        print(f"ES: {es_line}")
        print(f"→ détecté : {es_label[0]} (probabilité : {es_prob[0]:.2f})")
        print("-" * 80)
