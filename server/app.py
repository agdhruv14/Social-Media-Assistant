import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required.")
gemini_url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.0-flash:generateContent"
)


PLATFORM_LIMITS = {
    "linkedin": {"char_limit": 1300, "hashtag_limit": 30},
    "instagram": {"char_limit": 2200, "hashtag_limit": 30},
    "twitter": {"char_limit": 280,  "hashtag_limit": 30},
    "facebook": {"char_limit": 63206, "hashtag_limit": 30},
}

vader_analyzer = SentimentIntensityAnalyzer()
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=False
)

def classify_tone(text: str) -> str:
    scores = vader_analyzer.polarity_scores(text)
    comp = scores['compound']
    if comp >= 0.05:
        sentiment = "Positive"
    elif comp <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"


    emo = emotion_classifier(text)[0]['label']

    contractions = re.findall(r"\b(?:'t|'re|'ve|'ll|'d|'s)\b", text)
    contraction_ratio = len(contractions) / max(len(text.split()), 1)
    style = "Informal" if contraction_ratio > 0.05 else "Formal"

    return f"Sentiment: {sentiment}; Emotion: {emo}; Style: {style}"


def call_gemini_api(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    resp = requests.post(gemini_url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    return data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "").strip()

@app.route('/review', methods=['POST'])
def review_post():
    req = request.get_json() or {}
    text: str = req.get('text', '')
    platform: str = req.get('platform', '').lower()

    tone = classify_tone(text)

    limits = PLATFORM_LIMITS.get(platform, {})

    suggestions_prompt = (
        f"Provide 3 concise suggestions to improve clarity, tone, and engagement for the following post. "
        "List each suggestion on its own line, prefixed by a number. "
        "Respond in plain text only; do not include any Markdown or extra commentary.\n\n" + text
    )
    suggestions = call_gemini_api(suggestions_prompt)

    revised_prompt = (
        f"Rewrite the post using the suggestions above to enhance clarity, tone, and engagement. "
        "Return only the revised text in plain text, with no headings, lists, or additional commentary. "
        "Maintain a length similar to the original. The post must be revised based on the following suggestions:\n {suggestions}\n\n" + text
    )
    revised = call_gemini_api(revised_prompt)


    return jsonify({
        "tone": tone,
        "limitations": limits,
        "suggestions": suggestions,
        "revised_post": revised
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)