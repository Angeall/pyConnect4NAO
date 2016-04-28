from ai.connect4.game import Game
from ai.connect4.strategy.human import Human
from ai.connect4.strategy.naive import Naive

__author__ = 'Anthony Rouneau'

if __name__ == "__main__":
    game = Game()
    game.register_player(Naive())
    game.register_player(Human())
    game.play()

