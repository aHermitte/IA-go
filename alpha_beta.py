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