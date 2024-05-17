import time
import Goban
import random
import alpha_beta_transformed as alpha_beta
from playerInterface import *

class myPlayer(PlayerInterface):
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._moved_played = 0

    def getPlayerName(self):
        return "Kom"
    
    def heuristic(self, board: Goban.Board) -> int:
        score = board.compute_score()
        if self._mycolor == Goban.Board._WHITE:
            return score[1] - score[0] + board._capturedWHITE - board._capturedBLACK
        return score[0] - score[1] + board._capturedBLACK - board._capturedWHITE
    
    def _evaluate(self, board: Goban.Board) -> int:
            if board.is_game_over():
                print("GAME OVER")
                black_score , white_score = self._board.compute_score()
                if self._mycolor == Goban.Board._WHITE:
                    if white_score > black_score:
                        return 100000
                    else :
                        return -100000
                if self._mycolor == Goban.Board._BLACK:
                    if black_score > white_score:
                        return 100000
                    else:
                        return +100000
            return self.heuristic(board)
    
    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        
        if self._moved_played < 5:
            self._moved_played += 1
            print("JE JOUE ALEATOIREMENT")
            move = random.choice(self._board.legal_moves())
            self._board.push(move)
            return Goban.Board.flat_to_name(move)
        
        print("JE VAIS JOUER QUOI?")
        scores = []
        for move in self._board.legal_moves():
            self._board.push(move)
            score = alpha_beta.max_value(self._board, -10000, 10000, 3, 3, self._evaluate)
            self._board.pop()
            scores.append((score, move))        

        print("SCORES: ", scores)
        best_move = self._chooseBestMove(scores)
        print("JE JOUE ", Goban.Board.flat_to_name(best_move))
        self._board.play_move(best_move)
        return Goban.Board.flat_to_name(best_move)
    
    def _chooseBestMove(self, scores):
        max_score = float('-inf')
        best_move = None
        all_equal = True
        for score, move in scores:
            if score > max_score:
                max_score = score
                best_move = move
                all_equal = False
            elif score == max_score:
                all_equal = True
        if all_equal:
            best_move = scores[random.randint(0, len(scores)-1)][1]        
        return best_move
    
    def playOpponentMove(self, move):
        print("Opponent played ", move, "i.e. ", move) # New here
        # the board needs an internal representation to push the move. Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)
    
    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(")