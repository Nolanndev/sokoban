import sys
import os
import time 

from threading import Thread

from python.grid import Grid
from python.map import Map
from python.algorithme_A import algorithmeA



class ThreadWithReturnValue(Thread):
    """
    Source : https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
    Meme principe qu'un thread sauf que l'on peut recuperer la possible valeur de retour de la fonction cible ("target").
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
        
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,**self._kwargs)
            
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    

def Ginput(str=""):
    """
    Cette fonction est comme la fonction native input().
    
    parametre:
    -str (str) La chaine de caractère à afficher dont-on attend une entrée
    
    On retourne la touche appuyer, l'interet c'est qu'il n'y a plus besoin d'appuyer sur entrer à chaque fois.
    source : https://stackoverflow.com/questions/24072790/how-to-detect-key-presses/
    """
    try:
        import getkey as gt #gere les évenements clavier
    except:
        print("Vous n'avez pas installé le module getkey.")
        print("Il est recommander de l'installer(pip install getkey) pour une meilleure expérience.")
    print(str)
    while True:
        key = gt.getkey()
        print(key)
        return key
    
    
def clear_console():
    """
    Cette fonction execute la commande clear (cls sous windows) dans le terminal
    """
    os.system('cls' if os.name in ('nt', 'dos') else 'clear') #la méthode de clear est différent suivant l'OS
    
    
def print_solving(compteur):
    """
    Fonction utilisée quand l'algorithme est entrain de recherché, elle permet de gerer l'affichage du fait qu'il recherche. 
    Obligé de creer une fonction pour pouvoir l'appelé à partir d'un Thread  
    """
    try:
        import termcolor as tc              
        print(tc.colored(f'\r{" "*20}\rSolving{"."*(compteur%4)}',"yellow"),end="")
    except:
        print(f'\r{" "*20}\rSolving{"."*(compteur%4)}',end="")
    
    
def play_level(grid):
    """
    Cette fonction permet de lancer un niveau et d'y jouer
    parametre:
    -grid (objet Grid) Correspond a la grille du niveau que l'on veut jouer
    """
    clear_console()
    
    try:
        import getkey as gt
        getkey_installed=True
    except:
        print("Vous n'avez pas installé le module getkey.")
        print("Il est recommander de l'installer (pip install getkey) pour une meilleure expérience.\n")
        getkey_installed=False
        
    try:
        import termcolor as tc              #Utiliser pour colorer le texte dans le terminal
        termcolor_installed=True
    except:
        print("Vous n'avez pas installé le module termcolor.")
        print("Il est recommander de l'installer (pip install termcolor) pour une meilleure expérience.\n")
        termcolor_installed=False
        
        
    last_moves = []
    retour_state = False
        
    map = Map(grid)
    map.display()
    
    level = True
    while level:
        
        # on a choisit z q s d car se sont les touches classiques de direction
        direction = Ginput("Direction ( z | q | s | d | c (Quitter game) | a (Resoudre le niveau) | e (Annuler le dernier coup) | r (Recommencer le niveau)) : ").lower() if getkey_installed else input("Direction ( z | q | s | d | c (quit game)) : ").lower()
        
        clear_console()
        
        if direction == "z":
            last_moves.append(map)
            map = map.move("top")
        elif direction == "s":
            last_moves.append(map)
            map = map.move("bottom")
        elif direction == "q":
            last_moves.append(map)
            map = map.move("left")
        elif direction == "d":
            last_moves.append(map)
            map = map.move("right")

        elif direction == "r":
            map = Map(grid) 
            
        elif direction == 'e':
            if not len(last_moves) == 0:
                map = last_moves.pop()
                retour_state = True    
                
        map.display()        
            
        if direction == "a":              #L'utilisateur veut resoudre le niveau actuelle (niveau possiblement modifié par les coups du joueurs)
            solve_thread = ThreadWithReturnValue(target=map.solve, args=())     #On creer un Thread qui lance la méthode de resolution de la map actuelle 
            solve_thread.start()
            
            compteur = 0
            
            while solve_thread.is_alive():                  #Tant que le Thread de résolution est en cours
                
                print_thread = Thread(target=print_solving ,args=([compteur%4]))        #On creer des Threads qui gérent l'affichage dans le terminal en appelant la fonction print_solving
                print_thread.start()
                
                compteur += 1
                time.sleep(0.3)
                
            all_moves = solve_thread.join()                 #On recupere la valeur de retour de la méthode map.solve
            if type(all_moves) == tuple:    #Cela suppose que le niveau a une solution
                for move in all_moves[0]:       #On joue automatiquement tout les coups de la solution, 1 coup toute les 0.5 secondes
                    clear_console()
                    map = map.move(move)
                    map.display()
                    time.sleep(0.5)
                    
            
            else:                       #Si le niveau n'as pas de solution, on l'affiche 
                clear_console()
                map.display()
                print("/!\\ "+all_moves) if not termcolor_installed else print(tc.colored("/!\\ "+all_moves,"red"))
                level = False
                  
                                           
        elif direction not in [lettre for lettre in 'zqsdaerc']:
            print(tc.colored("/!\\ Commande inconnue","red")) if termcolor_installed else print("/!\\ Commande inconnue")        
        
        
        win_game = map.win_game()
        loose_game = map.loose_game()
            
        if direction == "c" or win_game or loose_game:  # si "c" est entré alors c'est la fin du niveau actuel
            level=False
            print("Fin du jeu !")
            
            if not termcolor_installed:
                print("Bravo ! Vous avez gagné") if win_game else print("Dommage ! Vous avez perdu") if loose_game else print("")
            else:
                 print(tc.colored("Bravo ! Vous avez gagné","green")) if win_game else print(tc.colored("Dommage ! Vous avez perdu","red")) if loose_game else print("")
                 
    print("\n---------Appuyé sur entré pour quitter cette page---------")
    input()
    
     
     
def homepage():
    """
    Fonction qui permet d'afficher le menu textuel du Sokoban
    """
    clear_console()
    print(r"""
  _____         _           _                
 / ____|       | |         | |                         
| (___    ___  | | __ ___  | |__    __ _  _ __         
 \___ \  / _ \ | |/ // _ \ | '_ \  / _` || '_ \        
_ ___) || (_) ||   <| (_) || |_) || (_| || | | |       
|_____/  \___/ |_|\_\\___/ |_.__/  \__,_||_| |_|       
                """)
    print("-----------------Page d'acceuil-----------------\n")
    print("Liste des commandes :")
    print("\t-\"lister-niveaux\" (ln) : Affiche la liste des niveaux disponibles\n")
    print("\t-\"ajouter-niveau\" (an) : Ajoute un niveau dans la liste des niveaux disponibles (ex : an ~/exemple/niveau_test.txt)\n")
    print("\t-\"supprimer-niveau\" (sn) : Supprime un niveau à partir de son nom ou son identifiant de la liste des niveaux disponibles (ex : sn niveau_test.txt ou sn 1)\n")
    print("\t-\"jouer-niveau\" (jn) : Permet de jouer un niveau à partir de son nom ou son identifiant de la liste des niveaux disponibles (ex : jn niveau_test.txt ou jn 1)\n")
    print("\t-\"quitter\" (qt) : Permet de quitter cette page et le jeu\n")
    
    
def play_sokoban():
    """
    Fonction qui gére le menu du sokoban ainsi que les commandes mise à disposition
    """
    homepage()
    game = True
    
    while game:
        command = input("Rentrez votre commande :").split()
        destination = sys.path[0]+("\\niveaux\\") if os.name in ('nt', 'dos') else sys.path[0]+"/niveaux/"
        
        listeFichiers=[]
        for (repertoire, sousRepertoires, fichiers) in os.walk(destination):
            listeFichiers = fichiers
            break
        listeFichiers.sort()
        
        while len(command)==0:
            command = input("Rentrez votre commande :").split() if len(command)==0 else command
        
        if command[0] == "lister-niveaux" or command[0] == "ln":            
            for i in range(0,len(listeFichiers),2):
                try:
                    print(f'({i+1}) {listeFichiers[i][:30]:35} ({i+2}) {listeFichiers[i+1][:35]}')  #On utilise les formats pour afficher les fichiers en deux colonnes
                except:
                    print(f'({i+1}) {listeFichiers[i][:30]}')
                    
        elif command[0] == "ajouter-niveau" or command[0] == "an":
            try:
                file = command[1] 
                copy_command = 'copy' if os.name in ('nt', 'dos') else 'cp -vi'  #la méthode de copy est différent suivant l'OS
                os.system(f'{copy_command} {file} {destination}')
                listeFichiers.sort()
            except:
                pass
            
        elif command[0] == "supprimer-niveau" or command[0] == "sn":
            try:
                file = command[1] 
                try :
                    file = listeFichiers[int(file)-1]    #si on rentre sn 1 pour supprimer le premier fichier de listeFichiers
                except:
                    pass
                remove_command = 'del /p' if os.name in ('nt', 'dos') else 'rm -vi'  #la méthode est différent suivant l'OS
                os.system(f'{remove_command} {destination}{file}')
            except:
                pass
        
        elif command[0] == "jouer-niveau" or command[0] == "jn":
            try:
                file = command[1] 
                try :
                    file = listeFichiers[int(file)-1]    #on rentre jn 1 pour jouer le premier fichier de listeFichiers 
                except:
                    pass
                grid = Grid(sys.path[0]+(f"\\niveaux\\{file}") if os.name in ('nt', 'dos') else sys.path[0]+f"/niveaux/{file}")
                play_level(grid)    #On joue le niveau
                homepage()          #On rapelle homepage quand le niveau est fini
            except:
                pass
            
        elif command[0] == "quitter" or command[0] == "qt":
            print("Au revoir")
            game = False    
            
        print()
            

if __name__=="__main__":
    play_sokoban()

    