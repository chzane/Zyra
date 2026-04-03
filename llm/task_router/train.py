import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
import joblib

# 读取数据
csv = pd.read_csv("train.csv")

texts = csv["text"].tolist()
labels = csv["label"].astype(str).str.strip().tolist()

# embedding模型
embed_model = SentenceTransformer("../models/bge-base-zh-v1.5")

# 向量化
X = embed_model.encode(
    texts,
    normalize_embeddings=True,
    show_progress_bar=True
)

# 标签编码
le = LabelEncoder()
y = le.fit_transform(labels)

class_counts = pd.Series(y).value_counts()
use_stratify = class_counts.min() >= 2 and len(class_counts) > 1

if use_stratify:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
else:
    print("警告：存在样本数小于2的类别，已使用非分层切分。")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=None
    )

# LightGBM分类器
clf = MLPClassifier(
    hidden_layer_sizes=(512, 128),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42
)

clf.fit(X_train, y_train)

# 预测
pred = clf.predict(X_test)

print(classification_report(
    y_test,
    pred,
    labels=list(range(len(le.classes_))),
    target_names=le.classes_
))

# 保存
joblib.dump(clf, "router_classifier_zhcn.pkl")
joblib.dump(le, "label_encoder_zhcn.pkl")
