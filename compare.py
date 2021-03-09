import poker, cfr
import matplotlib.pyplot as plt

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
    
    #loads AIs
    bInfo,bitr = cfr.getMostRecentSave("Saves")
    aInfo,aitr = cfr.getMostRecentSave("SavesAbstract2")
    
    #player 1 details (more precise abstraction)
    playerList[0].info = aInfo
    playerList[0].AI = poker.CFRIntelligence
    playerList[0].absLevel = 2
    
    #player 2 details (simple abstraction)
    playerList[1].info = bInfo
    playerList[1].AI = poker.CFRIntelligence
    
    
    #setup
    bigBlind = 20
    buttonPos = 0
    
    p1Winnings = []
    p2Winnings = []
    
    #simulates rounds of the game, chip count reset
    for i in range(10000):
        buttonPos = poker.gameRound(deck,playerList,bigBlind,buttonPos,4,False)
        
        p1Win = playerList[0].chips - 500
        p2Win = -p1Win
        p1Winnings.append(p1Win)
        p2Winnings.append(p2Win)
        
        for p in playerList:
            p.reset(deck)
            p.history = []
            p.chips = 500
    
    
    
    
    plotLine(getMBBValues(p1Winnings),"Advanced player balance")
    print(sum(getMBBValues(p1Winnings))/len(p1Winnings))
    plotLine(getCumulativeValues(p1Winnings),"Advanced player balance")
        