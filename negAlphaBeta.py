# 1 : Fonction Negαβ(etat, α, β) ◃ Évaluation niveau AMI
# 2 :   Si EstF euille(etat) Alors ◃ Fin de partie ou horizon atteint
# 3 :       Retourner evalue(etat) ◃ Évaluation heuristique
# 4 :   Fin Si
# 5 :   Pour Tout successeur s de etat Faire
# 6 :       val ← −N egαβ(s, −β, −α)
# 7 :       Si val > α Alors
# 8 :           α ← val
# 9 :           Si α > β Alors
# 10 :              Retourner α ◃ Coupe
# 11 :          Fin Si
# 12 :      Fin Si
# 13 :   Fin Pour
# 14 :   Retourner α
# 15 : Fin Fonction

def negAlphaBeta(board, alpha, beta):
    if board.is_game_over():
        return board.evaluate()
    for move in board.legal_moves():
        val = -negAlphaBeta(board.push(move), -beta, -alpha)
        if val > alpha:
            alpha = val
            if alpha > beta:
                return alpha
    return alpha