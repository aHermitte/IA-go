from playerInterface import *
import Goban
import alpha_beta
import random

class myPlayer(PlayerInterface):
    
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._moved_played = 0

    def getPlayerName(self):
        return "Alpha Beta Player"
    
    # TODO: améliorer l'efficacité du choix du meilleur coup (en temps et en pertinence)
    def getPlayerMove(self):
        if self._moved_played < 5:
            self._moved_played += 1
            print("JE JOUE ALEATOIREMENT")
            move = random.choice(self._board.legal_moves())
            self._board.push(move)
            return Goban.Board.flat_to_name(move)
        print("JE VAIS JOUER QUOI?")
        heuristics = []
        for move in self._board.legal_moves():
            self._board.push(move)
            heuristic = alpha_beta.max_value(self._board, -10000, 10000, 2, self._evaluate)
            self._board.pop()
            heuristics.append((heuristic, move))
        
        print("HEURISTICS: ", heuristics)
        best_move = self._chooseBestMove(heuristics)
        print("JE JOUE ", Goban.Board.flat_to_name(best_move))
        self._board.push(best_move)
        return Goban.Board.flat_to_name(best_move)
    
    def _chooseBestMove(self, heuristics):
        max_heuristic = float('-inf')
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
    
    def _evaluate(self, board: Goban.Board) -> int:
        if board.is_game_over():
            print("GAME OVER")
            black_score , white_score = self._board.compute_score()
            if self._mycolor == Goban.Board._WHITE:
                if white_score > black_score:
                    return 100000
            else:
                if black_score > white_score:
                    return 100000
            return -100000
        print("EVALUATING")
        if (self._mycolor == Goban.Board._WHITE): 
            return board._nbWHITE - board._nbBLACK 
        else: 
            return board._nbBLACK - board._nbWHITE
        
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
    
    



    