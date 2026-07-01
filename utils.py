import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from textblob import TextBlob

# ── Paths — adjust if your pkl files are elsewhere ───────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
DATA_PATH = os.path.join(BASE_DIR, "fake reviews dataset.csv")

@st.cache_resource
def load_model():
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.rename(columns={'text_': 'text'}, inplace=True)
    df.drop_duplicates(inplace=True)
    df['category_clean'] = df['category'].str.replace(r'_\d+$', '', regex=True).str.replace('_', ' ')
    df['is_fake'] = (df['label'] == 'CG').astype(int)
    df['purchase_proxy'] = (df['rating'] >= 4).astype(int)
    df['sentiment'] = df['text'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    return df

@st.cache_data
def load_data_with_scores():
    try:
        df = load_data()
        model, vectorizer = load_model()

        X = vectorizer.transform(df['text'])
        proba = model.predict_proba(X)

        df['prob_fake'] = proba[:, 0]
        df['prob_real'] = proba[:, 1]
        df['model_label'] = model.predict(X)
        df['model_confidence'] = df[['prob_fake', 'prob_real']].max(axis=1)
        df['model_agrees'] = (df['model_label'] == df['is_fake']).astype(int)

        return df

    except Exception as e:
        st.error(f"🚨 MODEL ERROR: {e}")
        return pd.DataFrame()


@st.cache_data
def get_category_stats():
    df = load_data_with_scores()
    def weighted_inflation(group):
        fake = group[group['prob_fake'] > 0.5]
        real = group[group['prob_real'] > 0.5]
        if len(fake) == 0 or len(real) == 0:
            return np.nan
        return (
            np.average(fake['rating'], weights=fake['prob_fake']) -
            np.average(real['rating'], weights=real['prob_real'])
        )

    stats = df.groupby('category_clean').apply(lambda g: pd.Series({
        'total_reviews':             len(g),
        'fake_count':                (g['model_label'] == 0).sum(),
        'fake_ratio':                (g['model_label'] == 0).mean(),
        'avg_rating_all':            g['rating'].mean(),
        'avg_rating_fake':           g.loc[g['model_label']==0, 'rating'].mean(),
        'avg_rating_real':           g.loc[g['model_label']==1, 'rating'].mean(),
        'avg_confidence_fake':       g.loc[g['model_label']==0, 'model_confidence'].mean(),
        'avg_confidence_real':       g.loc[g['model_label']==1, 'model_confidence'].mean(),
        'weighted_rating_inflation': weighted_inflation(g),
        'purchase_rate':             g['purchase_proxy'].mean(),
        'avg_sentiment_fake':        g.loc[g['model_label']==0, 'sentiment'].mean(),
        'avg_sentiment_real':        g.loc[g['model_label']==1, 'sentiment'].mean(),
        'sneaky_fakes':              ((g['is_fake']==1) & (g['model_label']==1)).sum(),
    })).reset_index()

    stats['rating_inflation'] = stats['avg_rating_fake'] - stats['avg_rating_real']
    stats['trust_erosion'] = (
        stats['fake_ratio'] * 0.5 +
        (stats['weighted_rating_inflation'].clip(0) / 5) * 0.3 +
        stats['avg_confidence_fake'].fillna(0) * 0.2
    ).round(3)

    return stats

def predict_single(text: str):
    model, vectorizer = load_model()
    X = vectorizer.transform([text])
    proba = model.predict_proba(X)[0]
    pred  = model.predict(X)[0]
    sentiment = TextBlob(text).sentiment.polarity
    return {
        'prob_fake':   float(proba[0]),
        'prob_real':   float(proba[1]),
        'prediction':  'fake' if pred == 0 else 'real',
        'confidence':  float(max(proba)),
        'sentiment':   sentiment,
        'word_count':  len(text.split()),
    }
