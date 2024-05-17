import time
import Goban
import random
from playerInterface import *

N_PROMISING_MOVES = 10
TIME_MONTE_CARLO = 30
TOTAL_TIME = 1800
W_SCORE = 1
W_CAPTURE = 1
W_LIBERTY = 2

class myPlayer(PlayerInterface):
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._move_played_count = 0
        self._starting_time = time.time()

    def getPlayerName(self):
        return "GoGoGadget"
    
    def strong_heuristic(self, board: Goban.Board) -> int:
        score = board.compute_score()
        white_lib = Goban.Board.calculate_liberties(board)[Goban.Board._WHITE]
        black_lib = Goban.Board.calculate_liberties(board)[Goban.Board._BLACK]
        
        total_score = sum(score)
        total_capture = board._capturedBLACK + board._capturedWHITE
        total_lib = white_lib + black_lib

        if self._mycolor == Goban.Board._WHITE:
            return W_SCORE*(score[1] - score[0]) + W_CAPTURE*(board._capturedWHITE - board._capturedBLACK) + W_LIBERTY*(white_lib - black_lib)
        return W_SCORE*(score[0] - score[1]) + W_CAPTURE*(board._capturedBLACK - board._capturedWHITE) + W_LIBERTY*(black_lib - white_lib)
    
    # idée : changer evaluate (ou ses poids) en fct de l'avancée de la game
    def _evaluate(self, board: Goban.Board) -> int:
            if board.is_game_over():
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
            return self.strong_heuristic(board)
    
    def getPlayerMove(self):
        self._move_played_count += 1

        #Si le jeu est game-over on passe
        if self._board.is_game_over():
            return "PASS"
        
        #Si le jeu est en début de partie, on joue aléatoirement
        if self._move_played_count < 3:
            move = random.choice(self._board.legal_moves())
            self._board.push(move)
            return Goban.Board.flat_to_name(move)
        
        #On évalue les coups possibles et on explorera les meilleurs

        t1 = time.time()
        scored_moves = {}
        moves = self._board.legal_moves()
        # if(len(moves) <=10):
        #     depth = 3 #on explore plus profondément si on a peu de coups
        # else:
        #     depth = 2

        depth = 2

        if(self._board.get_number_of_stones() >  self._board._BOARDSIZE**2):
            W_LIBERTY = 2
        for move in moves:
            self._board.push(move)
            scored_moves[move] = self.alphabeta(self._board, self._mycolor, depth, float('-inf'), float('inf'))
            self._board.pop()
        print("Time of all minimax : ", time.time() - t1)

        promising_moves = []
        #garde les N_PROMISING_MOVES meilleurs coups
        for move in scored_moves.keys():
            if len(promising_moves) < N_PROMISING_MOVES:
                promising_moves.append(move)
            else:
                for i in range(min(N_PROMISING_MOVES, len(promising_moves))):
                    if scored_moves[move] > scored_moves[promising_moves[i]]:
                        promising_moves[i] = move
                        break


        scored_prom_moves = {}
        #initialiser le dictionnaire avec les coups prometteurs et des scores nuls
        for move in promising_moves:
            scored_prom_moves[move] = 0

        t = time.time()
        i=0
        j=0
        #monte carlo sur les coups prometteurs
        while(time.time() - t < TIME_MONTE_CARLO*(1 - (time.time() - self._starting_time)/TOTAL_TIME)):
            i = (i+1) % min(N_PROMISING_MOVES, len(promising_moves))
            if(i==0):
                j+=1
            move = promising_moves[i]
            self._board.push(move)
            scored_prom_moves[move] += self.monteCarlo(self._board, self._mycolor, depth = 0)
            self._board.pop()

        #statistiques, on divise les scores par le nombre de fois où on a exploré le coup
        for move in promising_moves[:i]:
            scored_prom_moves[move] /= max(j,1)
        for move in promising_moves[i:]:
            scored_prom_moves[move] /= j+1

        best_move = promising_moves[0]
        for m in promising_moves:
            if scored_prom_moves[m] > scored_prom_moves[best_move]:
                best_move = m
    
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

    def minimax(self, board : Goban.Board, current_player : int, 
            depth : int) -> int :
        
        #gestion d'urgence pour éviter de dépasser le temps
        if(time.time() - self._starting_time > TOTAL_TIME - 10):
            print("Gestion d'urgence du minimax déclenchée")
            return 0
    
        if board.is_game_over() :
            if(board.winner() == self._mycolor):
                return 100000
            else:
                return -100000
            
        if(depth == 0):
            return self._evaluate(board)

        moves = board.legal_moves()
        scores = []
        for move in moves :
            board.push(move)
            scores.append(self.minimax(board, Goban.Board.flip(current_player), depth - 1))
            board.pop()

        if current_player == self._mycolor:
            return max(scores)
        else:
            return min(scores)

    def alphabeta(self, board : Goban.Board, current_player : int, 
            depth : int, alpha : int, beta : int) -> int :
        
        #gestion d'urgence pour éviter de dépasser le temps
        if(time.time() - self._starting_time > TOTAL_TIME - 10):
            print("Gestion d'urgence de l'alphabeta déclenchée")
            return 0
    
        if board.is_game_over() :
            if(board.winner() == self._mycolor):
                return 100000
            else:
                return -100000
            
        if(depth == 0):
            return self._evaluate(board)

        moves = board.legal_moves()
        if current_player == self._mycolor:
            max_score = float('-inf')
            for move in moves:
                board.push(move)
                score = self.alphabeta(board, Goban.Board.flip(current_player), depth - 1, alpha, beta)
                board.pop()
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in moves:
                board.push(move)
                score = self.alphabeta(board, Goban.Board.flip(current_player), depth - 1, alpha, beta)
                board.pop()
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
            return min_score


    #La terminaison en un temps acceptable n'est pas garantie
    #necessité d'ajouter des gardes-fous
    def monteCarlo(self, board : Goban.Board, current_player : int, depth : int) -> int :

        #securité d'urgence pour éviter de dépasser le temps
        if(time.time() - self._starting_time > TOTAL_TIME- 10):
            print("Gestion d'urgence du monte carlo déclenchée")
            return 0

        if board.is_game_over():
            if(board.winner() == self._mycolor):
                print("Monte Carlo hit a winning leaf node")
                return 1
            else:
                print("Monte Carlo hit a losing leaf node")
                return 0

        #print("Monte Carlo depth : ", depth)

        moves = board.legal_moves()
        move = random.choice(moves)
        board.push(move)
        score = self.monteCarlo(board, Goban.Board.flip(current_player), depth + 1)
        board.pop()
        return score