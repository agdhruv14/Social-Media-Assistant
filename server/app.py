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
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required.")
# Construct the full endpoint including the key
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.0-flash:generateContent"
    f"?key={GEMINI_API_KEY}"
)

# Platform-specific limits
PLATFORM_LIMITS = {
    "linkedin": {"char_limit": 1300, "hashtag_limit": 30},
    "instagram": {"char_limit": 2200, "hashtag_limit": 30},
    "twitter": {"char_limit": 280,  "hashtag_limit": 30},
    "facebook": {"char_limit": 63206, "hashtag_limit": 30},
}

# Simple NLP-based tone classification
def classify_tone(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    return "Neutral"

# Wrapper to call the Gemini completion API
def call_gemini_api(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}  # wrap prompt as per Gemini API quickstart
        ]
    }
    resp = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Google Generative Language API returns candidates under 'candidates'
    answer = data.get("candidates", [])[0].get("content", "")['parts'][0]['text']
    print(answer)
    return answer

@app.route('/review', methods=['POST'])
def review_post():
    req = request.get_json() or {}
    text: str = req.get('text', '')
    platform: str = req.get('platform', '').lower()

    # Analyse tone
    tone = classify_tone(text)

    # Fetch platform limits
    limits = PLATFORM_LIMITS.get(platform, {})

    # Prepare prompts
    suggestions_prompt = (
        f"Suggest improvements to clarity, tone, and engagement for this post. Make sure your answer is relatively short with a list of brief suggestions only:\n\n{text}"
    )
    suggestions = call_gemini_api(suggestions_prompt)
    
    revised_prompt = (
        f"Rewrite this post for clarity, tone, and engagement without changing the core message. The suggestions for improvement are: {suggestions}. Based on these suggestions return a revised text of similar length to the other one. Ensure your response includes only the revised text and introduction:\n\n{text}"
    )

    # Call Gemini
    
    revised = call_gemini_api(revised_prompt)

    return jsonify({
        "tone": tone,
        "limitations": limits,
        "suggestions": suggestions,
        "revised_post": revised
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)