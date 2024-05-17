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
import random

# probabilité d'explorer un noeud
# peut-être revoir si elle devrait evoluer autrement


#Actuellement le raisonnement est : plus on va profondément, moins on explore de coups
#On pourrait imaginer une fonction qui donne une probabilité de plus en plus grande d'explorer un noeud
#Ou meme qui est grande au début, puis diminue, puis augmente à nouveau
#On peut imaginer que les noeuds initiaux explorés varient en fct du nb de coups déjà joués
#On peut imaginer que noeuds initiaux + proba dans la profondeur varient en fct du temps restant
#Favoriser les explorations profonde en milieu de game

def probalistic_evaluate(depth, initial_depth) -> float:
    if(initial_depth-depth == 0):
        return 1
    else :                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        return 1/float(initial_depth-depth)**3

def max_value(board: Goban.Board, alpha: int, beta: int, depth: int, initial_depth : int, evaluate) -> int:
    if board.is_game_over() or depth == 0:
        return evaluate(board)
    for move in board.legal_moves():
        #plus on va profondément, moins on explore de coups
        if(random.random() < probalistic_evaluate(depth, initial_depth)):
            board.push(move)
            alpha = max(alpha, min_value(board, alpha, beta, depth-1, initial_depth, evaluate))
            board.pop()
            if alpha >= beta:
                return beta
    return alpha

def min_value(board: Goban.Board, alpha: int, beta: int, depth : int, initial_depth : int, evaluate) -> int:
    if board.is_game_over() or depth == 0:
        return evaluate(board)
    for move in board.legal_moves():
        if(random.random() < probalistic_evaluate(depth, initial_depth)):
            board.push(move)
            beta = min(beta, max_value(board, alpha, beta, depth-1, initial_depth, evaluate))
            board.pop()
            if alpha >= beta:
                return alpha
    return beta