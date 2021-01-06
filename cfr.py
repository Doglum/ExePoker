import random

class InfoSet():
    def __init__(self,actions):
        #cumulative regrets
        self.cumRegrets = [0 for i in range(len(actions))]
        #cumulative strategy for calc of average
        self.stratSum = [0 for i in range(len(actions))]
        
    def normaliseStrat(self, strat):
        """Turns regrets into probability distrubution strategy"""
        #removes negatives
        noNegatives = [max(x,0) for x in strat]
        normStrat = []
        if sum(noNegatives) > 0:
            for act in noNegatives:
                normStrat.append(act/sum(noNegatives))
                
        #if no strictly positive regrets exist, make uniform dis
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
        """Returns average of all used strategies, i.e.
        the approximate Nash equilibrium strategy"""
        return self.normaliseStrat(self.stratSum)

class Sets():
    """Object that stores, retrieves and creates information sets"""
    def __init__(self):
        self.sets = {}
    def getInfoSet(self,params):
        if params not in self.sets:
            self.sets[params] = InfoSet()
        return self.sets[params]
    
stored = Sets()






