import random
class InfoSet():
    def __init__(self):
        self.cumRegrets = [0 for i in range(2)]
        self.stratSum = [0 for i in range(2)]

    def normaliseStrat(self, strat):
        """Turns regrets into probability distrubution strategy"""
        noNegatives = [max(x,0) for x in strat]
        normStrat = []
        if sum(noNegatives) > 0:
            for act in noNegatives:
                normStrat.append(act/sum(noNegatives))
                
        #if no positive regrets exist, make uniform dis
        else:
            normStrat = [1/2]*2

        return normStrat

    def getStrat(self, reachProb):
        """Returns current strategy for this info set"""
        strat = self.cumRegrets.copy()
        strat = self.normaliseStrat(strat)

        """Updates strategy sum as strategy has been used"""
        for i in range(len(self.stratSum)):
            self.stratSum[i] += reachProb * strat[i]

        return strat

    def averageStrat(self):
        return self.normaliseStrat(self.stratSum)

class Game():
    def __init__(self):
        self.sets = {}
        #terminal game histories b - bet, p - pass
        self.terminal = ["BP","BB","PP","PBB","PBP"]

    #cretes infosets as they're discovered
    def getInfoSet(self,card,history):
        if (card,history) not in self.sets:
            self.sets[(card,history)] = InfoSet()
        return self.sets[(card,history)]            

def payoff(history, cards):
    #opponent folded, win 1
    if history in ["BP","PBP"]:
        return 1
    
    else:
        #pot was increased to 2
        if "B" in history:
            payoff = 2
        else:
            payoff = 1
        current = len(history)%2
        playerCard = cards[current]
        opponentCard = cards[(current + 1) % 2]

        #+ payoff if winning, - if losing
        if playerCard > opponentCard:
            return payoff
        else:
            return -payoff

def cfr(cards, history, reachProbs, currentPlayer, game):
    if history in game.terminal:
        return payoff(history, cards)

    card = cards[currentPlayer]
    iSet = game.getInfoSet(card,history)
    opponent = (currentPlayer + 1) % 2

    strat = iSet.getStrat(reachProbs[currentPlayer])

    newRegrets = [0 for i in range(2)]
    actions = ["B","P"]
    for i in range(2):
        actionProb = strat[i]
        action = actions[i]
        newReachProbs = reachProbs.copy()
        newReachProbs[currentPlayer] *= actionProb

        #recursive call
        newRegrets[i] = -cfr(cards,history+action,newReachProbs,opponent, game)

    #value is regrets weighted by action probability
    nodeValue = 0
    for i in range(len(strat)):
        nodeValue += strat[i] * newRegrets[i]

    
    for i in range(2):
        iSet.cumRegrets[i] += reachProbs[opponent]*(newRegrets[i] - nodeValue)

    return nodeValue

def train(itr):
    """Performs itr iterations of cfr"""
    util = 0
    deck = [1,2,3]
    game = Game()
    for i in range(itr):
        cards = random.sample(deck,2)
        history = ""
        reachProbs = [1,1]
        util += cfr(cards,history,reachProbs,0,game)
    return util,game

if __name__ == "__main__":
    a,game = train(50000)

    print("Probability of bet, probability of pass")
    for i in game.sets:
        s = game.sets[i]
        print(i,"\t",s.averageStrat())

    print("\n Cum. Regret of not playing bet / pass")
    for i in game.sets:
        s = game.sets[i]
        print(i,"\t",s.cumRegrets)
