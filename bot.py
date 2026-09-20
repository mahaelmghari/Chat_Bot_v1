import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import json
import random

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

#load trained model, intents, words and classes
with open('./data/chatbot_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)


with open('./data/intents.json', encoding = 'utf-8') as file:
    intents = json.load(file)

with open('./data/words.pkl', 'rb') as words:
    words = pickle.load(file)

with open('./data/classes.pkl', 'rb') as classes:
    classes = pickle.load(file)

#clean up
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

#bag of words
def bow(sentence, words, show_details = False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  

    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words, show_details = False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse = True)
    return_list = []

    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints, intents_json):
    if not ints:
        return "Sorry, I don't understand."
    
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
        break
    return "Sorry, I don't understand."

def chatbot_response(text):
    ints = predict_class(text, model)
    res = get_response(ints, intents)
    return res
