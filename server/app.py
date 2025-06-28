import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import requests
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

# Platform-specific limits
PLATFORM_LIMITS = {
    "linkedin": {"char_limit": 1300, "hashtag_limit": 30},
    "instagram": {"char_limit": 2200, "hashtag_limit": 30},
    "twitter": {"char_limit": 280,  "hashtag_limit": 30},
    "facebook": {"char_limit": 63206, "hashtag_limit": 30},
}

# Simple NLP-based tone classification
def classify_tone(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    return "Neutral"

# Wrapper to call the Gemini completion API
def call_gemini_api(prompt):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "max_tokens": 200}
    resp = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Adjust according to actual response schema
    return data.get("choices", [])[0].get("text", "").strip()

@app.route('/review', methods=['POST'])
def review_post():
    data = request.get_json() or {}
    text = data.get('text', '')
    platform = data.get('platform', '').lower()

    # Analyse tone
    tone = classify_tone(text)

    # Fetch platform limits
    limits = PLATFORM_LIMITS.get(platform, {})

    # Generate suggestions and revised post via Gemini
    suggestions_prompt = (
        f"Suggest improvements to clarity, tone, and engagement for this post:\n\n{text}"
    )
    revised_prompt = (
        f"Rewrite this post for clarity, tone, and engagement without changing the core message:\n\n{text}"
    )
    suggestions = call_gemini_api(suggestions_prompt)
    revised = call_gemini_api(revised_prompt)

    return jsonify({
        "tone": tone,
        "limitations": limits,
        "suggestions": suggestions,
        "revised_post": revised
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)