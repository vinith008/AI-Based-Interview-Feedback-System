from flask import Flask, render_template, request, jsonify
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
import re

app = Flask(__name__)

nltk.download('vader_lexicon')
nltk.download('punkt')
sia = SentimentIntensityAnalyzer()

saved_speeches = []  # Store all past speeches with timestamps

def evaluate_response(text):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    sentiment_score = sia.polarity_scores(text)["compound"]
    sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"

    fluency = len(words) / max(len(sentences), 1)
    vocabulary = len(set(words)) / max(len(words), 1)
    confidence = min(100, fluency * 10 + sentiment_score * 20 + vocabulary * 50)

    # Detecting hesitations and filler words
    filler_words = ["um", "uh", "like", "you know", "ah", "hmm"]
    hesitation_count = sum(text.lower().count(fw) for fw in filler_words)
    
    # Detecting repeated words
    word_freq = nltk.FreqDist(words)
    repeated_words = [word for word, freq in word_freq.items() if freq > 2]
    
    # Detecting grammatical issues (basic pattern matching for common errors)
    grammar_issues = []
    if re.search(r"\b(i)\b", text):
        grammar_issues.append("'I' should be capitalized")
    if re.search(r"\bi amn't\b", text):
        grammar_issues.append("Incorrect contraction 'amn't'. Use 'I'm not'")
    
    suggestions = []
    if fluency > 20:
        suggestions.append("Try using shorter sentences for clarity.")
    if vocabulary < 0.5:
        suggestions.append("Expand your vocabulary for better impact.")
    if hesitation_count > 3:
        suggestions.append("Try reducing filler words like 'um' and 'ah' for more clarity.")

    return {
        "sentiment": sentiment,
        "fluency": round(fluency, 2),
        "vocabulary": round(vocabulary, 2),
        "confidence": round(confidence, 2),
        "repeated_words": repeated_words,
        "hesitations": hesitation_count,
        "grammar_issues": grammar_issues,
        "suggestions": suggestions
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return render_template("history.html", speeches=saved_speeches)

@app.route("/process_speech", methods=["POST"])
def process_speech():
    data = request.get_json()
    text = data.get("text", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if text:
        evaluation = evaluate_response(text)
        saved_speeches.append({"time": timestamp, "text": text})  # Store speech with timestamp

        return jsonify({
            "transcribed_text": text,
            "evaluation": evaluation
        })
    return jsonify({"error": "No speech detected."})

if __name__ == "__main__":
    app.run(debug=True)