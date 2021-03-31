import poker, cfr
import matplotlib.pyplot as plt
from copy import deepcopy
from itertools import combinations

global figureNum
figureNum = 0
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
    
def getCumulativeValues(vals):
    """Gets accumulated values of list of vals"""
    cumVals = []
    cumValue = 0
    for v in vals:
        cumValue+=v
        cumVals.append(cumValue)
    return cumVals

def getMBBValues(vals,bb = 20):
    mbb = []
    cumValue = 0
    for i in range(len(vals)):
        cumValue += vals[i]
        mbb.append(((cumValue/bb)*1000)/(i+1))
    return mbb

def duel(player1,player2,rounds = 10000,printing = True):
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
        buttonPos = poker.gameRound(deck,playerList,bigBlind,buttonPos,4,False)
        
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

def tournament(players,rounds = 100):
    """Performs 1 duel between each player in players and 
    returns 2d winnings list"""
    winnings = [[0 for i in range(len(players))] for i in range(len(players))]
    for pair in combinations(players,2):
        i1 = players.index(pair[0])
        i2 = players.index(pair[1])
        win1,win2 = duel(pair[0],pair[1],rounds,printing=False)
        winnings[i1][i2] = sum(win1)/(20/1000)/rounds
        winnings[i2][i1] = sum(win2)/(20/1000)/rounds
        
    return winnings
    
    
    
    

if __name__ == "__main__":
    from cfr import Sets,InfoSet
    #creates deck & players
    deck = poker.Card.getDeck()
    playerList = poker.Player.getPlayerList(2,500)
    AIList = []
    
    #initialises player objects for AIs
    raisePlayer = poker.Player(500)
    raisePlayer.AI = poker.raiseBot
    AIList.append(raisePlayer)
    
    randomPlayer = poker.Player(500)
    randomPlayer.AI = poker.randomBot
    AIList.append(randomPlayer)
    
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
    playerList[1] = afPlayer
    
    graphTitle = "Player 1 winnings"
    
    rounds = 10000
    
    
    winnings = tournament(AIList,rounds)
    
    
    #p1Winnings, p2Winnings = duel(playerList[0],playerList[1],rounds)
    """
    plotLine(getMBBValues(p1Winnings)[500:],graphTitle)
    print((sum(p1Winnings)/(20/1000)/rounds),"mbb/g")
    plotLine(getCumulativeValues(p1Winnings),graphTitle)
    """