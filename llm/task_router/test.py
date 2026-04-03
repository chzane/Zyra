import joblib
from sentence_transformers import SentenceTransformer

clf = joblib.load("router_classifier_zhcn.pkl")
le = joblib.load("label_encoder_zhcn.pkl")

embed_model = SentenceTransformer("../models/bge-base-zh-v1.5")

while True:
    text = input("\n> ").strip()
    
    if text.lower() in ["exit", "quit"]:
        break
    
    emb = embed_model.encode([text], normalize_embeddings=True)

    pred = clf.predict(emb)[0]
    label = le.inverse_transform([pred])[0]

    print(label)