import os
import io
import nltk
import speech_recognition as sr
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_url_path='/static', static_folder='static')

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        sentiment_scores = sia.polarity_scores(text)
        return text, sentiment_scores
    except sr.UnknownValueError:
        return None, None
    
def map_sentiment_score_to_label(sentiment_score):
    if sentiment_score >= 0.05:
        return "Happy"
    elif sentiment_score <= -0.05:
        return "Sad"
    else:
        return "Neutral"

# Define route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    sentiment_score = None
    transcribed_text = None
    sentiment_label = None
    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'})

        audio_file = request.files['audio']

        if audio_file and (audio_file.filename.endswith('.mp3') or audio_file.filename.endswith('.wav')):
            temp_audio_file = 'temp_audio' + os.path.splitext(audio_file.filename)[1]
            audio_file.save(temp_audio_file)
            transcribed_text, sentiment_scores = analyze_sentiment(temp_audio_file)

            if sentiment_scores:
                sentiment_score = sentiment_scores['compound']
                sentiment_label = map_sentiment_score_to_label(sentiment_score)

            # Delete the temporary audio file
            os.remove(temp_audio_file)

    return render_template('index.html', sentiment_score=sentiment_score, transcribed_text=transcribed_text, sentiment_label=sentiment_label)

# Define route for the Text Sentiment Analysis page
@app.route('/text.html', methods=["GET", "POST"])
def text():
    # Your route handling code here

    if request.method == "GET":
        return render_template("text.html")
    if request.method == "POST":
        st = request.form.get("review-text")
    if st == '':
        return render_template('text.html')

    sentences = [s.strip() for s in st.split('.') if s.strip()]

    analyzer = SentimentIntensityAnalyzer()

    compound_sentiment = 0.0  # Initialize compound sentiment score

    for sentence in sentences:
        sentiment = analyzer.polarity_scores(sentence)
        compound_sentiment += sentiment['compound']

    compound_sentiment /= len(sentences)  # Calculate the average compound sentiment

    if compound_sentiment >= 0.05:
        sentiment_label = "Happy"
        emoji = "😄"
        address = 'https://st.depositphotos.com/1016482/2236/i/950/depositphotos_22362437-stock-photo-background-with-heap-of-yellow.jpg'
    elif compound_sentiment <= -0.05:
        sentiment_label = "Sad"
        emoji = "😔"
        address = 'https://www.ecopetit.cat/wpic/mpic/270-2706765_sad-emoji-cover-photo-for-fb.jpg'
    else:
        sentiment_label = "Neutral"
        emoji = "😐"
        address = 'https://atlas-content-cdn.pixelsquid.com/stock-images/neutral-face-facial-expression-L63Mrq1-600.jpg'

    return render_template('output.html', sentence=st, sentiment=sentiment_label, emoji=emoji, address=address)

# Define route for the About page
@app.route('/about.html')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
