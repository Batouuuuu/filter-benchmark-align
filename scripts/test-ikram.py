import fasttext

model = fasttext.load_model("../data/models/lid.176.ftz")

with open("../data/aligned/spanish/fr.txt", "r", encoding="utf-8") as f:
    lines = [next(f) for _ in range(5)]  # teste 5 lignes

for line in lines:
    label, prob = model.predict(line.strip())
    print(f"{line.strip()} → {label[0]} (prob: {prob[0]:.2f})")
