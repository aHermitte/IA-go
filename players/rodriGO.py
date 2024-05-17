# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time, math, random
import Goban 
from Goban import Board
from random import choice,shuffle
from playerInterface import *
import multiprocessing
isLeaf = lambda b, depth: depth == 0 or b.is_game_over()

##TOTAL_TIME IN SECONDS (29 min (not 30 to avoid timeout))
TOTAL_TIME=15*60
FINDER_NUMBER= 3

global remaining_time 
remaining_time = TOTAL_TIME



class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!
    
    '''
    def flat_to_coord(self, flat):
        return Goban.Board.name_to_coord(Goban.Board.flat_to_name(flat))

    def coord_to_flat(self, coord):
        return Goban.Board.name_to_flat(Goban.Board.coord_to_name(coord))

    ## Heuristic aux functions
    def get_liberty(self,b: Goban.Board, flat):
        (i,j) = self.flat_to_coord(flat)
        liberties = 0
        board = b.get_board()
        if i > 0 and board[self.coord_to_flat((i-1,j))] == 0:
            liberties += 1
        if i < Board._BOARDSIZE - 1 and board[self.coord_to_flat((i+1,j))] == 0:
            liberties += 1
        if j > 0 and board[self.coord_to_flat((i,j-1))] == 0:
            liberties += 1
        if j < Board._BOARDSIZE - 1 and board[self.coord_to_flat((i,j+1))] == 0:
            liberties += 1
        return liberties
    
    def get_liberties(self, b: Goban.Board):
        board = b.get_board()
        black_liberties = 0
        white_liberties = 0
        for i in range(Board._BOARDSIZE):
            for j in range(Board._BOARDSIZE):
                if board[self.coord_to_flat((i,j))] == 1: #Black
                    black_liberties += self.get_liberty(b, self.coord_to_flat((i,j)))
                elif board[self.coord_to_flat((i,j))] == 2: #White
                    white_liberties += self.get_liberty(b, self.coord_to_flat((i,j)))
        return (black_liberties, white_liberties)
    

    def get_stones(self, b: Goban.Board, color):
        board = b.get_board()
        stones = []
        for i in range(Board._BOARDSIZE):
            for j in range(Board._BOARDSIZE):
                if board[self.coord_to_flat((i,j))] == color:
                    stones.append((i,j))
        return stones

        


    

    #######
    def heuristic(self, b : Goban.Board):
        if b.is_game_over():
            if b.result() == "1-0" and self._mycolor == Goban.Board._BLACK:
                return math.inf
            elif b.result() == "0-1" and self._mycolor == Goban.Board._WHITE:
                return -math.inf
            elif b.result() == "1-0" and self._mycolor == Goban.Board._WHITE:
                return -math.inf
            elif b.result() == "0-1" and self._mycolor == Goban.Board._BLACK:
                return math.inf
            else:
                return 0
        (b_score,w_score) = b.compute_score()
        diff_black_pieces = b.diff_stones_board()
        diff_captured_black = b.diff_stones_captured()
        (black_liberties, white_liberties) = self.get_liberties(b)

        ## Score calculation

        black_score_b = b_score - w_score + 3*diff_black_pieces + 3*diff_captured_black + black_liberties - white_liberties 
        white_score_b = w_score - b_score - 3*diff_black_pieces - 3*diff_captured_black - white_liberties + black_liberties 
        black_score_w = w_score - b_score + 3*diff_black_pieces + 3*diff_captured_black + white_liberties - black_liberties 
        white_score_w = b_score - w_score - 3*diff_black_pieces - 3*diff_captured_black - black_liberties + white_liberties 


        
        if self._mycolor == 1:
            if self._mycolor == b._nextPlayer:
                return black_score_b
            else:
                return white_score_b
        else:
            if self._mycolor == b._nextPlayer:
                return white_score_w
            else:
                return black_score_w
                    
        


    def minVar(self, a,b):
        return a if a <= b else b

    def maxVar(self, a, b):
        return a if a >= b else b


    def MaxMinAlphaBeta(self, b:Goban.Board, depth, alpha, beta):
        if isLeaf(b, depth):
            return self.heuristic(b)
        best = -math.inf
        for m in b.generate_legal_moves():
            b.push(m)
            best = self.maxVar(best, self.MinMaxAlphaBeta(b, depth-1, alpha, beta))
            b.pop()
            alpha = self.maxVar(alpha, best)
            if alpha >= beta:
                break
        return best

    def MinMaxAlphaBeta(self, b: Goban.Board, depth, alpha, beta):
        if isLeaf(b, depth):
            return self.heuristic(b)
        worse = math.inf
        for m in b.generate_legal_moves():
            b.push(m)
            worse = self.minVar(worse,self.MaxMinAlphaBeta(b, depth-1, alpha, beta))
            b.pop()
            beta = self.minVar(beta, worse)
            if alpha >= beta:
                break
        return worse
    def playBestMove(self, b: Goban.Board, depth, bestScore, bestMove):
        ##Instance variable to store the best move
        legals = b.legal_moves()
        shuffle(legals)
        bestScore.value = -float('inf')
        bestMove.value =  choice(legals)
        print("Searching for best move")
        for m in legals:
            b.push(m)
            searching_board = Goban.Board(b)
            score = self.MinMaxAlphaBeta(searching_board, depth, -float('inf'), float('inf'))
            b.pop()
            # print("Move : ", m, "Score : ", score)
            if score >= bestScore.value:
                print("Better Score oldbest : ",bestScore.value, "withMove", bestMove.value)
                if (score == bestScore.value):
                    if random.randint(0, 1) == 0:
                        bestScore.value = score
                        bestMove.value = m
                else:
                    bestScore.value = score
                    bestMove.value = m
            if bestScore.value == float('inf'):
                print("BREAK Best move : ", bestMove.value, "Score : ", bestScore.value)
                break


    def decide_time_to_play(self, b: Goban.Board, timeMax=10):
        """Algorithm to decide the time to play for this move, which won't exceed the timeMax given in parameter and based on the board and the remaining time."""
        if self._turn < 20:
            return timeMax
        else:
            return self._remaining_time / 30

    def deroulementIA(self, b:Goban.Board, timeMax=10):
        print("----------")
        if b.is_game_over():
            print("GAME OVER")
            return "PASS"
        #Define timeMax
        timeMax = self.decide_time_to_play(b, timeMax)

        ##Initialise variables
        start = time.time()
        i = 2
        bestMove = None
        bestScore = -float('inf')
        bestS = multiprocessing.Value('d', -float('inf'))
        bestM = multiprocessing.Value('i', 0)
        
        ##Sacrifice 10% of the time for a deep deep search in the first move
        # print("Digging deep ....")
        # timeout = timeMax * 0.2
        # thread = multiprocessing.Process(target=self.playBestMove, args=(b, 3, bestS, bestM))
        # thread.start()
        # thread.join(timeout)
        # if thread.is_alive():
        #     thread.terminate()
            # thread.join()
        # print("Best move: ", bestM.value, "Score: ", bestS.value)

        bestMove = bestM.value
        bestScore = bestS.value



        ##Iterative deepening
        while time.time() - start < timeMax:
                testing_board = Goban.Board(b)
                try:
                    timeout = timeMax - (time.time() - start)
                    print("Remaining time: ", timeout)
                    threads = []
                    for i in range(FINDER_NUMBER):
                        threads.append(multiprocessing.Process(target=self.playBestMove, args=(testing_board, i, bestS, bestM)))
                        threads[i].start()

                    for i in range(1, FINDER_NUMBER):
                        threads[i].join(timeout)
                        if threads[i].is_alive():
                            threads[i].terminate()
                            threads[i].join()

                    if bestS.value == float('inf'):
                        print("BREAK Best move: ", bestM, "Score: ", bestS)
                        bestMove = bestM.value
                        break
                    if bestS.value >= bestScore:
                        bestMove = bestM.value
                        bestScore = bestS.value
                    i += 1
                except Exception as e:
                    print("Error: ", e)
                    break
               
        self._remaining_time -= (time.time() - start)
        return bestMove

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._secondLastPlayerHasPassed = False

    def getPlayerName(self):
        return "rodriGO"


    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
        
        ## Check double pass
        if self._board._lastPlayerHasPassed and self._secondLastPlayerHasPassed:
            return "PASS"
        else:
            self._secondLastPlayerHasPassed = self._board._lastPlayerHasPassed
        move = self.deroulementIA(self._board,timeMax=10)
        self._board.push(move)

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")

        print("Liberties : ",str(self.get_liberties(self._board)))

        self._board.prettyPrint()
        self._turn += 1
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 
        self._turn += 1

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)
        self._remaining_time = TOTAL_TIME
        self._turn = 0

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")



