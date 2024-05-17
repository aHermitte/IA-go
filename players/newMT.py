import Goban
from playerInterface import PlayerInterface
import numpy as np
import random

class MCTSNode:
    cache = {}

    def __init__(self, move=None, parent=None, board=None, move_number=0):
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.board = board if board else None
        self.untried_moves = self.filter_and_evaluate_moves(board, move_number) if board else []

    @staticmethod
    def get_cache_key(move, move_number):
        return (move, move_number)

    @staticmethod
    def get_from_cache(move, move_number):
        return MCTSNode.cache.get(MCTSNode.get_cache_key(move, move_number))

    @staticmethod
    def update_cache(move, move_number, score):
        MCTSNode.cache[MCTSNode.get_cache_key(move, move_number)] = score

    @staticmethod
    def clear_cache():
        MCTSNode.cache.clear()

    def evaluate_liberties(self, board):
        black_liberties = 0
        white_liberties = 0
        visited = set()  

        for position in range(Goban.Board._BOARDSIZE ** 2):
            if position in visited or board._board[position] == Goban.Board._EMPTY:
                continue  

            liberties, group = self.calculate_group_liberties(board, position)
            visited.update(group)  

            if board._board[position] == Goban.Board._BLACK:
                black_liberties += liberties
            elif board._board[position] == Goban.Board._WHITE:
                white_liberties += liberties

        return black_liberties, white_liberties

    def calculate_group_liberties(self, board, start_position):
        liberties = set()
        group = set()
        stack = [start_position]
        color = board._board[start_position]

        while stack:
            position = stack.pop()
            if position in group:
                continue
            group.add(position)

            for neighbor in board._get_neighbors(position):
                if board._board[neighbor] == Goban.Board._EMPTY:
                    liberties.add(neighbor)
                elif board._board[neighbor] == color and neighbor not in group:
                    stack.append(neighbor)

        return len(liberties), group


    def find_empty_group(self, board, start_position, visited):
        empty_group = set()
        edge_stones = []
        stack = [start_position]

        while stack:
            position = stack.pop()
            if position in visited:
                continue
            visited.add(position)
            empty_group.add(position)

            for neighbor in board._get_neighbors(position):
                if board._board[neighbor] == Goban.Board._EMPTY and neighbor not in visited:
                    stack.append(neighbor)
                elif board._board[neighbor] in (Goban.Board._BLACK, Goban.Board._WHITE):
                    edge_stones.append(board._board[neighbor])

        return empty_group, edge_stones

    def extension_du_territoire(self, board):
        territory_score = 0
        visited = set()
        for position in range(Goban.Board._BOARDSIZE ** 2):
            if position in visited or board._board[position] != Goban.Board._EMPTY:
                continue
            # Trouver toutes les cases vides connectées
            empty_group, edge_stones = self.find_empty_group(board, position, visited)
            visited.update(empty_group)
            # Compter la dominance de couleur autour du groupe vide
            if len(edge_stones) == edge_stones.count(Goban.Board._BLACK):
                territory_score += len(empty_group)  # Plus de points si entouré uniquement par des pierres noires
            elif len(edge_stones) == edge_stones.count(Goban.Board._WHITE):
                territory_score -= len(empty_group)  # Plus de points négatifs si entouré uniquement par des pierres blanches
        return territory_score

    def does_it_close_losange(self, board, move, player_color):
        if player_color == Goban.Board._BLACK:
            opponent_color = Goban.Board._WHITE
        else:
            opponent_color = Goban.Board._BLACK
        
        move_str = board.move_to_str(move)

        # position de 0 à 63
        if (move_str[0] == "G" or move_str[0] == "H" or move_str[1] == "8" or move_str[1] == "1"):
            close_from_left = False
        else: 
            close_from_left = board[move + 2] == opponent_color and board[move + 1 - Goban.Board._BOARDSIZE] == opponent_color and board[move + 1 + Goban.Board._BOARDSIZE] == opponent_color

        if (move_str[0] == "A" or move_str[0] == "B" or move_str[1] == "8" or move_str[1] == "1"):
            close_from_right = False
        else:
            close_from_right = board[move - 2] == opponent_color and board[move - 1 - Goban.Board._BOARDSIZE] == opponent_color and board[move - 1 + Goban.Board._BOARDSIZE] == opponent_color
        
        if (move_str[1] == "7" or move_str[1] == "8" or move_str[0] == "A" or move_str[0] == "H"):
            close_from_top = False
        else:
            close_from_top = board[move - 1 + Goban.Board._BOARDSIZE] == opponent_color and board[move + 1 + Goban.Board._BOARDSIZE] == opponent_color and board[move + 2 * Goban.Board._BOARDSIZE] == opponent_color
        
        if (move_str[1] == "1" or move_str[1] == "2" or move_str[0] == "A" or move_str[0] == "H"):
            close_from_bottom = False
        else:
            close_from_bottom = board[move - 1 - Goban.Board._BOARDSIZE] == opponent_color and board[move + 1 - Goban.Board._BOARDSIZE] == opponent_color and board[move - 2 * Goban.Board._BOARDSIZE] == opponent_color

        return close_from_right or close_from_left or close_from_top or close_from_bottom

    def detect_special_structures(self, board, move, player_color):
        score = 0
        legal_move = board.legal_moves()

        for movea in legal_move:
            if self.does_it_close_losange(board, movea, player_color):
                score -= 3
        return score


    def stone_num(self, board):
        return board._nbBLACK, board._nbWHITE
    
    def early_game(self, distance_to_center, territory_score, liberties, captured_stones, structure_score):
        return -0.1 * distance_to_center + 0.3 * liberties + 0.1 * territory_score + 4 * captured_stones + 0.5 * structure_score

    def mid_game(self, distance_to_center, territory_score, liberties, captured_stones, structure_score):
        return 0.5 * territory_score + 0.4 * liberties + 4 * captured_stones - 0.1 * distance_to_center + 1.5 * structure_score

    def end_game(self, territory_score, liberties, captured_stones, structure_score):
        return territory_score + 2 * liberties + 4 * captured_stones + 1 * structure_score


    def filter_and_evaluate_moves(self, board, move_number):
        if board.is_game_over():
            return []

        center = Goban.Board._BOARDSIZE // 2
        possible_moves = board.legal_moves()
        evaluated_moves = []
        liberties = float("inf")
        score = float("-inf")

        for move in possible_moves:
            cached_result = MCTSNode.get_from_cache(move, move_number)
            if cached_result:
                score = cached_result
            else:
                init_black, init_white = self.stone_num(board)
                board.push(move)

                black_stones, white_stones = self.stone_num(board)
                black_liberties, white_liberties = self.evaluate_liberties(board)
                distance_to_center = max(abs((move % Goban.Board._BOARDSIZE) - center), abs((move // Goban.Board._BOARDSIZE) - center))
                territory_score = self.extension_du_territoire(board)
                if (move_number > 6):
                    structure_score = self.detect_special_structures(board, move, board.next_player())
                else:
                    structure_score = 0

                board.pop()

                if (board.next_player() == Goban.Board._BLACK):
                    captured_stones = init_white - white_stones
                    liberties = black_liberties - white_liberties
                else:
                    captured_stones = init_black - black_stones
                    liberties = white_liberties - black_liberties

                if (move_number <= 10):
                    score = self.early_game(distance_to_center, territory_score, liberties, captured_stones, structure_score)
                elif (move_number <= 35):
                    score = self.mid_game(distance_to_center, territory_score, liberties, captured_stones, structure_score)
                else:
                    score = self.end_game(territory_score, liberties, captured_stones, structure_score)

                MCTSNode.update_cache(move, move_number, score)

            evaluated_moves.append((score, move))

        evaluated_moves.sort(reverse=True, key=lambda x: x[0])
        top_moves = [move for _, move in evaluated_moves[:20]]
        return top_moves



    def select_child(self):
        return max(self.children, key=lambda c: c.wins / c.visits + np.sqrt(2 * np.log(self.visits) / c.visits))

    def expand(self, move_number):
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        new_board = Goban.Board(self.board)
        new_board.push(move)
        child_node = MCTSNode(move=move, parent=self, board=new_board, move_number=move_number)
        self.children.append(child_node)
        return child_node

    def simulate(self, move_number):
        trial_board = Goban.Board(self.board)
        simulation_move_number = move_number 

        while not trial_board.is_game_over():
            possible_moves = self.filter_and_evaluate_moves(trial_board, simulation_move_number)
            if possible_moves:
                move = random.choice(possible_moves)
                trial_board.push(move)
                simulation_move_number += 1 
            else:
                break 

        return trial_board.result()


    def backpropagate(self, result):
        self.visits += 1
        if (self.board.next_player() == Goban.Board._BLACK and result == "0-1") or (self.board.next_player() == Goban.Board._WHITE and result == "1-0"):
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result)


class myPlayer(PlayerInterface):
    def __init__(self):
        self.board = Goban.Board()
        self.root = MCTSNode(board=self.board)
        self._mycolor = None
        self.move_number = 0

    def getPlayerName(self):
        return "Monte-Carlo Player"

    def best_move(self):
        for i in range(3000):
            # print("\033[0;31m", i,  "\033[0m")
            node = self.root
            while node.children:
                node = node.select_child()
            if not node.board.is_game_over():
                node = node.expand(move_number=self.move_number)
            result = node.simulate(move_number=self.move_number)
            node.backpropagate(result)
        best_child = max(self.root.children, key=lambda c: c.visits)
        return best_child.move

    def update_root(self, move):
        for child in self.root.children:
            if child.move == move:
                self.root = child
                return
        self.root = MCTSNode(board=self.board)

    def getPlayerMove(self):
        print("looking for a move")
        if self.board.is_game_over():
            return "PASS"
        move = self.best_move()
        self.board.push(move)
        self.move_number += 1
        self.update_root(move)
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        self.board.push(Goban.Board.name_to_flat(move))
        self.update_root(Goban.Board.name_to_flat(move))
        self.move_number += 1

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!")
        else:
            print("I lost!")
        MCTSNode.clear_cache()
