from playerInterface import *
import Goban
import alpha_beta
import random

class testPlayer(PlayerInterface):
    
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "testPlayer"
    
    def getPlayerMove(self):
        print("JE VAIS JOUER QUOI?")
        heuristics = []
        for move in self._board.legal_moves():
            self._board.push(move)
            heuristic = alpha_beta.max_value(self._board, -10000, 10000, 1)
            self._board.pop()
            heuristics.append((heuristic, move))
        
        print("HEURISTICS: ", heuristics)
        best_move = self._chooseBestMove(heuristics)
        print("JE JOUE ", Goban.Board.flat_to_name(best_move))
        self._board.push(best_move)
        return Goban.Board.flat_to_name(best_move)
    
    def _chooseBestMove(self, heuristics):
        max_heuristic = -10000
        best_move = None
        all_equal = True
        for heuristic, move in heuristics:
            if heuristic > max_heuristic:
                max_heuristic = heuristic
                best_move = move
                all_equal = False
            elif heuristic == max_heuristic:
                all_equal = True
        if all_equal:
            best_move = heuristics[random.randint(0, len(heuristics)-1)][1]
        return best_move
    
    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 
        
    def newGame(self, color):
        print("J'arrive en mode ", color)
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)
        
    def endGame(self, winner):
        if self._mycolor == winner:
            print("Gg!!!")
        else:
            print("Bg...")
    
    



    