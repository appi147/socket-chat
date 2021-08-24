import random


class Card():
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value} of {self.suit}"


class Deck():
    _values = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    _suits = ["Spades", "Diamonds", "Clubs", "Hearts"]
    cards = []

    def __init__(self, mode="default"):
        if mode == "29":
            self._values = ["J", "9", "A", "10", "K", "Q", "8", "7"]
        else:
            pass
        self.cards = [Card(value, suit) for value in self._values for suit in self._suits]

    def shuffle(self):
        random.shuffle(self.cards)

def CardGame29():
    priority = {
        "J": 13,
        "9": 12,
        "A": 11,
        "10": 10,
        "K": 9,
        "Q": 8,
        "8": 7,
        "7": 6
    }

    points = {
        "J": 3,
        "9": 2,
        "A": 1,
        "10": 1,
        "K": 0,
        "Q": 0,
        "8": 0,
        "7": 0
    }

d = Deck("29")
for card in d.cards:
    print(card)
