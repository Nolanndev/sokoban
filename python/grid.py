'''
'\' : vide exterieur
' ' : vide intérieur
'#' : mur
'@' : personnage
'$' : caisse
'.' : objectif
'*' : caisse sur une zone de rangement 
'+' : joueur sur une zone de rangement 
'''

class Grid:
    """
    Class qui permet de gérer la création d'une grille de jeu.
    arguments:
    -file(str) chemin vers le fichier txt où le niveau est écris, None par défaut
    -array(list) matrice qui correspond à un niveau, [] par défaut
    """
    
    def __init__(self, file=None, array=[]):
        self.grid = array
        
        if file:
            self.grid = self.file_to_grid(file)
        
    def __hash__(self):
        chaine = ""
        for i in self.grid:
            for j in i:
                chaine += j
        return chaine.__hash__()
        
    def file_to_grid(self, file):
        """Méthode permettant de générer une grille de jeu (sous forme de matrice)
        à partir d'une grille écris dans fichier textuel.
        
        arguments:
        -file (str): fichier d'entrée.
        
        on retourne une grille sous forme de liste.
        """
        
        possible_char = "# @+$*./"
        
        with open(file ,mode="r",encoding="utf-8") as file:
            new_grid = []
            compteur = 0
            
            for line in file.readlines():
                new_grid.append([])
                
                for elt in line[:-1]:       #on enleve le saut de ligne à la fin
                    if elt in possible_char:
                        new_grid[compteur].append(elt) 
                    else:
                        return new_grid[:-1]    #on enleve la sousliste vide crée pour rien
                compteur += 1
                
            return new_grid
                
        
        
    def grid_to_file(self, file_name):
        """Méthode qui permet d'enregistrer dans un fichier texte
        
        arguments:
        -file_name (str) Le nom du fichier de sauvegarde
        
        retourne rien """
        
        with open(file_name, mode = "w", encoding = 'utf-8') as file:
            for line in self.grid:
                for elt in line:
                    file.write(elt)
                file.write("\n")
                    
            
    def display_grid(self):
        """
        Méthode permettant d'afficher sous forme textuelle self.grid
        Si l'element actuelle est "/" on le remplace par " " pour un meilleur affichage
        
        on ne retourne rien.
        """
        
        for line in self.grid:
            for elt in line:
                print(elt if elt != "/" else " ", end="")
            print()
        
        
    def get_grid_position(self, x, y=None):
        """Méthode permettant de retourner la valeur de grille[x][y]
        
        arguments:
        -x (int) designe la ligne dont on veux retourner la valeur
        -y (int) designe la colonne dont on veux retourner la valeur (par defaut y = None)
        
        On retourne grille[x] si seul x est definis, on retourne grille[x][y] si on definis x et y
        retourne ValueError si x ou y sont mal définis
        """
        
        try:
            if type(y)==int:
                return self.grid[x][y]
            return self.grid[x]
    
        except:
            raise ValueError("Un des paramètres n'est pas valide")    
        
        
    def grid_set_value(self, x, y, value):     
        """Méthode qui permet définir la valeur de grille[x][y] 
        Paramètres:
        -x (int) designe la ligne dont on veux modifier la valeur
        -y (int) designe la colonne dont on veux modifier la valeur 
        -value (str) designe la valeur que l'on vas mettre dans la grille
        
        On retourne ValueError si l'un des parmamètres est mal définis, sinon on ne retourne rien.
        """
        
        try:
            self.grid[x][y] = value
        
        except:
            raise ValueError("Un des paramètres n'est pas valide") 
        
        
    def player_position(self):
        """
        Méthode qui permet de connaitre la position (x,y) du joueur
        
        On retourne rien si on ne trouve pas de joueur ("@") dans la grille, sinon on retourne la position sous forme de tuple (x,y)
        """
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.get_grid_position(i,j)=="@" or self.get_grid_position(i,j)=="+":
                    return (i,j)
    
    
    def box_number(self):
        """
        Méthode qui permet de connaitre le nombre de boite de la grille (les boites placées sur un objectif ne sont pas compter)
        
        On retourne le nombre de boite ("$") de la grille
        """
        number=0
        for line in self.grid:
            for elt in line:
                number += 1 if elt=="$" else 0
        return number 
    
    
    def box_position(self):
        """
        Méthode qui permet de connaitre la position de toutes les boites (les boites placées sur un objectif ne sont pas compter) de la grille
        
        On retourne une liste de tuple, chaque tuple correspond à la position (x,y) de chaque boites ("$")
        """
        list_positions = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y] == "$":
                    list_positions.append((x,y))
        return list_positions
        
                
    
if __name__ == '__main__':   
    import sys, os
    g=Grid(sys.path[0]+("\\..\\niveaux\\niveau001.txt") if os.name in ('nt', 'dos') else sys.path[0]+"/../niveaux/niveau001.txt")   #On gére le cas ou on est sous windows
    g.display_grid()
    g.grid_set_value(1, 2, "#")
    g.display_grid()
    print(g.box_position())
    
