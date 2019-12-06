'''
Created on 29 oct. 2019
Ce module contient les différents webservices REST permettant d'interagir avec ce moteur à partir de l'application mobile, du site web (ou d'un autre client)
@author: Anas Neumann <anas.neumann.isamm@gmail.com>
'''
# -*-coding:Utf-8 -*
from flask import Flask, request
from DAO import FlashCard, flashcards, pages, Page, categories, Category, Answer, users, historic
from Engine import loadcards, initialTheme, initialCardLevel, reloadLevelAndComplexity, getElt, getHistoric, getLevels
from flask.json import jsonify

# Création d'une application back REST avec Flask
app = Flask(__name__)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX UTILISATEURS
------------------------------------------------------------------------'''

# Afficher le leaderboard des utilisateurs classés par level puis rank dans chaque level
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    return jsonify([r.serialize() for r in getLevels(False, True)])

# Connexion d'un utilisateur
@app.route('/login', methods=['POST'])
def login():
    c = request.json
    for user in users:
        if user.mail == c['mail'] and user.password == c['password']:
            return jsonify(200)
    return jsonify(401)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX CARTES
------------------------------------------------------------------------'''

# Afficher l'ensemble des flashcards
@app.route('/flashcard', methods=['GET'])
def getAllCards():
    return jsonify([f.serialize() for f in flashcards])

# Ajouter une nouvelle flashcard
@app.route('/flashcard', methods=['POST'])
def addCard():
    c = request.json
    cardId = 1
    if  len(flashcards) > 0 and isinstance(flashcards[len(flashcards)-1], FlashCard) :
        cardId += flashcards[len(flashcards)-1].id
    newCard = FlashCard(c['question'], -1, c['picture'], [], [], cardId, -1, c['pageId'], 0)
    for answer in c['answers']:
        answerId = 1
        if  len(newCard.answers) > 0:
            answerId += newCard.answers[len(newCard.answers)-1].id
        newCard.answers.append(Answer(answer['content'], answer['isTrue'], cardId, answerId))
    newCard.themeId = initialTheme(newCard)
    newCard.levelId = initialCardLevel(newCard)
    flashcards.append(newCard)
    return jsonify(cardId)

# Ajouter une nouvelle flashcard
@app.route('/flashcard/<card_id>', methods=['DELETE'])
def deleteCard(card_id):
    for f in flashcards:
        if isinstance(f, FlashCard) and f.id == int(card_id):
            flashcards.remove(f)
    return jsonify(200)

# Modifier la question d'une flashcard
@app.route('/flashcard/<card_id>', methods=['PUT'])
def updateCard(card_id):
    c = request.json
    for f in flashcards:
        if isinstance(f, FlashCard) and f.id == int(card_id):
            flashcards.append(FlashCard(c['question'], c['levelId'], c['picture'], f['answers'], f['historic'], card_id, f['themeId'], f['pageId'], f['complexity']))
            flashcards.remove(f)
    return jsonify(200)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX REPONSES
------------------------------------------------------------------------'''

# Ajouter une réponse à une flashcard
@app.route('/answer/<card_id>', methods=['POST'])
def addAnswer(card_id):
    c = request.json
    for f in flashcards:
        if isinstance(f, FlashCard) and f.id == int(card_id):
            answerId = 1
            if  len(f.answers) > 0 and isinstance(f.answers[len(f.answers)-1], Answer) :
                answerId += f.answers[len(f.answers)-1].id
            f.answers.append(Answer(c['content'], c['isTrue'], card_id, answerId))
    return jsonify(answerId)

# Supprimer l'une des réponses d'une flashcard
@app.route('/answer/<card_id>/<answer_id>', methods=['DELETE'])
def deleteAnswer(card_id, answer_id):
    for f in flashcards:
        if isinstance(f, FlashCard) and f.id == int(card_id):
            for a in f.answers:
                if isinstance(a, Answer) and a.id == int(answer_id):
                    f.answers.remove(a)
    return jsonify(200)

# Modifier la réponse d'une flashcard
@app.route('/answer/<card_id>/<answer_id>', methods=['PUT'])
def updateAnswer(card_id, answer_id):
    c = request.json
    for f in flashcards:
        if isinstance(f, FlashCard) and f.id == int(card_id):
            for a in f.answers:
                if isinstance(a, Answer) and a.id == int(answer_id):
                    f.answers.append(Answer(c['content'], c['isTrue'], card_id, answer_id))
                    f.answers.remove(a)
    return jsonify(200)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX PAGES
------------------------------------------------------------------------'''

# Afficher l'ensemble des pages
@app.route('/page', methods=['GET'])
def getAllPages():
    return jsonify([p.serialize() for p in pages])

# Récuperer une nouvelle page de la base de données de Wikimédica
@app.route('/page', methods=['POST'])
def addPage():
    c = request.json
    pages.append(Page(c['title'], c['pageId'], [], c['catId']))
    return jsonify(int(c['pageId']))

# Une page a été supprimée de la base de données de Wikimédica
@app.route('/page/<page_id>', methods=['DELETE'])
def deletePage(page_id):
    for p in pages:
        if isinstance(p, Page) and p.id == int(page_id):
            pages.remove(p)
    return jsonify(200)

# Une page a été modifiée dans la base de données de Wikimédica
@app.route('/page/<page_id>', methods=['PUT'])
def updatePage(page_id):
    c = request.json
    for p in pages:
        if isinstance(p, Page) and p.id == int(page_id):
            pages.append(Page(c['title'], c['pageId'], p.themes, c['catId']))
            pages.remove(p)
    return jsonify(200)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX CATEGORIES
------------------------------------------------------------------------'''

# Afficher l'ensemble des categorys
@app.route('/category', methods=['GET'])
def getAllCategories():
    return jsonify([c.serialize() for c in categories])

# Récuperer une nouvelle catégorie de la base de données de Wikimédica
@app.route('/category', methods=['POST'])
def addCategory():
    c = request.json
    categories.append(Category(c['name'], c['page'], c['catId']))
    return jsonify(int(c['categoryId']))

# Une catégorie a été supprimée de la base de données de Wikimédica
@app.route('/category/<category_id>', methods=['DELETE'])
def deleteCategory(category_id):
    for elt in categories:
        if isinstance(elt, Category) and elt.id == int(category_id):
            categories.remove(elt)
    return jsonify(200)

# Une catégorie a été modifiée dans la base de données de Wikimédica
@app.route('/category/<category_id>', methods=['PUT'])
def updateCategory(category_id):
    c = request.json
    for elt in categories:
        if isinstance(elt, Category) and elt.id == int(category_id):
            categories.append(Category(c['name'], c['page'], c['catId']))
            categories.remove(elt)
    return jsonify(200)

'''------------------------------------------------------------------------
WEBSERVICES RELATIFS AUX ESSAIS DE JEU
------------------------------------------------------------------------'''

# Récuperer un nouveau paquet de carte à partir d'une page
@app.route('/pile/<user_id>/<page_id>', methods=['GET'])
def loadPile(user_id, page_id):
    pile = list()
    u = getElt(int(user_id), users)
    if u != None:
        pile = loadcards(u, int(page_id))
    return jsonify([p.serialize() for p in pile])

# Refuser une carte
@app.route('/cancel/<user_id>/<card_id>', methods=['POST'])
def cancel(user_id, card_id):
    h = getHistoric(int(user_id), int(card_id))
    historic.remove(h)
    h.views +=1
    historic.append(h)
    return jsonify(200)

# Répondre à la question d'une carte
@app.route('/play/<user_id>/<card_id>', methods=['POST'])
def play(user_id, card_id):
    u = getElt(int(user_id), users)
    c = getElt(int(card_id), flashcards)
    h = getHistoric(int(user_id), int(card_id)) 
    user_answers = request.json['answers']
    error = list()
    if u != None and c != None:
        for answer in user_answers:
            for a in c.answers:
                if a.id == answer.id and a.isTrue is False:
                    error.append(a)
        historic.remove(h)
        h.views +=1
        if len(error) > 0:
            h.echec +=1
        else:
            h.success +=1
        historic.append(h)
        if request.json['reload'] == "true":
            newCardInformations = reloadLevelAndComplexity(c, False)
            newUserInformations = reloadLevelAndComplexity(u, True)
            c.level = newCardInformations.level
            c.complexity = newCardInformations.complexity
            u.level = newUserInformations.level
            u.complexity = newUserInformations.complexity
    return jsonify([e.serialize() for e in error])