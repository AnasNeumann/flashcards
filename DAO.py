'''
Created on 29 oct. 2019
Ce module contient les classes de données du projet ainsi qu'une simulation de la base par des listes
@author: Anas Neumann <anas.neumann.isamm@gmail.com>
'''

# -*-coding:Utf-8 -*
import hashlib

# Une catégorie de pages
class Category:
    def __init__(self, name, pages=[], catId=-1):
        self.id = catId
        self.name = name
        self.pages = pages   

    def serialize(self):
        pagesJson = list()
        for p in self.pages:
            pagesJson.append(p.serialize())
        return {
            'id': self.id, 
            'name': self.name,
            'pages': pagesJson
        }

    def __eq__(self, other):
        return self.id == other.id

# Une page de l'application Wikimédica
class Page:
    def __init__(self, title, pageId=-1, themes=[], catId=-1):
        self.id = pageId
        self.title = title
        self.catId = catId
        self.themes = themes

    def serialize(self):
        themesJson = list()
        for t in self.themes:
            themesJson.append(t.serialize())
        return {
            'id': self.id, 
            'title': self.title,
            'catId' : self.catId,
            'themes': themesJson
        }

    def __eq__(self, other):
        return self.id == other.id
    
# Un des thèmes abordés dans une page
class Theme:
    def __init__(self, name, themeId=-1, cards=[], keywords={}, pageId=-1):
        self.id = themeId
        self.name = name
        self.keywords = keywords
        self.pageId = pageId
        self.cards = cards

    def serialize(self):
        cardsJson = list()
        for c in self.cards:
            cardsJson.append(c.serialize())
        return {
            'id': self.id, 
            'name': self.name,
            'pageId' : self.pageId,
            'keywords': self.keywords,
            'cards': cardsJson,
        }

    def __eq__(self, other):
        return self.id == other.id

# Un niveau de difficulté (pour les cartes et les utilisateurs)
class Level:
    def __init__(self, name, rank, levelId=-1):
        self.id = levelId
        self.name = name
        self.rank = rank
        self.users = []
        self.cards = []

    def serialize(self):
        usersJson = list()
        cardsJson = list()
        for u in self.users:
            usersJson.append(u.serialize())
        for c in self.cards:
            cardsJson.append(c.serialize())
        return {
            'id': self.id, 
            'name': self.name,
            'rank' : self.rank,
            'users': usersJson,
            'cards': cardsJson,
        }

    def __eq__(self, other):
        return self.id == other.id

# Un utilisateur de l'application (avec chiffrage du mot de passe)
class User: 
    def __init__(self, name, password, userId=-1, complexity=-1, levelId=-1, isTeacher=False):
        self.id = userId
        self.name = name
        self.password = hashlib.sha1(password.encode()).hexdigest() 
        self.complexity = complexity
        self.levelId = levelId
        self.isTeacher = isTeacher

    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'password' : self.password,
            'complexity' : self.complexity,
            'levelId' : self.levelId,
            'isTeacher' : self.isTeacher
        }

    def __eq__(self, other):
        return self.id == other.id

# Une carte question
class FlashCard:
    def __init__(self, question, levelId=-1, picture="", answers=[], cardId=-1, themeId=-1, pageId=-1, complexity=0):
        self.id = cardId
        self.question = question
        self.levelId = levelId
        self.answers = answers
        self.complexity = complexity
        self.picture = picture
        self.themeId = themeId
        self.pageId = pageId 
    
    def serialize(self):
        answersJson = list()
        for a in self.answers:
            answersJson.append(a.serialize()) 
        return {
            'id': self.id, 
            'question': self.question,
            'picture' : self.picture,
            'levelId' : self.levelId,
            'complexity' : self.complexity,
            'themeId' : self.themeId,
            'pageId' : self.pageId,
            'answers' : answersJson
        }

    def __eq__(self, other):
        return self.id == other.id

# Une réponse d'une carte
class Answer:
    def __init__(self, content, isTrue=False, cardId=-1, answerId=-1):
        self.id = answerId
        self.cardId = cardId
        self.isTrue = isTrue
        self.content = content

    def serialize(self):
        return {
            'id': self.id, 
            'isTrue': self.isTrue,
            'content' : self.content,
            'cardId' : self.cardId
        }

    def __eq__(self, other):
        return self.id == other.id

# L'historique entre en carte et un utilisateur
class History: 
    def __init__(self, cardId=-1, userId=-1, views=0, success=0, echec=0):
        self.id = (userId, cardId)
        self.cardId = cardId
        self.userId = userId
        self.views = views
        self.echec = echec
        self.success = success

    def serialize(self):
        return {
            'id': self.id, 
            'userId': self.userId,
            'views' : self.views,
            'cardId' : self.cardId,
            'echec' : self.echec,
            'success' : self.success
        }

    def __eq__(self, other):
        return self.id == other.id

'''------------------------------------------------------------------------
SIMULATION D'UNE BASE DE DONNEES (en utilisant des listes)
------------------------------------------------------------------------'''

# Definition de listes pour contenir l'ensemble des objets
flashcards=list()
users=list()
themes=list()
pages=list()
categories=list()
levels=list()
historic = list()

# Création des 10 niveaux de difficulté
levels.append(Level("Vraiment trop nul", 1, 1))
levels.append(Level("Débutant", 2, 2))
levels.append(Level("Facile", 3, 3))
levels.append(Level("Intermédiaire", 4, 4))
levels.append(Level("Avancé", 5, 5))
levels.append(Level("Difficile", 6, 6))
levels.append(Level("Hasardeux", 7, 7))
levels.append(Level("NP-complet", 8, 8))
levels.append(Level("Mission Impossible 007", 9, 9))
levels.append(Level("PHD", 10, 10))

# Création d'utilisateurs fictifs
users.append(User("Anas", "password", 1, 1, 10, True))
users.append(User("Jean", "password", 2, 1, 8, False))
users.append(User("Pierre", "password", 3, 2, 8, True))