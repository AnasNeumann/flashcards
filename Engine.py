'''
Created on 29 oct. 2019
Ce module contient les différents traitements metiers (sauf le réseau de neurones auquel ce module fait appel) 
@author: Anas Neumann <anas.neumann.isamm@gmail.com>
'''
# -*-coding:Utf-8 -*
from DAO import themes, users, flashcards, pages, levels, History, historic
from NeuralNetwork import classify
import random

# Réglages des formules mathématiques
ALPHA = 10
BETA = 5
GAMMA = 1
PILE_SIZE = 50

'''------------------------------------------------------------------------
ETAPE "EN COURS" : RECUPERATION DES CARTES ET CHANGEMENT DES NIVEAUX
------------------------------------------------------------------------'''

# Charger le prochain paquet de cartes à répondre en fonction de l'utilisateur et de la page en cours
def loadcards(user, pageId):
    pageCat = getElt(pageId, pages).catId
    result = list()

    #1. Combler en respectant les proportions
    samePage = 0.7 * PILE_SIZE
    otherPageSameCategory = 0.2 * PILE_SIZE
    otherPageOtherCategory = 0.1 * PILE_SIZE
    sameLevel = 0.8 * PILE_SIZE
    levelPlusOne = 0.1 * PILE_SIZE
    levelMinusOne = 0.1 * PILE_SIZE
    for c in orderCards(flashcards, user.id): 
        if c['card'].pageId == pageId and samePage > 0:
            if c['card'].levelId == (user.levelId + 1) and levelPlusOne > 0:
                result.append( c['card'])
                levelPlusOne -= 1
            elif c['card'].levelId == (user.levelId - 1) and levelMinusOne > 0:
                result.append( c['card'])
                levelMinusOne -= 1
            elif sameLevel>0: 
                result.append( c['card'])
                sameLevel -=1
            samePage -= 1
        else :
            if getElt(pageId, pages).catId == pageCat and otherPageSameCategory >0:
                if c['card'].levelId == (user.levelId + 1) and levelPlusOne > 0:
                    result.append( c['card'])
                    levelPlusOne -= 1
                elif c['card'].levelId == (user.levelId - 1) and levelMinusOne > 0:
                    result.append( c['card'])
                    levelMinusOne -= 1
                elif sameLevel>0: 
                    result.append( c['card'])
                    sameLevel -=1
                otherPageSameCategory -= 1
            elif otherPageOtherCategory >0:
                if c['card'].levelId == (user.levelId + 1) and levelPlusOne > 0:
                    result.append( c['card'])
                    levelPlusOne -= 1
                elif c['card'].levelId == (user.levelId - 1) and levelMinusOne > 0:
                    result.append( c['card'])
                    levelMinusOne -= 1
                elif sameLevel >0: 
                    result.append( c['card'])
                    sameLevel -=1
                otherPageOtherCategory -= 1
                
    #2. Combler aléatoirement s'il y a encore des catégories vides (manque de cartes)
    for c in flashcards:
        if len(result) >= PILE_SIZE:
            break
        else:
            result.append(c)
    
    #3. Mélanger les cartes sélectionnées 
    random.shuffle(result)
    return result

# Tri d'une pile de carte par intêret pour l'utilisateur
def orderCards(cards, userId):
    sortedCards = list()
    for c in cards:
        v = 0
        for h in getAllHistory(c.id, False):
            if h.userId == userId:
                v = ALPHA*(h.success + h.echec)/h.views + BETA*h.echec/h.views - GAMMA*h.views
                break
        sortedCards.append({'card' : c, 'value' : v})
    return sortedCards.sort(key=lambda card: card.value, reverse=True)

# Modifier le level d'une carte ou d'un user
def reloadLevelAndComplexity(elt, eltIsUser):
    listOfElements = users if eltIsUser is True else flashcards
    maxComplexity = 0
    result = {
        'complexity' : getComplexity(elt, eltIsUser),
        'level' : 10
    }
    for element in listOfElements:
        maxComplexity = max(maxComplexity, element.complexity)
    for i in range(10, 1, -1):
        if i/10 >= result['complexity']/maxComplexity:
            result['level'] = i
    return result

# Calculer la "complexité" actuel d'une carte ou d'un user
def getComplexity(elt, eltIsUser):
    eltId = "cardId" if eltIsUser is True else "userId"
    listOfElements = flashcards if eltIsUser is True else users
    historic = getAllHistory(elt.id, eltIsUser)
    totalComplexity = 0
    totalEssais = 0
    for h in historic:
        totalComplexity += h.echec * ALPHA * getElt(h[eltId], listOfElements).levelId
        totalEssais += h.echec + h.success
    return totalComplexity/totalEssais


'''------------------------------------------------------------------------
ETAPE "INITIALE" : CREATION D'UNE NOUVELLE CARTE OU PAGE
------------------------------------------------------------------------'''

# Calcul initial du level d'une nouvelle carte (appel du réseau de neurones)
def initialCardLevel(card):
    return classify(getNewCardFeatures(card))
 
# Récupération des features d'une nouvelle carte avant l'appel du réseau de neurones
def getNewCardFeatures(card):
    features = {
        'categoryId' : card.catId,
        'pageId' : card.pageId,
        'themeId' : card.themeId,
        'picture' : (card.picture == ""),
        'nbrAnswers' : len(card.answers),
        'sizeAnswers' : 0,
        'sizeQuestion' : len(card.question.split(".")),
        'sizeSentencesQuestion': 0,
        'sizeSentencesAnswers' : 0,
        'sizeWordsQuestion' : 0,
        'sizeWordsAnswers' : 0
    }

    #1. Informations sur les réponses
    totalSentences = 0
    totalWords = 0
    totalChars = 0
    for answer in card.answers:  
        sentences = answer.split(".")
        totalSentences += len(sentences)
        nbrWordsByAnswer = 0
        nbrCharsByAnswer = 0
        for sentence in sentences:
            words = sentence.split(" ")
            nbrWordsByAnswer += len(words)
            nbrCharsBySentence = 0
            for word in words:
                nbrCharsBySentence += len(word)
            nbrCharsByAnswer += nbrCharsBySentence/len(words)
        totalWords += nbrWordsByAnswer/len(sentences)
        totalChars += nbrCharsByAnswer/len(sentences)
    features['sizeAnswers'] = totalSentences/len(card.answers)
    features['sizeSentencesAnswers'] = totalWords/len(card.answers)
    features['sizeWordsAnswers'] = totalChars/len(card.answers)

    #2. Information sur la question
    question = card.question.split(".")
    totalWords = 0
    totalChars = 0
    for sentence in question:
        words = sentence.split(" ")
        totalWords += len(words)
        nbrCharsBySentence = 0
        for word in words:
            nbrCharsBySentence += len(word)
        totalChars += nbrCharsBySentence/len(words)
    features['sizeSentencesQuestion'] = totalWords/len(question)
    features['sizeWordsQuestion'] = totalChars/len(question)
    return features

# Classement initial du thème d'une nouvelle carte via les sorties de LDA
def initialTheme(card):
    finalTheme = {
        'id' : -1,
        'total' : 0
    }
    for t in themes:
        total = 0
        for k in t.keywords:
            total += k['coef']*card.question.count(k['word'])
        if total > finalTheme['total']:
            finalTheme['total'] = total
            finalTheme['id'] = t.id
    return finalTheme['id']

# Appel LDA pour chaque page pour obtenir les thèmes
def ldaTheme(page):
    #TODO call the LDA library
    return 0

'''------------------------------------------------------------------------
AUTRES METHODES
------------------------------------------------------------------------'''

# Rechercher un objet dans une liste par ID
def getElt(eltId, listOfElt):
    for elt in listOfElt:
        if elt.id == eltId:
            return elt
    return None

# Rechercher dans un historic
def getHistoric(userId, cardId):
    for h in historic:
        if h.cardId == cardId and h.userId == userId:
            return h
    newH =  History(cardId, userId, 0, 0, 0)
    return newH

# Rechercher tout les historics d'un user ou d'une carte
def getAllHistory(eltId, eltIsUser):
    result = list()
    for h in historic:
        if eltIsUser is True and h.userId == eltId:
            result.append(h)
        elif eltIsUser is False and h.cardId == eltId:
            result.append(h)
    return result

# rechercher tous les levels avec leurs users, cartes ou les deux
def getLevels(getCards, getUsers):
    result = [l for l in levels]
    result.sort(key = lambda level: level.rank)
    for r in result:
        if getUsers is True:
            for u in users:
                if u.levelId == r.id:
                    r.users.append(u)
            r.users.sort(key = lambda user: user.complexity)
        if getCards is True:
            for f in flashcards:
                if f.levelId == r.id:
                    r.cards.append(f)
            r.cards.sort(key = lambda card: card.complexity)
    return result
