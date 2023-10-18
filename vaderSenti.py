import spacy
from vaderSentiment import vaderSentiment
english = spacy.load("en_core_web_sm")
result = english(input("Enter the statement: "))
sentences = [str(s) for s in result.sents]
analyzer = vaderSentiment.SentimentIntensityAnalyzer()
sentiment = [analyzer.polarity_scores(str(s)) for s in sentences]
print(sentiment[0])
print("The statement you just entered is: ")
print(sentiment[0]['pos']*100,'% positive')
print(sentiment[0]['neg']*100,'% negative')
print(sentiment[0]['neu']*100,'% neutral')

if(sentiment[0]['compound'] >= 0.05) : 
    sent="Positive" 
elif(sentiment[0]['compound'] <= - 0.05) : 
    sent="Negative" 
else :
    sent="Neutral"
print("OVERALL SENTIMENT: ",sent)