# Fonction M axV alue(etat, α, β)) ◃ Niveau AMI
    # Si EstF euille(etat) Alors
    #   Retourner evalue(etat) ◃ Évaluation heuristique
    # Fin Si
    # Pour Tout successeur s de etat Faire
    #   α ← max(α,M inV alue(s, α, β))
    #   Si α ≥ β Alors ◃ Coupe β
    #       Retourner β
    #   Fin Si
    # Fin Pour
    # Retourner α
# Fin Fonction

# Fonction M inV alue(etat, α, β))
    # Si EstF euille(etat) Alors
    #   Retourner evalue(etat) ◃ Niveau ENNEMI
    # Fin Si
    # Pour Tout successeur s de etat Faire
    #   β ← min(β,M axV alue(s, α, β))
    #   Si α ≥ β Alors ◃ Coupe α
    #       Retourner α
    #   Fin Si
    # Fin Pour
    # Retourner β
# Fin Fonction


# Ce fichier implémente les fonctions MaxValue et MinValue de l'algorithme Alpha-Beta du cours
# TODO: Améliorer la fonction d'évaluation heuristique

import Goban

def max_value(board: Goban.Board, alpha: int, beta: int, depth: int, evaluate) -> int:
    if board.is_game_over() or depth == 0:
        return evaluate(board)
    for move in board.legal_moves():
        board.push(move)
        alpha = max(alpha, min_value(board, alpha, beta, depth-1, evaluate))
        board.pop()
        if alpha >= beta:
            return beta
    return alpha

def min_value(board: Goban.Board, alpha: int, beta: int, depth, evaluate) -> int:
    if board.is_game_over() or depth == 0:
        return evaluate(board)
    for move in board.legal_moves():
        board.push(move)
        beta = min(beta, max_value(board, alpha, beta, depth-1, evaluate))
        board.pop()
        if alpha >= beta:
            return alpha
    return beta