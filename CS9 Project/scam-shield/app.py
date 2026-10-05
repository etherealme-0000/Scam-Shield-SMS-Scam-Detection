import streamlit as st
import joblib
import re
import string
import nltk
from nltk.corpus import stopwords
import db

st.set_page_config(page_title="Scam Shield", layout="centered")

db.init_db()

@st.cache_resource
def load_stopwords():
    try:
        return set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords')
        return set(stopwords.words('english'))

STOPWORDS = load_stopwords()

@st.cache_resource
def load_model():
    model = joblib.load('scam_shield_model.pkl')
    vectorizer = joblib.load('scam_shield_vectorizer.pkl')
    return model, vectorizer

model, vectorizer = load_model()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\d+', '', text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return ' '.join(words)

st.title("Scam Shield")
st.caption("SMS Scam Detection Using Machine Learning (Naive Bayes)")

st.write(
    "Paste an SMS message below and Scam Shield will predict whether it's "
    "**legitimate** or a **scam**, using a Naive Bayes model trained on the "
    "SMS Spam Collection Dataset."
)

message = st.text_area(
    "Enter an SMS message",
    placeholder="e.g. Congratulations! You've won a free prize. Click here to claim now!",
    height=120,
)

if st.button("Check message", type="primary"):
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        cleaned = clean_text(message)
        vec = vectorizer.transform([cleaned])
        prediction = model.predict(vec)[0]
        proba = model.predict_proba(vec)[0]
        confidence = proba[prediction]
        label = "SCAM" if prediction == 1 else "LEGITIMATE"

        if prediction == 1:
            st.error(f"This message looks like a **SCAM** ({confidence:.0%} confidence)")
        else:
            st.success(f"This message looks **LEGITIMATE** ({confidence:.0%} confidence)")

        with st.expander("See prediction details"):
            st.write(f"**Cleaned text used for prediction:** {cleaned if cleaned else '(empty after cleaning)'}")
            st.write(f"**Probability — Legitimate (ham):** {proba[0]:.2%}")
            st.write(f"**Probability — Scam (spam):** {proba[1]:.2%}")

        db.save_prediction(message, label, float(confidence))

st.divider()

st.subheader("Prediction History")
total, scam_count = db.get_stats()
col1, col2 = st.columns(2)
col1.metric("Total messages checked", total)
col2.metric("Flagged as scam", scam_count)

history = db.get_all_predictions()
if history:
    with st.expander(f"View all {len(history)} past predictions"):
        for msg, pred, conf, ts in history:
            icon = "⚠️" if pred == "SCAM" else "✅"
            st.write(f"{icon} **{pred}** ({conf:.0%}) — *{msg[:80]}{'...' if len(msg) > 80 else ''}* — {ts[:19]}")
else:
    st.caption("No predictions yet — try checking a message above.")

with st.sidebar:
    st.header("About this model")
    st.write("**Algorithm:** Multinomial Naive Bayes")
    st.write("**Features:** TF-IDF with unigrams + bigrams (5,000 features)")
    st.write("**Dataset:** SMS Spam Collection Dataset (5,169 unique messages)")
    st.markdown("---")
    st.write("**Test set performance:**")
    st.metric("Accuracy", "98.1%")
    st.metric("Precision", "96.6%")
    st.metric("Recall", "87.8%")
    st.metric("F1-score", "92.0%")
    st.markdown("---")
    st.caption("Scam Shield — CCE105 Project")