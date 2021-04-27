import poker, cfr
import matplotlib.pyplot as plt
from copy import deepcopy
from itertools import combinations
import numpy as np
import time,csv

global figureNum
figureNum = 0

def loadGames(filename="games.csv",skill=None,ai=None):
    """Converts csv of human games into useful info"""
    aiPlayer = poker.Player(500)
    humanPlayer = poker.Player(500)
    entries = []
    with open(filename, encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",")
        for row in csvreader:
            entries.append(row)
    
    #removes headers
    entries = entries[1:]
    #filters entries based on params
    if skill and ai:
        entries = [e for e in entries if e[3]==ai and e[5]==skill]
    elif skill:
        entries = [e for e in entries if e[5]==skill]
    elif ai:
        entries = [e for e in entries if e[3]==ai]
        
    print("No. Experienced:",len([e for e in entries if e[5]=="Experienced"]))
    print("No. Intermediate:",len([e for e in entries if e[5]=="Intermediate"]))
    print("No. Novice:",len([e for e in entries if e[5]=="Novice"]))
    
    
    #converts entry to useful objects
    #history, aiButton, result, aiType, aiIteration, playerSkill, aiCards, playCards, commCards
    for entry in entries:
        if entry[0][-1]=="F":
            reason = "fold"
        else:
            reason = "showdown"
            
        amount = int(entry[2])
        
        if amount<0:
            aiWin,humanWin = "lose","win"
        elif amount == 0:
            aiWin,humanWin = "tie","tie"
        else:
            aiWin,humanWin = "win","lose"
        
        #makes cards card objects, ai,play,comm
        cardIndices = [6,7,8]
        cardsList = []
        for i in cardIndices:
            cards = []
            for card in entry[i].split():
                value = 0
                if card[:-1] == "J":
                    value = 11
                elif card[:-1] == "Q":
                    value = 12
                elif card[:-1] == "K":
                    value = 13
                elif card[:-1] == "A":
                    value = 14
                else:
                    value = int(card[:-1])
                cards.append(poker.Card(value,card[-1]))
            cardsList.append(cards)
        
        #adds entries as recorded tuples
        aiPlayer.recorded.append((aiWin,reason,cardsList[0],cardsList[2],amount))
        humanPlayer.recorded.append((humanWin,reason,cardsList[1],cardsList[2],-amount))
    
    aiWinnings = [r[4] for r in aiPlayer.recorded]
    humanWinnings = [r[4] for r in humanPlayer.recorded]
    return [aiPlayer, humanPlayer], aiWinnings, humanWinnings
    
    
def plotLine(values,title,x="Round No.",y="Advantage"):
    """Plots a line chart with pyplot"""
    global figureNum
    figureNum+=1
    plt.figure(figureNum)
    plt.plot(values)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.show()
    
def plotBar(groups,values,title,x="Card Rank",y="Quantity"):
    """Plots a bar chart with pyplot"""
    global figureNum
    figureNum+=1
    plt.figure(figureNum)
    plt.bar(groups,values)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.show()
    
def plotMultipleBar(groups,valuesList,title,x="Card Rank",y="Quantity"):
    """Plots multiple bars"""
    global figureNum
    figureNum+=1
    plt.figure(figureNum)
    
    # set width of bars
    barWidth = 0.25
     
    #Gets positions
    pos = np.arange(len(valuesList[0]))
     
    player = 0
    # Make one bar for each values list in valuesList
    for values in valuesList:
        plt.bar(pos, values, width=barWidth, label="Player "+str(player))
        player += 1
        pos = [p + barWidth for p in pos]
     
    # Adds labels for x at correct locations
    plt.xlabel(x)
    plt.xticks([r + barWidth/2 for r in range(len(valuesList[0]))], groups)
    
    plt.ylabel(y)
    plt.title(title)
    
    plt.legend()
    plt.show()
    
def plotLossReason(record,title,x="Player",y="Quantity"):
    global figureNum
    figureNum+=1
    plt.figure(figureNum)
    groups = ["Lose","Win","Tie"]
    folds = []
    showdowns = []
    
    folds.append(len([r for r in records0 if r[0]=="lose" and r[1]=="fold"]))
    folds.append(len([r for r in records0 if r[0]=="win" and r[1]=="fold"]))
    folds.append(0)
    
    showdowns.append(len([r for r in records0 if r[0]=="lose" and r[1]=="showdown"]))
    showdowns.append(len([r for r in records0 if r[0]=="win" and r[1]=="showdown"]))
    showdowns.append(len([r for r in records0 if r[0]=="tie" and r[1]=="showdown"]))
    
    width = 0.8
    fig, ax = plt.subplots()
    
    ax.bar(groups, folds, width, label='Fold')
    ax.bar(groups, showdowns, width, bottom=folds,label='Showdown')
    
    ax.legend()
    plt.ylabel(y)
    plt.xlabel(x)
    plt.title(title)
    plt.show()
    
    
    
def getCumulativeValues(vals):
    """Gets accumulated values of list of vals"""
    cumVals = []
    cumValue = 0
    for v in vals:
        cumValue+=v
        cumVals.append(cumValue)
    return cumVals

def getMBBValues(vals,bb = 20):
    """Gets cumulative mili big blind per game value"""
    mbb = []
    cumValue = 0
    for i in range(len(vals)):
        cumValue += vals[i]
        mbb.append(((cumValue/bb)*1000)/(i+1))
    return mbb

def cardRanks():
    groups = ["High",
              "Pair",
              "2Pair",
              "3Kind",
              "Strt",
              "Flush",
              "FHouse",
              "4Kind",
              "StFlu"]
    return groups

def categoriseCardRanks(record):
    """Gets records from player object and counts the hand
    ranks of each play"""
    groups = cardRanks()
    values = [0 for i in range(9)]
    for r in record:
        if not len(r[3])<3:
            rank = poker.getBest(r[2],r[3])[0]
            values[rank-1] += 1
    return groups,values

def averageRankPayoff(record):
    """Gets records and calculates average payoff of a rank in mbb"""
    groups = cardRanks()
    wins = [[] for i in range(9)]
    for r in record:
        if not len(r[3])<3:
            rank = poker.getBest(r[2],r[3])[0]
            wins[rank-1].append(r[4])
            
    results = []
    for w in wins:
        if len(w) == 0:
            results.append(0)
        else:
            results.append((sum(w)/len(w))/0.02)
    return groups, results
        

def duel(player1,player2,rounds = 10000,printing = True, analyse = False):
    """Simulates rounds of poker between two AIs and returns their winnings
    and losses, will print an update message at intervals if printing is true"""
    playerList[0] = player1
    playerList[1] = player2
    
    updateInterval = rounds/10
    
    #setup
    bigBlind = 20
    buttonPos = 0
    
    p1Winnings = []
    p2Winnings = []
    
    
    
    #simulates rounds of the game, chip count reset
    for i in range(rounds):
        buttonPos = poker.gameRound(deck,playerList,bigBlind,buttonPos,4,False,analyse)
        
        p1Win = playerList[0].chips - 500
        p2Win = -p1Win
        p1Winnings.append(p1Win)
        p2Winnings.append(p2Win)
        
        for p in playerList:
            p.reset(deck)
            p.history = []
            p.chips = 500
            
        if i % updateInterval == 0:
            if printing: print("Reached",i,"Iterations")
            
    return p1Winnings, p2Winnings

def tournament(players, rounds = 100, analyse = False):
    """Performs 1 duel between each player in players and 
    returns 2d winnings list"""
    winnings = [[0 for i in range(len(players))] for i in range(len(players))]
    for pair in combinations(players,2):
        i1 = players.index(pair[0])
        i2 = players.index(pair[1])
        win1,win2 = duel(pair[0],pair[1],rounds,printing=False,analyse = analyse)
        winnings[i1][i2] = sum(win1)/(20/1000)/rounds
        winnings[i2][i1] = sum(win2)/(20/1000)/rounds
        
    return winnings
    
    
    
    

if __name__ == "__main__":
    #creates deck & players
    deck = poker.Card.getDeck()
    playerList = poker.Player.getPlayerList(2,500)
    AIList = []
    
    #initialises player objects for AIs
    raisePlayer = poker.Player(500)
    raisePlayer.AI = poker.raiseBot
    #AIList.append(raisePlayer)
    
    callPlayer = poker.Player(500)
    callPlayer.AI = poker.callBot
    #AIList.append(callPlayer)
    
    randomPlayer = poker.Player(500)
    randomPlayer.AI = poker.randomBot
    #AIList.append(randomPlayer)
    
    #Abstraction level 1, non forgetful (b - basic)
    bPlayer = poker.Player(500)
    bPlayer.info, bitr = cfr.getMostRecentSave("Abstract1")
    bPlayer.AI = poker.CFRIntelligence
    bPlayer.absLevel = 1
    AIList.append(bPlayer)
    
    #Abstraction level 2, non forgetful (a - advanced)
    aPlayer = poker.Player(500)
    aPlayer.info, aitr = cfr.getMostRecentSave("Abstract2")
    aPlayer.AI = poker.CFRIntelligence
    aPlayer.absLevel = 2
    AIList.append(aPlayer)
    
    #Abstraction level 1, forgetful (bf -basic forgetful)
    bfPlayer = poker.Player(500)
    bfPlayer.info, bfItr = cfr.getMostRecentSave("ForgetfulAbstract1")
    bfPlayer.AI = poker.CFRIntelligence
    bfPlayer.absLevel = 1
    bfPlayer.forgetful = True
    AIList.append(bfPlayer)
    
    #Abstraction level 2, forgetful (af -advanced forgetful)
    afPlayer = poker.Player(500)
    afPlayer.info, afItr = cfr.getMostRecentSave("ForgetfulAbstract2")
    afPlayer.AI = poker.CFRIntelligence
    afPlayer.absLevel = 2
    afPlayer.forgetful = True
    AIList.append(afPlayer)
    
    #Probabilistic, forgetful (p - probabilistic)
    pPlayer = poker.Player(500)
    pPlayer.info,pItr = cfr.getMostRecentSave("ForgetfulProbabilistic")
    pPlayer.AI = poker.CFRIntelligence
    pPlayer.forgetful = True
    pPlayer.probabilistic = True
    #AIList.append(pPlayer)
    
    #CONFIGURE as appropriate, player 0 goes first
    playerList[0] = bfPlayer
    playerList[1] = randomPlayer
    
    graphTitle = "Player 0 winnings"
    
    rounds = 1000
    
    
    
    #ROUND ROBIN TOURNAMENT
    """
    start = time.time()
    winnings = tournament(AIList,rounds)
    end = time.time()
    print(end-start,"seconds to complete round robin")
    print(np.matrix(winnings))
    """
    
    #DUEL, necessary for below items
    #"""
    start = time.time()
    p1Winnings, p2Winnings = duel(playerList[0],playerList[1],rounds,analyse = True)
    end = time.time()
    print(end-start,"seconds to complete duel")
    #"""
    
    #HUMAN ASSESSMENT, alternative to duel
    #skill can be Novice,Intermediate,Experienced, ai can be any ai's name
    #playerList,p1Winnings,p2Winnings = loadGames(ai=None,skill=None)
    
    #WINNINGS OVER TIME, mbb/g then accumulated winnings by round
    #"""
    plotLine(getMBBValues(p1Winnings)[100:],graphTitle)
    print((sum(p1Winnings)/(20/1000)/rounds),"mbb/g")
    plotLine(getCumulativeValues(p1Winnings),graphTitle)
    #"""
    
    #RECORDS, necessary for below items
    #"""
    records0 = playerList[0].recorded
    records1 = playerList[1].recorded
    #"""
    
    #RANK OCCURENCE FOR BOTH PLAYERS
    #"""
    trimmedRecords0 = [r for r in records0 if True]
    trimmedRecords1 = [r for r in records1 if True]
    
    groups,values0 = categoriseCardRanks(trimmedRecords0)
    _,values1 = categoriseCardRanks(trimmedRecords1)
    
    valuesList = [values0,values1]
    
    plotMultipleBar(groups,valuesList,"Card Ranks of each player")
    #"""
    
    #AVERAGE PAYOFF BY RANK
    #"""
    groups,avgPayValues0 = averageRankPayoff(records0)
    _,avgPayValues1 = averageRankPayoff(records1)
    plotMultipleBar(groups,[avgPayValues0,avgPayValues1],"Mean Winnings by Rank",y="Mean Winnings (mbb)")
    #"""
    
    
    #LOSS REASON, 1 bar
    """
    folds = len([r for r in records0 if r[0]=="lose" and r[1]=="fold"])
    worseHands = len([r for r in records0 if r[0]=="lose" and r[1]=="showdown"])
    plotBar(["Folds","Worse Hand"],[folds,worseHands],"Reason for loss",x="")
    """
    
    #WIN/LOSS REASON, stacked bar
    #"""
    percentWin = len([r for r in records0 if r[0]=="win"])/len(records0)
    print("Proportion of games won:",percentWin)
    plotLossReason(records0,"Reason For Loss/Win/Tie",x="")
    #"""