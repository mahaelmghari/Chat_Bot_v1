import nltk
import json
import pickle
import numpy as np

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD

import random

#download ntlk 
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
 
lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ['?', '!']

with open('intents.json') as data_file:
    intents = json.load(data_file)

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

#documents = combination between patterns and intents
print(len(documents), 'documents')
print(len(classes), 'classes', classes)
print(len(words), 'unique lemmatized words', words)

# create training datat
train_x = []
train_y = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    for w in words:
        bag.append(1 if w in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    train_x.append(bag)
    train_y.append(output_row)

#shuffle together 
combined = list(zip(train_x, train_y))
random.shuffle(combined)
train_x, train_y = zip(*combined)

train_x = np.array(train_x)
train_y = np.array(train_y)

print('Training data created')

#model creation - 3 layers, 128 neurons, 64 neurons, output layer = number of intents (softmax)
model = Sequential()
model.add(Dense(128, input_shape = (len(train_x[0]),), activation = 'relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation = 'relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation = 'softmax'))

#compile model
sgd = SGD(learning_rate = 0.01, decay = 1e-6, momentum = 0.9, nesterov = True)
model.compile(loss = 'categorical_crossentropy', optimizer = sgd, metrics = ['accuracy'])

#training
hist = model.fit(train_x, train_y, epochs = 200, batch_size = 5, verbose = 1)

model.save('.data/chatbot_model.keras')

print('model created')