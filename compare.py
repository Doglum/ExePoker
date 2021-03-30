import poker, cfr
import matplotlib.pyplot as plt
from copy import deepcopy

global figureNum
figureNum = 0
def plotLine(values,title,x="Round No.",y="Advantage"):
    """Plots a line"""
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
    

if __name__ == "__main__":
    from cfr import Sets,InfoSet
    #creates deck & players
    deck = poker.Card.getDeck()
    playerList = poker.Player.getPlayerList(2,500)
    
    #initialises player objects for AIs
    raisePlayer = poker.Player(500)
    raisePlayer.AI = poker.raiseBot
    
    randomPlayer = poker.Player(500)
    randomPlayer.AI = poker.randomBot
    
    
    #Abstraction level 1, non forgetful (b - basic)
    bPlayer = poker.Player(500)
    bPlayer.info, bitr = cfr.getMostRecentSave("Abstract1")
    bPlayer.AI = poker.CFRIntelligence
    bPlayer.absLevel = 1
    
    #Abstraction level 2, non forgetful (a - advanced)
    aPlayer = poker.Player(500)
    aPlayer.info, aitr = cfr.getMostRecentSave("Abstract2")
    aPlayer.AI = poker.CFRIntelligence
    aPlayer.absLevel = 2
    
    #Abstraction level 1, forgetful (bf -basic forgetful)
    bfPlayer = poker.Player(500)
    bfPlayer.info, bfItr = cfr.getMostRecentSave("ForgetfulAbstract1")
    bfPlayer.AI = poker.CFRIntelligence
    bfPlayer.absLevel = 1
    bfPlayer.forgetful = True
    
    #Abstraction level 2, forgetful (af -advanced forgetful)
    afPlayer = poker.Player(500)
    afPlayer.info, afItr = cfr.getMostRecentSave("ForgetfulAbstract2")
    afPlayer.AI = poker.CFRIntelligence
    afPlayer.absLevel = 2
    afPlayer.forgetful = True
    
    #Probabilistic, forgetful (p - probabilistic)
    pPlayer = poker.Player(500)
    pPlayer.info,pItr = cfr.getMostRecentSave("ForgetfulProbabilistic")
    pPlayer.AI = poker.CFRIntelligence
    pPlayer.forgetful = True
    pPlayer.probabilistic = True
    
    #CONFIGURE as appropriate, player 0 goes first
    playerList[0] = bfPlayer
    playerList[1] = afPlayer
    
    graphTitle = "Player 1 winnings"
    
    rounds = 10000
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
            print("Reached",i,"Iterations")
    
    
    
    
    plotLine(getMBBValues(p1Winnings)[500:],graphTitle)
    print((sum(p1Winnings)/(bigBlind/1000)/rounds),"mbb/g")
    plotLine(getCumulativeValues(p1Winnings),graphTitle)
        