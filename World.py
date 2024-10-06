import numpy as np
import json
from copy import deepcopy


def loadValues(name):
    name = f"{name}.json"
    file = open(name)
    json_str = file.read()
    json_data = json.loads(json_str)
    return json_data


def storeValues(name, data):
    with open(f'{name}.json', 'w') as f:
        json.dump(data, f)


def softMax(x):
    x = np.array(x)
    return np.exp(x)/sum(np.exp(x))


class Field:
    def __init__(self):
        self.field = np.zeros(9)

    def getWinner(self):
        # check rows
        for a in range(3):
            if sum(self.field[3*a:3*a+3]) == 3:
                return 1
            if sum(self.field[3*a:3*a+3]) == -3:
                return -1
        # check columns
        for a in range(3):
            if sum(self.field[a::3]) == 3:
                return 1
            if sum(self.field[a::3]) == -3:
                return -1
        # check diagonals
        if self.field[0] + self.field[4] + self.field[8] == 3:
            return 1
        if self.field[0] + self.field[4] + self.field[8] == -3:
            return -1
        if self.field[2] + self.field[4] + self.field[6] == 3:
            return 1
        if self.field[2] + self.field[4] + self.field[6] == -3:
            return -1
        return None

    def isFinished(self):
        return 0 not in self.field or self.getWinner() is not None


class Player:
    def __init__(self, first, symbol):
        self.first = first
        self.symbol = symbol
        self.stateTable = {}

    def choose(self, field):
        bestAction = [[], -1000]
        for action in self.getPossibleActions(field):
            if self.stateTable[action[0]] > bestAction[1]:
                bestAction = [action, self.stateTable[action[0]]]

        return bestAction[0][1]

    def getPossibleActions(self, field):
        possibleActions = []
        for a in range(9):
            f = deepcopy(field)
            if field[a] == 0:
                f[a] = self.symbol
                possibleActions.append([str(f), a])
        return possibleActions


class World:
    def __init__(self):
        self.field = Field()
        self.p1 = Player(True, 1)
        self.p2 = Player(False, -1)
        self.counter = {"wins": 0,
                        "draws": 0,
                        "looses": 0,
                        "rec": 0}
        self.visited = []

    def train(self, player):
        self.field = Field()
        if player == 1:
            self.p2.stateTable = loadValues("p2")
        else:
            self.p1.stateTable = loadValues("p1")

        for a in range(9):
            if self.field.field[a] != 0:
                continue
            f = deepcopy(self.field)
            f.field[a] = 1
            print(self.trainLoop(f, player, -1))

    def trainLoop(self, field, player, turn):
        reward = 0
        if field.isFinished():
            if field.getWinner() == player:
                reward = 5
            elif field.getWinner() == -player:
                reward = -20
            else:
                reward = -1
        elif str(field.field) in self.p1.stateTable and player == 1:
            reward = self.p1.stateTable[str(field.field)]
        elif str(field.field) in self.p2.stateTable and player == -1:
            reward = self.p2.stateTable[str(field.field)]
        else:
            returns = []
            weights = []
            for a in range(9):
                if field.field[a] != 0:
                    continue
                f = deepcopy(field)
                f.field[a] = turn
                returns.append(0.8*self.trainLoop(f, player, -turn))
                #returns.append(0.5*self.trainLoop(f, player, -turn))
                w = 1#np.abs(returns[-1])
                if player == -turn:
                    try:
                        if player == 1:
                            w = self.p1.stateTable[str(f.field)]
                            #w = np.abs(self.p1.stateTable[str(f.field)])
                        else:
                            w = self.p2.stateTable[str(f.field)]
                            #w = np.abs(self.p2.stateTable[str(f.field)])

                    except KeyError:
                        w = 1
                weights.append(w)
                #returns[-1] = returns[-1] * w
            weights = softMax(weights)
            returns = [returns[a]*weights[a] for a in range(len(weights))]
            reward = sum(returns)
            #reward = sum(returns)/sum(weights)
        if player != turn:
            if player == 1:
                self.p1.stateTable[str(field.field)] = reward
            else:
                self.p2.stateTable[str(field.field)] = reward
        return reward

    def loadFiles(self):
        self.p1.stateTable = loadValues("p1")
        self.p2.stateTable = loadValues("p2")

    def doAction(self, action, symbol):
        if self.field.field[action] == 0:
            self.field.field[action] = symbol
            return True
        else:
            return False

    def play(self, start, **kwargs):
        self.p2.stateTable = loadValues("p2")
        self.p1.stateTable = loadValues("p1")

        if "p1" in kwargs:
            self.p1.stateTable = loadValues(kwargs["p1"])
        if "p2" in kwargs:
            self.p2.stateTable = loadValues(kwargs["p2"])

        if start:
            turn = -1
            while not self.field.isFinished():
                if turn == 1:
                    action = self.p2.choose(self.field.field)
                    if not self.doAction(action, -1):
                        print("Agent choose invalid action")
                else:
                    print(self.field.field[0:3])
                    print(self.field.field[3:6])
                    print(self.field.field[6:9])
                    print()

                    action = int(input()) - 1
                    valid = self.doAction(action, 1)
                    while not valid:
                        print("invalid action")
                        action = int(input()) - 1
                        valid = self.doAction(action, 1)
                turn = -turn
            print(self.field.field[0:3])
            print(self.field.field[3:6])
            print(self.field.field[6:9])
            if self.field.getWinner() == -1:
                print("you lost")
            elif self.field.getWinner() == 1:
                print("you won")
            else:
                print("draw")
        else:
            turn = 1
            while not self.field.isFinished():
                if turn == 1:
                    action = self.p1.choose(self.field.field)
                    if not self.doAction(action, 1):
                        print("Agent choose invalid action")
                else:
                    print(self.field.field[0:3])
                    print(self.field.field[3:6])
                    print(self.field.field[6:9])
                    print()

                    action = int(input()) - 1
                    valid = self.doAction(action, -1)
                    while not valid:
                        print("invalid action")
                        action = int(input()) - 1
                        valid = self.doAction(action, -1)
                turn = -turn
            print(self.field.field[0:3])
            print(self.field.field[3:6])
            print(self.field.field[6:9])
            if self.field.getWinner() == 1:
                print("you lost")
            elif self.field.getWinner() == -1:
                print("you won")
            else:
                print("draw")

    def run(self):
        turn = 1
        self.loadFiles()
        while not self.field.isFinished():
            if turn == 1:
                action = self.p1.choose(self.field.field)
                if not self.doAction(action, 1):
                    print("Agent choose invalid action")
            else:
                action = self.p2.choose(self.field.field)
                if not self.doAction(action, -1):
                    print("Agent choose invalid action")
            turn = -turn
            print(self.field.field[0:3])
            print(self.field.field[3:6])
            print(self.field.field[6:9])
            print()

        if self.field.getWinner() == 1:
            print("player 1 won")
        elif self.field.getWinner() == -1:
            print("player 1 won")
        else:
            print("draw")

    def testLoop(self, field, player, agent, turn):
        self.counter["rec"] += 1
        if str(field.field) in self.visited:
            pass#return
        else:
            self.visited.append(str(field.field))

        if field.isFinished():
            winner = field.getWinner()
            if winner == player:
                self.counter["wins"] += 1
            elif winner == -player:
                print(field.field[0:3])
                print(field.field[3:6])
                print(field.field[6:9])
                print()
                self.counter["looses"] += 1
            else:
                self.counter["draws"] += 1
            return

        if player == turn:
            action = agent.choose(field.field)
            f = deepcopy(field)
            f.field[action] = turn
            self.testLoop(f, player, agent, -turn)

        else:
            for a in range(9):
                if field.field[a] == 0:
                    f = deepcopy(field)
                    f.field[a] = turn
                    self.testLoop(f, player, agent, -turn)

    def test(self, file):
        self.field = Field()
        if "p1" in file:
            player = 1
            self.p1.stateTable = loadValues(file)
            agent = self.p1
        else:
            player = -1
            self.p2.stateTable = loadValues(file)
            agent = self.p2

        turn = 1
        if player == -1:
            for a in range(9):
                if self.field.field[a] == 0:
                    f = deepcopy(self.field)
                    f.field[a] = 1
                    self.testLoop(f, player, agent, -turn)
        else:
            action = agent.choose(self.field.field)
            self.field.field[action] = 1
            self.testLoop(self.field, player, agent, -turn)

        print(f'{self.counter["wins"] + self.counter["draws"] + self.counter["looses"]} matches played')
        print(f'won: {self.counter["wins"]}')
        print(f'draw: {self.counter["draws"]}')
        print(f'lost: {self.counter["looses"]}')


