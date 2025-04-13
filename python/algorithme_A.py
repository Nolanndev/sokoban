import sys
from grid import *
from map import *
import time

# reconstruit le chemin complet pour finir le niveau
def reconstruct_path(actions, pere, map):
    resultat = []
    res = ""
    goal = map
    while goal is not None:
        resultat.append(actions[goal])
        goal = pere[goal]
    
    return list(reversed(resultat)), str(len(list(reversed(resultat)))-1) + " déplacements"

# vérifie si la map d'entrée est déjà dans open, et si oui on l'ajoute si sopn heuristique est plus basse que celle actuelle 
def check_doublon(open, current):
    for i in range(len(open)):
        if open[i].map.grid == current.map.grid:
            if open[i].heuristique > current.heuristique:
                open[i] = current
    return open



# trie la liste open par rapport à l'heuristique des maps qu'elle contient
def trier_heuristique(open):
    n = len(open)
    for i in range(n):
        for j in range(0,n-i-1):
            if open[j].heuristique > open[j+1].heuristique:
                open[j],open[j+1] = open[j+1],open[j]
    return open



# A*
def algorithmeA(grid):
    plateau = grid
    open = [Map(plateau)]
    pere = {open[0]:None}
    actions = {open[0]:None}
    while len(open) > 0:
        open = trier_heuristique(open)
        current = open.pop(0)
        if current.win_game():
            return reconstruct_path(actions, pere, current)
        
        if current.loose_game() == False:
            open = check_doublon(open, current)
            for direction in current.get_directions_upgrade():
                next = current.move(direction)
                if next not in open and next not in pere:
                    open.append(next)
                    pere[next] = current
                    actions[next] = direction
    return "Le niveau n'a pas de solution"



if __name__ == '__main__':
    debut = time.time()
    level = sys.path[0]+"/../niveaux/niveau002.txt"
    print(algorithmeA(Grid(level)))
    print("temps d'éxécution :", time.time() - debut, "secondes")
    