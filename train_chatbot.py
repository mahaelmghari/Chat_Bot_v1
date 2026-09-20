import nltk
import json
import pickle
import numpy as np
import random

from nltk.stem import WordNetLemmatizer
from sklearn.neural_network import MLPClassifier

#download ntlk 
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
 
lemmatizer = WordNetLemmatizer()

# variables
words = []
classes = []
documents = []
ignore_words = ['?', '!']

with open('data/intents.json', encoding = 'utf-8') as data_file:
    intents = json.load(data_file)

#process intents
for intent in intents['intents']:
    for pattern in intent['patterns']:

        #tokenize each word
        w = nltk.word_tokenize(pattern)
        words.extend(w)

        #add documents in the corpus
        documents.append((w, intent['tag']))

        #add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#lemmatize and lower each word and remove duplicates
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

#sort classes
classes = sorted(list(set(classes)))

#documents = combination between patterns and intents (display info)
print(len(documents), 'documents')
print(len(classes), 'classes', classes)
print(len(words), 'unique lemmatized words', words)

# create training data
train_x = []
train_y = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    #create bag of words
    for w in words:
        bag.append(1 if w in pattern_words else 0)
    
    train_x.append(bag)
    train_y.append(classes.index(doc[1]))   

#shuffle together 
combined = list(zip(train_x, train_y))
random.shuffle(combined)
train_x, train_y = zip(*combined)

train_x = np.array(train_x)
train_y = np.array(train_y)

print('Training data created')

#model creation - 3 layers, 128 neurons, 64 neurons, output layer = number of intents (softmax)
model = MLPClassifier(
    hidden_layer_sizes = (128, 64),
    activation = 'relu',
    solver = 'sgd',
    learning_rate_init = 0.01,
    momentum = 0.9,
    max_iter = 500,
    batch_size = 5,
    random_state = 42
)

#training
print('Training model...')
model.fit(train_x, train_y)
print('Training completed')

accuracy = model.score(train_x, train_y)
print(f'Training accuracy: {accuracy * 100:2f}%')

#save model, words and classes
with open('data/chatbot_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
print('Saved model to: data/chatbot_model.pkl')

with open('data/words.pkl', 'wb') as words_file: 
    pickle.dump(words, words_file)
print('Saved words to: data/words.pkl')

with open('data/classes.pkl', 'wb') as classes_file: 
    pickle.dump(classes, classes_file)
print('Saved classes to: data/classes.pkl')

print('Model created successfully.')