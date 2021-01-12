import random
from itertools import combinations
from copy import deepcopy
import cfr

#consider switching to enum
class Card():
    """Class that represents a standard playing card"""
    def __init__(self,value,suit):

        self.value = value
        
        if value == 14:
            self.name = "A"
        elif value == 13:
            self.name = "K"
        elif value == 12:
            self.name = "Q"
        elif value == 11:
            self.name = "J"
        else:
            self.name=str(value)

        self.suit = suit
        
        if suit.lower() in ["c","clubs"]:
            self.name+="♣"
        elif suit.lower() in ["s","spades"]:
            self.name+="♠"
        elif suit.lower() in ["h","hearts"]:
            self.name+="♥"
        elif suit.lower() in ["d","diamonds"]:
            self.name+="♦"
        else:
            self.name += "badsuit"

    def __str__(self):
        """Makes object convertable to string"""
        return self.name

    def __eq__(self,other):
        """Allows comparison with =="""
        equal = self.value == other.value and \
                self.suit == other.suit
        return equal
        

    def getDeck():
        """Creates a 52 card deck (list) of Card objects"""
        deck = []
        suits = ["Clubs","Spades","Hearts","Diamonds"]
        for sui in suits:
            for val in range(2,15):
                deck.append(Card(val,sui))
        return deck

    def displayCards(cards):
        """Displays multiple cards, formatted horizontally"""
        msg = ""
        for card in cards:
            msg+=str(card)+" "*(4-len(str(card)))
        print(msg)

def drawX(x,deck):
    """Removes x cards from a deck list and returns it as a list"""
    hand = []
    for i in range(x):
        cardToRemove = random.choice(deck)
        deck.remove(cardToRemove)
        hand.append(cardToRemove)
    return hand

def humanIntelligence(choices,player):
    """Takes list of decisions, allows human to choose them"""
    amount = 0
    Card.displayCards(player.holeCards)
    print("You may takes the following actions:")
    for choice in choices:
        print(choice)
    playerChoice = input("What would you like to do?\n")

    if playerChoice == "Raise":
        amount = int(input("By how much?\n"))
        return playerChoice, amount
    else:
        return playerChoice, amount

def randomBot(choices,player):
    """AI that randomly selects an action"""
    amount = 0
    choice = random.choices(choices)[0]
    if choice == "Raise":
        amount = 20
        return choice, amount
    else:
        return choice, amount
    

def CFRTrainingIntelligence(choices,player):
    hole = player.holeCards
    comm = player.communityCards
    iSets = cfr.stored.sets
    
    #TODO finish

class Player():
    """Class representing a poker player, also contains info available
    to them"""
    def __init__(self,chips):
        self.holeCards = []
        self.chips = chips
        self.bet = 0
        self.folded = False
        self.allin = False
        self.busted = False #could remove from playerList instead

        #info for CFR
        self.communityCards = []
        self.history = []

        #function that handles decisions TODO think about
        self.AI = humanIntelligence

    def reset(self,deck):
        """Removes cards from player back to deck,
        resets round specific attributes"""
        deck += self.holeCards
        self.holeCards.clear()
        
        self.bet = 0
        self.folded = False
        self.allin = False
        

    def getPlayerList(n,chips):
        """Returns a list of n player objects with equal chips"""
        playerList = []
        for i in range(n):
            playerList.append(Player(chips))
        return playerList

    def call(self,pot,highestBet):
        """Player matches highest bet or does as best they can
        and goes all in"""
        #go all-in to call
        if highestBet-self.bet > self.chips:
            self.bet += self.chips
            pot += self.chips
            self.allin = True
            
        #standard call, match highest
        else:
            self.chips -= highestBet - self.bet
            pot += highestBet - self.bet
            self.bet = highestBet

        return pot

    def fold(self):
        self.folded = True

    #raise is reserved word, consider alternatives
    def _raise(self,pot,highestBet,amount):
        """Takes current highest bet and amount to raise,
            adjusts chip count and returns new highest bet"""
        if highestBet - self.bet + amount > self.chips:
            print("rejected")
        else:
            previousBet = self.bet
            self.bet += highestBet - self.bet + amount
            self.chips -= highestBet - previousBet + amount
            pot += highestBet - previousBet + amount
            highestBet += amount

        if self.chips == 0:
            self.allin = True

        return pot,highestBet
            
#maybe program dealing in correct order
def deal(deck,playerList):
    """Deals 2 cards to each player, removing them from the deck"""
    for player in playerList:
        if not player.busted:
            player.holeCards += drawX(2,deck)


def handRecognition(hand):
    """Takes a list of 5 Card objects and classifies it as a poker hand"""
    #hand = hand.copy() might be needed
    hand.sort(key = lambda card:card.value) #sorts hand by value asc

    rankings = [0,0,0,0,0,0]

    #---flush /straight flush---
    flush = True
    suit = hand[0].suit
    for card in hand[1::]:
        if card.suit != suit:
            flush = False
            break
    if flush:
        rankings[1] = hand[4].value
    
    #---straight / straight flush---
    straight = True

    #ace counts as low card
    if hand[4].value==14 and hand[0].value==2:
        for i in range(1,3):
            if hand[i].value + 1 != hand[i+1].value:
                straight = False
                break
            
        if straight:
            rankings[1] = 5
            
    #typical case, ace is high card
    else:
        for i in range(4):
            if hand[i].value + 1 != hand[i+1].value:
                straight = False
                break
            
        if straight:
            rankings[1] = hand[4].value
            

    #---four of a kind---
    four = False
    fourValue = 0
    for i in range(2):
        if hand[i].value == hand[i+1].value and \
           hand[i].value == hand[i+2].value and \
           hand[i].value == hand[i+3].value:
            four = True
            fourValue = hand[i].value
            break
    
    #---three of a kind / full house three---
    three = False
    threeValue = 0
    for i in range(3):
        if hand[i].value == hand[i+1].value and \
           hand[i].value == hand[i+2].value:
            three = True
            threeValue = hand[i].value
            break
    
    #---pair / 2 pair / Full house pair---
    pairs = 0
    pairValues = []
    for i in range(4):
        if hand[i].value == hand[i+1].value:
            pairs+=1
            pairValues.append(hand[i].value)


    #---rank assignment + tie-breaker values---
    if straight and flush:
        rankings[0] = 9
        
        msg = "Straight Flush"
        
    elif four:
        rankings[0] = 8
        rankings[1] = fourValue
        for card in hand[0::4]:
            if card.value != fourValue:
                rankings[2] = card.value
                break
            
        msg = "Four of a Kind"
        
    elif three and pairs >= 3:
        rankings[0] = 7
        rankings[1] = threeValue
        for val in pairValues:
            if val != threeValue:
                rankings[2] = val
                break
            
        msg = "Full House"
        
    elif flush:
        rankings[0] = 6
        
        msg = "Flush"

    elif straight:
        rankings[0] = 5
        
        msg = "Straight"

    elif three:
        rankings[0] = 4
        rankings[1] = threeValue
        kickers = [x for x in hand if x.value!=threeValue]
        rankings[2] = kickers[-1].value
        rankings[3] = kickers[-2].value
        
        msg = "Three of a Kind"
        
    elif pairs == 2:
        rankings[0] = 3
        rankings[1] = pairValues[-1]
        rankings[2] = pairValues[-2]
        rankings[3] = [x for x in hand if not x.value in pairValues][0].value
        
        msg = "Two Pair"
        
    elif pairs == 1:
        rankings[0] = 2
        rankings[1] = pairValues[0]
        kickers = [x for x in hand if not x.value in pairValues]
        rankings[2] = kickers[-1].value
        rankings[3] = kickers[-2].value
        rankings[4] = kickers[-3].value
        
        msg = "Pair"

    else:
        rankings[0] = 1
        for i in range(1,6):
            rankings[i] = hand[-i].value

        msg = "High Card"

    return rankings,msg


def getWinningHands(rankList,compareIndex = 0,toCompare = []):
    """Takes a list of outputted arrays from hand recognition and outputs
       the indices of the winners"""
    highest = -1
    winners = []
    
    if compareIndex == 0:
        toCompare = list(range(len(rankList)))
        
    compCopy = toCompare.copy()
    for i in compCopy:
        
        #if new highest, remove lowers from contention
        if rankList[i][compareIndex] > highest:
            for win in winners:
                toCompare.remove(win)
            winners.clear()

            
            highest = rankList[i][compareIndex]
            winners.append(i)

        elif rankList[i][compareIndex] == highest:
            winners.append(i)

        else:
            toCompare.remove(i)

    #if a single winner has been found / there's a tie  
    if len(winners) == 1 or highest == 0 or compareIndex == 5:
        return winners
    
    else:
        return getWinningHands(rankList,compareIndex+1,toCompare)

def getBest(holeCards,communityCards):
    """Take list of 2 hole cards and list of 5 community cards best,
    return the rankList of the best hand, also works with >=3 community cards"""
    best = [0,0,0,0,0,0]
    #21 iterations for full 7 cards
    for hand in combinations(holeCards+communityCards,5):
        #gets the higher ranking of the two hands
        compare2 = [best]
        compare2.append(handRecognition(list(hand))[0])
        bestIndex = getWinningHands(compare2)[0]
        best = compare2[bestIndex]
        
    return best
        
    

def checkGameWon(playerList):
    """Check to see if there is a winner, returns true if so"""
    playersIn = 0
    for player in playerList:
        if not player.folded and not player.busted:
            win = player
            playersIn += 1
        if playersIn > 1:
            return False, None
    return True, win

def estimateHandStrength(holeCards,communityCards,opponents=1,iterations=500):
    """Performs random iterations of possible outcomes to
    get an estimate of potential hand strength"""

    #removes known cards from estimation
    simulatedDeck = Card.getDeck()
    cardsToRemove = []
    for card in holeCards+communityCards:
        for i in range(len(simulatedDeck)):
            if card == simulatedDeck[i]:
                cardsToRemove.append(simulatedDeck[i])
                break

    for card in cardsToRemove:
        simulatedDeck.remove(card)

    #performs iterations of possibilities
    flopWins = 0
    turnWins = 0
    riverWins = 0
    for i in range(iterations):
        dck = simulatedDeck.copy()
        cmCards = communityCards.copy()
        
        #simulate opponent cards
        oppHoles = []
        for i in range(opponents):
            oppHoles.append(drawX(2,dck))

        #TODO add something for pre-flop strength

        #estimate strength on flop
        if len(cmCards) == 0:
            cmCards+=drawX(3,dck)
            if compareSimHands(holeCards,cmCards,oppHoles):
                flopWins += 1
            
        #estimate strength on turn
        if len(cmCards) == 3:
            cmCards+=drawX(1,dck)
            if compareSimHands(holeCards,cmCards,oppHoles):
                turnWins += 1
                
        #estimate strength on river
        if len(cmCards) == 4:
            cmCards+=drawX(1,dck)
            if compareSimHands(holeCards,cmCards,oppHoles):
                riverWins += 1

        #estimate strength on showdown
        elif len(cmCards) == 5:
            if compareSimHands(holeCards,cmCards,oppHoles):
                riverWins += 1
                
    return [flopWins,turnWins,riverWins]

def compareSimHands(holeCards,cmCards,oppHoles):
    """Helper for estimateHandStrength, returns true if a
    player wins with inputted hole cards and community cards"""
    playerValue = getBest(holeCards,cmCards)
    oppValues = []
    for hole in oppHoles:
        oppValues.append(getBest(hole,cmCards))
    return getWinningHands([playerValue]+oppValues)[0] == 0
        

def bettingRound(playerList,highestBet,activePlayer,pot,limit,printing = True):
    """Handles a betting round of a single poker game"""
    playersReady = 0
    while playersReady < len(playerList):
        player = playerList[activePlayer]
        if player.folded or player.busted or player.allin:
            activePlayer = (activePlayer + 1) % len(playerList)
            playersReady += 1
            continue

        raised = False
        folded = False

        #if player needs to call
        if player.bet < highestBet:

            #if raise limit reached, remove raise as possible action
            if limit > 0:
                choice, amount = player.AI(["Call","Raise","Fold"],player)
            elif limit == 0:
                choice, amount = player.AI(["Call","Fold"],player)
            
            if choice == "Call":
                pot = player.call(pot,highestBet)
                raised = False
                if printing:
                    print("Player",activePlayer,"calls")
                
            elif choice == "Raise":
                pot,highestBet = player._raise(pot,highestBet,amount)
                raised = True
                limit -= 1
                if printing:
                    print("Player",activePlayer,"raises to",highestBet)
                
            elif choice == "Fold":
                player.fold()
                raised = False
                folded = True
                if printing:
                    print("Player",activePlayer,"folds")
                
        #if player doesn't need to call     
        elif player.bet == highestBet:
            #if raise limit reached, remove raise as possible action
            if limit > 0:
                choice, amount = player.AI(["Check","Raise"],player)
            elif limit == 0:
                choice, amount = player.AI(["Check"],player)

            if choice == "Check":
                raised = False
                if printing:
                    print("Player",activePlayer,"checks")
                
            elif choice == "Raise":
                pot,highestBet = player._raise(pot,highestBet,amount)
                raised = True
                limit -= 1
                if printing:
                    print("Player",activePlayer,"raises to",highestBet)

        if raised:
            playersReady = 1

        #needed for 1st round where a player can start with enough chips
        elif folded:
            if checkGameWon(playerList)[0]:
                break
            
        else:
            playersReady += 1

        #adds betting history info (as letter) to players
        for p in playerList:
            p.history.append(choice)
        
        activePlayer = (activePlayer + 1) % len(playerList)

    return activePlayer, highestBet, pot

def gameRound(*args):
    #TODO switch away from *args
    """Performs one full round of poker"""
    deck = args[0]
    playerList = args[1]
    bigBlind = args[2]
    buttonPos = args[3]
    limit = args[4]
    pot = 0
    #TODO account for busted players for blinds
    if len(playerList) > 2:
        activePlayer = (buttonPos + 3) % len(playerList)
    elif len(playerList) == 2:
        #heads up, dealer is also small blind
        activePlayer = buttonPos

    #sets blinds by raising half big blind twice
    if len(playerList) > 2:
        pot, highestBet = playerList[(buttonPos+1) % len(playerList)]._raise(pot,0,int(bigBlind/2))
        pot, highestBet = playerList[(buttonPos+2) % len(playerList)]._raise(pot,highestBet,int(bigBlind/2))
    elif len(playerList) == 2:
        pot, highestBet = playerList[buttonPos]._raise(pot,0,int(bigBlind/2))
        pot, highestBet = playerList[(buttonPos+1) % len(playerList)]._raise(pot,highestBet,int(bigBlind/2))
    

    communityCards = []

    print("Dealing...")
    deal(deck,playerList)

    #preflop
    activePlayer, highestBet, pot = bettingRound(playerList,highestBet,0,pot,limit)
    gameWon, winner = checkGameWon(playerList)
    
    if not gameWon:
        #flop
        communityCards += drawX(3,deck)
        for p in playerList:
            p.communityCards = deepcopy(communityCards)
        Card.displayCards(communityCards)

        activePlayer, highestBet, pot = bettingRound(playerList,highestBet,activePlayer,pot,limit)
        gameWon, winner = checkGameWon(playerList)

    #does turn and river
    for i in range(2):
        if not gameWon:
            communityCards += drawX(1,deck)
            for p in playerList:
                p.communityCards = deepcopy(communityCards)
            Card.displayCards(communityCards)
            
            activePlayer, highestBet, pot = bettingRound(playerList,highestBet,activePlayer,pot,limit)
            gameWon, winner = checkGameWon(playerList)



    if not gameWon:
        #post river, compare hands
        inContention = []
        rankList = []
        for player in playerList:
            if not player.folded and not player.busted:
                inContention.append(player)
                rankList.append(getBest(player.holeCards,communityCards))

        winnerIndices = getWinningHands(rankList)

        #TODO split pot when players are allin with <highestBet
        #TODO sort out rounding on odd splits
        winnings = pot/len(winnerIndices)
        
        for i in winnerIndices:
            print("Player",i,"Wins!")
            inContention[i].chips += winnings

    #if someone won because everyone else folded
    if gameWon:
        winner.chips += pot
        print("Player",playerList.index(winner),"Wins!")

    #TODO account for busted players
    butttonPos = (buttonPos + 1) % len(playerList)

    for player in playerList:
        player.reset(deck)
    for card in communityCards:
        deck.append(card)
        
    return buttonPos
        
#hand for testing
"""
hand = [
    Card(14,"d"),
    Card(12,"s"),
    Card(11,"c"),
    Card(10,"h"),
    Card(9,"s")
        ]


hand2 = [
    Card(14,"c"),
    Card(12,"h"),
    Card(11,"d"),
    Card(9,"s"),
    Card(10,"h")
        ]

hands = [handRecognition(hand)[0],handRecognition(hand2)[0]]
print(getWinningHands(hands))
"""

#hand comparison testing
"""
if __name__ == "__main__":
    deck = Card.getDeck()
    hands = []
    rankings = []
    for i in range(5):
        hands.append(draw5(deck))
    for hand in hands:
        Card.displayCards(hand)
        print(handRecognition(hand))
        rankings.append(handRecognition(hand)[0])
        print()

    print(getWinningHands(rankings))
"""

#estimate hand testing
"""
if __name__ == "__main__":
    deck = Card.getDeck()
    hole = [Card(9,"s"),Card(8,"s")]
    flop = [Card(2,"s"),Card(5,"s"),Card(8,"h")]
    turn = flop+[Card(11,"c")]
    river = turn+[Card(10,"c")]
    Card.displayCards(hole)
    print(estimateHandStrength(hole,[]))
    Card.displayCards(flop)
    print(estimateHandStrength(hole,flop))
    Card.displayCards(turn)
    print(estimateHandStrength(hole,turn))
    Card.displayCards(river)
    print(estimateHandStrength(hole,river))
"""
#"""
if __name__ == "__main__":
    #TODO finish game loop and get function to detect all but one busted
    deck = Card.getDeck()
    playerList = Player.getPlayerList(2,300)
    playerList[1].AI = randomBot
    bigBlind = 50
    buttonPos = 0
    buttonPos = gameRound(deck,playerList,bigBlind,buttonPos,4)
#"""
    
    
