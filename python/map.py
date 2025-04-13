import copy
import dis
import sys
import os
import math

from turtle import distance

from pathlib import Path
path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))

from grid import Grid
from algorithme_A import *

class Map:
    """
    Classe qui permet de gérer les interactions entre l'utilisateur et la carte
    Arguments:
    -grid(objet Grid) correspond à la grille du niveau
    """

    def __init__(self, grid):
        self.map = grid
        self.position_x = grid.player_position()[0]
        self.position_y = grid.player_position()[1]
        self.pas = 0
        self.heuristique = 0
        # on inverse x et y pour des raisons de praticité

    def __hash__(self):
        return self.map.__hash__()

    def __eq__(self,other):
        for i in range(len(self.map.grid)):
            for j in range(len(self.map.grid[i])):
                if self.map.grid[i][j] != other.map.grid[i][j]:
                    return False
        return True
    
    def solve(self):
        """
        Méthode qui permer de resoudre la map actuelle grace à l'algorithme A*
        On retourne une liste avec les coups à joués pour résoudre le niveau si le niveau a une solution, 
        sinon on retourne "ce niveau n'as pas de solution"
        """
        return algorithmeA(self.map)

    def move(self,direction):  
        """
            Permet de déplacer le joueur dans la direction donnée en paramètres
            Cette fonction gère aussi les collisions entre :
                    - le joueur et les murs
                    - le joueur et une caisse
                    - la caisse et un mur
                    - le joueur et une cible
                    - la caisse et une cible
            argument:
            - direction (str) Correspond à la direction du mouvement("top","bottom","left","right)
            
            On retourne un objet Map une fois que le mouvement est effectue
            """
        
        map_copy = copy.deepcopy(self)
            
        next_position_x, next_position_x2 = map_copy.position_x, map_copy.position_x
        next_position_y, next_position_y2 = map_copy.position_y, map_copy.position_y
        # les next_position2 sont utile pour verifier si il a y un mur après les boites

        if direction == "right":
            next_position_y += 1
            next_position_y2 += 2
        elif direction == "left":
            next_position_y -= 1
            next_position_y2 -= 2
        elif direction == "top":
            next_position_x -= 1
            next_position_x2 -= 2
        elif direction == "bottom":
            next_position_x += 1
            next_position_x2 += 2

        if not map_copy.is_wall(next_position_x, next_position_y): # collision avec un mur
            if map_copy.is_box(next_position_x, next_position_y): # collision avec une caisse
                if map_copy.is_wall(next_position_x2, next_position_y2) or map_copy.is_box(next_position_x2, next_position_y2): # collision entre une caisse et un mur
                    return map_copy 
                elif map_copy.is_target(next_position_x2, next_position_y2): # collision entre une caisse et une cible
                    map_copy.map.grid_set_value(next_position_x2, next_position_y2, '*')
                else: # déplacement simple de la caisse
                    map_copy.map.grid_set_value(next_position_x2, next_position_y2, "$")
            if map_copy.is_player_on_target(map_copy.position_x, map_copy.position_y): # collision entre le joueur et une cible
                map_copy.map.grid_set_value(map_copy.position_x, map_copy.position_y, ".")
            else: # déplacement du joueur sans laisser de traces
                map_copy.map.grid_set_value(map_copy.position_x, map_copy.position_y, " ")
            map_copy.position_x, map_copy.position_y = next_position_x, next_position_y
            if map_copy.is_target(map_copy.position_x, map_copy.position_y) or map_copy.map.get_grid_position(map_copy.position_x, map_copy.position_y) == '*': # déplacement du joueur
                map_copy.map.grid_set_value(map_copy.position_x, map_copy.position_y, "+")
            else: # déplacement du joueur
                map_copy.map.grid_set_value(map_copy.position_x, map_copy.position_y, "@")
        
        map_copy.pas += 1
        map_copy.heuristique = map_copy.caisses_restantes() + map_copy.max_distance_joueur_caisse() + map_copy.pas
        # print("pas : ",map_copy.pas,", caisses :",map_copy.caisses_restantes(),", heuristique :",map_copy.heuristique, end="\r")
        return map_copy


    def is_target(self, x, y):
        """
        Permet de verifier si la casse donnée contient une cible
        arguments :
            -x (int) position x que l'on veut verifier dans la grille
            -y (int) position y que l'on veut verifier dans la grille
            
        return True si la case en (x,y) est une cible (".") sinon return False
        """
        
        if self.map.get_grid_position(x, y) == '.':
            return True
        elif self.map.get_grid_position(x,y) == '+':
            return True
        return False


    def is_wall(self, x, y):
        """
        Permet de verifier si la casse donnée contient un mur
        arguments :
            -x (int) position x que l'on veut verifier dans la grille
            -y (int) position y que l'on veut verifier dans la grille
            
        return True si la case en (x,y) est un mur ("#") sinon return False
        """
        
        if self.map.get_grid_position(x, y) == "#":
            return True
        return False


    def is_box(self, x, y):
        """
        Permet de verifier si la casse donnée contient une boite ou une boite sur une cible
        arguments :
            -x (int) position x que l'on veut verifier dans la grille
            -y (int) position y que l'on veut verifier dans la grille
            
        return True si la case en (x,y) est une boite ("$") ou une boite sur une cible ("*") sinon return False
        """
        
        if self.map.get_grid_position(x, y) == "$":
            return True
        elif self.map.get_grid_position(x,y) == "*":
            return True
        return False
    
    
    def is_floor(self,x,y):
        """
        Permet de verifier si la casse donnée est un sol ou une cible
        arguments :
            -x (int) position x que l'on veut verifier dans la grille
            -y (int) position y que l'on veut verifier dans la grille
            
        return True si la case en (x,y) est un sol (" ") ou une cible (".") sinon return False
        """
        if self.map.get_grid_position(x, y) == " ":
            return True
        elif self.map.get_grid_position(x, y) == ".":
            return True
        return False
    
    
    def is_player_on_target(self, x, y):
        """
        Permet de verifier si la casse donnée est le joueur sur une cible
        arguments :
            -x (int) position x que l'on veut verifier dans la grille
            -y (int) position y que l'on veut verifier dans la grille
            
        return True si la case en (x,y) est un joueur sur une boite ("+") sinon return False
        """
        if self.map.get_grid_position(x, y) == "+":
            return True
        return False
    
    
    def blocked_box(self, x, y):
        """
        Permet de vérifier si une caisse est bloqué dans un coin
        arguments :
        -x (int) position x à laquelle est la boite
        -y (int) position y à laquelle est la boite
        
        return True si la boite est bloquée sinon return False
        """
        
        if self.is_box(x, y):   
            # a chaque fois on verifie si la boite est entre deux murs un sur l'axe x et un sur l'axe y. Elle peut etre entre deux murs sur le même axe et être encore déplacable
            
            if self.is_wall(x, y-1) and self.is_wall(x-1, y):   
                return True
            elif self.is_wall(x-1, y) and self.is_wall(x, y+1):
                return True
            elif self.is_wall(x, y+1) and self.is_wall(x+1, y):
                return True
            elif self.is_wall(x+1, y) and self.is_wall(x, y-1):
                return True
            
            return False
        
        
    def get_directions(self):
        """
        Méthode qui retourne toute les directions, sous forme de liste, dans lesquelles le prochain pas n'est pas un mur
        """
        directions = []
        if not self.is_wall(self.position_x, self.position_y - 1):
            directions.append("left")
        if not self.is_wall(self.position_x, self.position_y + 1):
            directions.append("right")
        if not self.is_wall(self.position_x - 1, self.position_y):
            directions.append("top")
        if not self.is_wall(self.position_x + 1, self.position_y):
            directions.append("bottom")
        return directions
    
    def get_directions_upgrade(self):
        """
        Méthode qui retourne toute les directions, sous forme de liste, dans lesquelles il est possible d'aller.
        Cette méthode est plus précide que la méthode "get_directions"
        """
        directions = ["left","top","right","bottom"]
        directionsPossibles = []

        px,py = self.get_player_position()

        for direction in directions:

            if direction == "left":
                if self.is_floor(px,py-1):
                    directionsPossibles.append(direction)
                elif self.is_box(px,py-1):
                    if not self.is_box(px,py-2) and not self.is_wall(px,py-2):
                        directionsPossibles.append(direction)

            if direction == "right":
                if self.is_floor(px,py+1):
                    directionsPossibles.append(direction)
                elif self.is_box(px,py+1):
                    if not self.is_box(px,py+2) and not self.is_wall(px,py+2):
                        directionsPossibles.append(direction)

            if direction == "top":
                if self.is_floor(px-1,py):
                    directionsPossibles.append(direction)
                elif self.is_box(px-1,py):
                    if not self.is_box(px-2,py) and not self.is_wall(px-2,py):
                        directionsPossibles.append(direction)
            
            if direction == "bottom":
                if self.is_floor(px+1,py):
                    directionsPossibles.append(direction)
                elif self.is_box(px+1,py):
                    if not self.is_box(px+2,py) and not self.is_wall(px+2,py):
                        directionsPossibles.append(direction)
        
        return directionsPossibles
    
    def caisses_restantes(self):
        """
        Retourne le nombre de caisses qu'ils restent à placer sur la map
        """
        compteur = 0
        for i in self.map.grid:
            for j in i:
                if j == '$':
                    compteur += 1
        return compteur
    
    def distance_joueur_caisse(self):
        pp = self.get_player_position()
        distance = len(self.map.grid) ** 2 #permet d'avoir une distance supérieure à la + grande distance possible
        for caisse in self.map.box_position():
            n_dist = (pp[0]-caisse[0]) + (pp[1]-caisse[1])
            if n_dist < distance:
                distance = n_dist
        return distance

    def max_distance_joueur_caisse(self):
        pp = self.get_player_position()
        distance = 0
        for caisse in self.map.box_position():
            n_dist = (pp[0]-caisse[0]) + (pp[1]-caisse[1])
            if n_dist > distance:
                distance = n_dist
        return distance
    
    def perdu_coin(self):
        for x,y in self.map.box_position():
            if self.blocked_box(x, y):
                return True
        return False

    def perdu_ligne(self):
        for caisse in self.map.box_position():
            px,py = caisse
        
            ## Vérification top
            if self.map.grid[px-1][py] == '#':
                for case in self.map.grid[px]:
                    if case == "." or case == "+":
                        return False
                
                for case in self.map.grid[px-1]:
                    if case == " " or case == "@":
                        return False
                return True
            
            ## Vérification bas
            if self.map.grid[px+1][py] == '#':
                for case in self.map.grid[px]:
                    if case == "." or case == "+":
                        return False
                
                for case in self.map.grid[px+1]:
                    if case == " " or case == "@":
                        return False
                return True
            
            ## Vérification gauche
            if self.map.grid[px][py-1] == '#':
                for ligne in self.map.grid:
                    if ligne[py] == '.' or ligne[py] == "+":
                        return False
                for ligne in self.map.grid:
                    if ligne[py-1] == ' ' or ligne[py-1]=="@":
                        return False
                return True
            
            ## Vérification droite
            if self.map.grid[px][py+1] == '#':
                for ligne in self.map.grid:
                    if ligne[py] == '.' or ligne[py] == "+":
                        return False
                for ligne in self.map.grid:
                    if ligne[py+1] == ' ' or ligne[py+1]=="@":
                        return False
                return True
        return False
        

    def get_player_position(self):
        """
        Méthode qui permet de connaitre la position (x,y) du joueur
        
        On retourne False si on ne trouve pas de joueur ("@") dans la grille, sinon on retourne la position sous forme de tuple (x,y)
        """
        return self.map.player_position()


    def display(self):
        """
        Méthode permettant d'afficher sous forme textuelle self.grid.
        
        on ne retourne rien.
        """
        self.map.display_grid()
        
    
    def loose_game(self):
        """
        Vérifie si le jeu est perdu, retourne True si c'est perdu, sinon on retourne False
        """
        if self.perdu_coin() == True:
            return True
        if self.perdu_ligne() == True:
            return True
        return False
    
    
    def win_game(self):
        """
        Vérifie si le jeu est gagné, retourne True si c'est gagné, sinon on retourne False
        """
        if self.map.box_number()==0:
            return True
        return False
    
if __name__=="__main__":
    g = Grid(file=sys.path[0]+("\\..\\niveaux\\niveau002.txt") if os.name in ('nt', 'dos') else sys.path[0]+"/../niveaux/niveau002.txt" )
    m = Map(g)
    m.display()
    m = m.move("right")
    m.display()
    print(m.solve())
    
