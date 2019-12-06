'''
Created on 29 oct. 2019
Ce module contient le réseau de neurones créé avec TensorFlow (pour la classification)
@author: Anas Neumann <anas.neumann.isamm@gmail.com>
'''
# -*-coding:Utf-8 -*
import tensorflow as tf

EPOCHS = 500

# Une fonction initiale (appelée une seule fois) pour l'initialisation de l'architecture du réseau
def initNeuralNetwork():
    model = tf.keras.Sequential([
      tf.keras.layers.Dense(11, activation=tf.nn.relu, input_shape=(11,)),
      tf.keras.layers.Dense(10, activation=tf.nn.relu),
      tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    return model

# Une fonction d'entrainement du réseau sur des données de test
def trainNeuralNetwork(model, inputs, labels):
    model.fit(inputs, labels, EPOCHS)

# Méthode principale du réseau de neurones (Classification)
def classify(inputs, model):
    return  model.predict(formatData(inputs))

# Formater les données pour tensorFlow
def formatData(inputs):
    data = list()
    data.append(inputs['categoryId'])
    data.append(inputs['pageId'])
    data.append(inputs['themeId'])
    data.append(inputs['picture'])
    data.append(inputs['nbrAnswers'])
    data.append(inputs['sizeAnswers'])
    data.append(inputs['sizeQuestion'])
    data.append(inputs['sizeSentencesQuestion'])
    data.append(inputs['sizeSentencesAnswers'])
    data.append(inputs['sizeWordsQuestion'])
    data.append(inputs['sizeWordsAnswers'])
    return data