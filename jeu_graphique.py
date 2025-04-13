import sys
import os
import random
import time

import pygame
from pygame.locals import *

from threading import Thread

from python.grid import Grid
from python.map import Map

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

class Button_image(pygame.sprite.Sprite):
    """
    Class qui permet de définir un sprite en fonction d'une image puis le place a la position donnée
    
    arguments : 
    -position (tuple) un tuple (x,y) qui définit la position du sprite créer
    -image (pygame.image) définis le contenus utilisé par le sprite 
    
    Ce sprite peut-être utilisé comme un bouton grâce à la méthode "set_triggered"
    """
    def __init__(self, position, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(position[0],position[1])
    
    def set_triggered(self, pos):
        """
        Vérifie si la position donnée est inclus dans le sprite
        
        argument:
        -pos (tuple) un tuple (x,y) qui définit la position à verfier
        
        On retourne True si la position est dans le sprite sinon on retourne False
        """
        return self.rect.collidepoint(pos)


class Button_text(pygame.sprite.Sprite):
    """
    Class qui permet de définir un sprite en fonction d'une image puis le place a la position donnée
    
    arguments : 
    -position (tuple) un tuple (x,y) qui définit la position du sprite créer
    -text (str) Le texte à écrire dans le sprite
    -color (tuple) Définis la couleur du texte (r,g,b)
    -font (pygame.font) Définis la police du texte, par défaut on utilise la police arial
    
    Ce sprite peut-être utilisé comme un bouton grâce à la méthode "set_triggered"
    """
    def __init__(self, position, text, color, font = None):
        pygame.sprite.Sprite.__init__(self)
        pygame.font.init()
        font = pygame.font.SysFont("arial.ttf",20) if font == None else font
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (position[0],position[1])
    
    def set_triggered(self, pos):
        """
        Vérifie si la position donnée est inclus dans le sprite
        
        argument:
        -pos (tuple) un tuple (x,y) qui définit la position à verfier
        
        On retourne True si la position est dans le sprite sinon on retourne False
        """
        return self.rect.collidepoint(pos[0], pos[1])



class Interface_graphique:
    """
    Class qui permet de gérer l'interface graphique d'un Sokoban.
    L'interface graphique est elle même gérée grâce au module pygame
    """
    
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.res=(1000,1000)
        self.screen = pygame.display.set_mode(self.res)

        self.police=pygame.font.Font(sys.path[0]+'/polices/retro.ttf', 70)
        self.titre_menu=pygame.font.Font(sys.path[0]+'/polices/tetris.ttf', 100)
        
        icone = pygame.image.load(sys.path[0]+"/images/images_jeu/icone.png")
        pygame.display.set_icon(icone)
        pygame.display.set_caption("Projet Sokoban")

        self.sprites = pygame.sprite.Group()
        
        self.count_file = 0         #l'index dans self.listeFichiers du niveau actuel 
        self.listeFichiers=[]
        repertoire = sys.path[0]+"/niveaux/"
        self.listeFichiers.extend(os.listdir(repertoire))
        self.listeFichiers.sort()
        
        self.list_musics=[]
        self.list_musics.extend(os.listdir(sys.path[0]+"/music/"))
        self.list_musics.remove("Xavier_Dang_-_Better_Never.mp3") #On enleve la musique du menu
        
        self.player_step_sound = pygame.mixer.Sound(sys.path[0]+"/sons/player_step.wav")
        self.btn_hit_sound = pygame.mixer.Sound(sys.path[0]+"/sons/button_hit.wav")
        self.music_on = True
        
        self.last_moves = []
        self.retour_state = False
        
        self.menu()
        

    def menu(self):
        """
        Méthode qui permet d'afficher le menu de jeu du Sokoban, cette méthode est directement appelé à l'initialisation de la class
        """
        if not pygame.mixer.music.get_busy() and self.music_on:
            pygame.mixer.music.load(sys.path[0]+"/music/Xavier_Dang_-_Better_Never.mp3")
            pygame.mixer.music.play(-1)
        
        self.sprites.empty()
        
        game_title = Button_text((500,200), "sokoban", (0,255,255), font = self.titre_menu)
        self.sprites.add(game_title)

        play_bt = Button_text((500,400),  "Jouer", (70,242,0), font=self.police)
        self.sprites.add(play_bt)
        
        level_bt = Button_text((500,500),  "Liste des niveaux", (215,232,82), font=self.police)
        self.sprites.add(level_bt)
        
        add_level_bt = Button_text((500,600),"Ajouter/Supprimer des niveaux",(215,232,82), font=self.police)
        self.sprites.add(add_level_bt)

        quit_bt = Button_text((500,700),  "Quitter", (223,0,0), font=self.police)
        self.sprites.add(quit_bt)
        
        music_image = pygame.image.load(sys.path[0]+"/images/images_jeu/music.png") if self.music_on else pygame.image.load(sys.path[0]+"/images/images_jeu/music_mute.png")
        music_button = Button_image((50,900), aspect_scale(music_image.convert_alpha(), 50,50))
        self.sprites.add(music_button)
        
        self.screen.fill((0,0,0))
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.flip()
        
        self.run = True
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT :
                    pygame.quit()
                    sys.exit()
                    
                if event.type == KEYDOWN and event.key == K_RETURN: #Si on clique sur entrée, on joue directement au jeu; Comme si on trigger le bouton joué
                    self.sprites.empty()
                    self.run = False     
                    self.btn_hit_sound.play()
                    pygame.mixer.music.stop()
                    self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file])
                          
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    if play_bt.set_triggered(event.pos):
                        self.sprites.empty()
                        self.run = False     
                        self.btn_hit_sound.play()
                        pygame.mixer.music.stop()
                        self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file])
                    elif level_bt.set_triggered(event.pos):
                        self.sprites.empty()
                        self.run=False
                        self.btn_hit_sound.play()
                        self.levels_list()
                    elif add_level_bt.set_triggered(event.pos):
                        self.btn_hit_sound.play()
                        thread_system = Thread(target=os.system ,args=([f"nautilus \"{sys.path[0]}/niveaux/\""])) if os.name not in ("nt","dos") else Thread(target=os.system ,args=([f'cd "{str(sys.path[0])}\\niveaux" && start .\\']))
                        thread_system.start()
                    elif quit_bt.set_triggered(event.pos):
                        self.btn_hit_sound.play()
                        pygame.quit()
                        sys.exit()
                    elif music_button.set_triggered(event.pos):
                        if self.music_on:
                            self.music_on = False
                            pygame.mixer.music.pause()
                            music_button.image = aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/music_mute.png").convert_alpha(),50,50)
                            
                        else:
                            self.music_on = True
                            pygame.mixer.music.unpause()
                            music_button.image = aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/music.png").convert_alpha(),50,50)
                        
            self.screen.fill((0,0,0))
            self.sprites.update()
            self.sprites.draw(self.screen)
            pygame.display.flip()          
                        
                        
    def levels_list(self):
        """
        Méthode qui permet de gérer l'affichage de la fenetre qui affiche tout les niveaux jouables
        """
        page = 1
        
        self.listeFichiers=[]
        repertoire = sys.path[0]+"/niveaux/"
        self.listeFichiers.extend(os.listdir(repertoire))
        self.listeFichiers.sort()

        level_title = Button_text((250,50), "Choisis ton niveau :", (223,0,0), font=self.police)
        self.sprites.add(level_title)

        back = Button_text((900,950), "Retour", (215,232,82), font=self.police)
        self.sprites.add(back)

        self.screen.fill((0,0,0))

        self.sprites.update()
        self.sprites.draw(self.screen)
        
        pygame.display.flip()
 
        self.run= True
        while self.run:

            self.level_page(page) #on affiche les niveaux de la page actuelle, chaque page possédent 20 niveaux 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    
                    if back.set_triggered(event.pos):   #Si le bouton retour est cliquee on retourne au menu
                        self.run=False
                        self.sprites.empty()
                        self.btn_hit_sound.play()
                        self.menu()

                    #Gére l'affichage des pages de niveaux 
                    elif self.previous_page2.set_triggered((event.pos[0]-145,event.pos[1]-910)):    #On modifie event.pos pour correspondre aux coordonnées de page_sprite_frame 
                        page = self.previous_page2_number
                    
                    elif self.previous_page.set_triggered((event.pos[0]-145,event.pos[1]-910)) or self.left_arrow.set_triggered((event.pos[0]-145,event.pos[1]-910)) :
                        page = self.previous_page_number
                        
                    elif self.next_page.set_triggered((event.pos[0]-145,event.pos[1]-910)) or self.right_arrow.set_triggered((event.pos[0]-145,event.pos[1]-910)):
                        page = self.next_page_number
                    
                    elif self.next_page2.set_triggered((event.pos[0]-145,event.pos[1]-910)):
                        page = self.next_page2_number
                    
                    compteur = 0
                    for sprite in self.lvl_sprites.sprites():                
                        if sprite.set_triggered((event.pos[0]-50+25, event.pos[1]-150+50)): #On modifie event.pos pour correspondre aux coordonnées de page_screen
                            self.count_file = compteur + (page-1)*20
                            self.btn_hit_sound.play()
                            pygame.mixer.music.stop()
                            self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file])
                        compteur+=1   

                        
    def level_page(self,page = 1):
        """
        """
        #Gestion de la liste des pages 
        page_sprite_frame = pygame.Surface((500,80))
        page_sprite_frame.fill((0,0,0))
        page_sprite_frame_rect = page_sprite_frame.get_rect()
        page_sprite_frame_rect.center = (400,950)
        
        page_sprites = pygame.sprite.Group()
        
        self.left_arrow = Button_text((15,40), "<", (215,232,82), font=self.police)
        page_sprites.add(self.left_arrow)
        
        self.previous_page2_number = page-2 if page-2 > 0 else len(self.listeFichiers)//20+1 if page-1 > 0 else len(self.listeFichiers)//20 if page-1 <=0 else len(self.listeFichiers)//20+1
        self.previous_page2 = Button_text((90,40), str(self.previous_page2_number), (15,232,82), font=self.police) 
        page_sprites.add(self.previous_page2)
        
        self.previous_page_number = page-1 if page-1 > 0 else len(self.listeFichiers)//20 +1
        self.previous_page = Button_text((165,40), str(self.previous_page_number), (15,232,82), font=self.police)
        page_sprites.add(self.previous_page)
        
        self.current_page = Button_text((240,40), str(page), (65,87,243), font=self.police) 
        page_sprites.add(self.current_page)
        
        self.next_page_number = page+1 if page < len(self.listeFichiers)//20 +1 else 1
        self.next_page = Button_text((315,40), str(self.next_page_number), (15,232,82), font=self.police) 
        page_sprites.add(self.next_page)
        
        self.next_page2_number = page+2 if page+2 <= len(self.listeFichiers)//20 +1 else page+1 if page+1 < len(self.listeFichiers)//20 +1 else 2 if self.next_page_number == 1 else 1
        self.next_page2 = Button_text((390,40), str(self.next_page2_number), (15,232,82), font=self.police) 
        page_sprites.add(self.next_page2)
        
        self.right_arrow = Button_text((465,40), ">", (215,232,82), font=self.police)
        page_sprites.add(self.right_arrow)
        
        
        
        #Gestion du cadre en lui même
        page_screen = pygame.Surface((950,800))
        page_screen.fill((20,20,20))
        page_screen_rect = page_screen.get_rect()
        page_screen_rect.center = (500,500)
        pygame.draw.rect(page_screen, (0,255,255), pygame.Rect(0,0,950,800), 3)
        
        #Gestion des icones de chaque niveaux
        self.lvl_sprites = pygame.sprite.Group()    
        
        for y in range(4):
            for x in range (5):
                try:                                            #les try except permettent de gerer les out of range sur listeFichiers
                    logo=pygame.image.load(sys.path[0]+"/images/icones_niveaux/"+ self.listeFichiers[(page-1)*20 + x + (y*5)][:-4] +".png").convert()
                    surface = pygame.Surface((150,150)) #On definis la surface pour garder un carre de 150*150 cliquable, sinon c'est juste l'image redimensionné 
                    logo = aspect_scale(logo, 150, 150)
                    surface.fill((20,20,20))
                    surface.blit(logo, logo.get_rect())
                    self.lvl_sprites.add(Button_image((180*x +35, 55+ 180*y), surface))
                except:
                    try:
                        button = Button_image((180*x +35, 55+ 180*y), pygame.Surface((150,150)))
                        text = pygame.font.SysFont("arial.ttf",20).render(self.listeFichiers[(page-1)*20 + x + (y*5)][:-4], True, (255,255,255))    #On affiche le noms du niveaux quand on a pas d'icones
                        button.image.blit(text, text.get_rect())
                        self.lvl_sprites.add(button)
                    except:
                        pass
                    
        self.lvl_sprites.update()
        self.lvl_sprites.draw(page_screen)
        self.screen.blit(page_screen, page_screen_rect)
        
        page_sprites.update()
        page_sprites.draw(page_sprite_frame)
        self.screen.blit(page_sprite_frame, page_sprite_frame_rect)
        
        self.sprites.update()
        self.sprites.draw(self.screen)  
        
        pygame.display.flip()
        
        
    def play_level(self,fichier):
        if not pygame.mixer.music.get_busy() and self.music_on: 
            pygame.mixer.music.load(sys.path[0]+"/music/"+random.choice(self.list_musics))
            pygame.mixer.music.play(-1)
        
        grille = Grid(file=fichier)
        carte = Map(grille)
        
        clock = pygame.time.Clock()
        self.clock_counter = 0
        pygame.time.set_timer(pygame.USEREVENT, 1000)   #On envoie un evenement toute les secondes
        
        self.coups = 0
        self.player_direction = "bottom"
        
        self.screen.fill((0,0,0))
        self.sprites.empty()
        self.display_level(carte)

        close_screen = False            #necessaire pour ne pas relancer le menu si on appuie sur la croix
        game_is_finished = False
        while not game_is_finished:
            pygame.time.Clock().tick(15)  # frames par secondes
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == pygame.USEREVENT:    #Toutes les secondes on incremente de 1 le nombre de secondes passées
                    self.clock_counter+=1
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    if self.boutton_menu.set_triggered(event.pos):
                        game_is_finished = True
                        self.run = False    
                        self.btn_hit_sound.play()
                        pygame.mixer.music.stop()
                        self.menu()
                    
                    elif self.restart_button.set_triggered(event.pos):
                        close_screen = True
                        game_is_finished = True
                        self.run = False
                        self.btn_hit_sound.play()
                        self.play_level(fichier)
                        
                    elif self.boutton_retour.set_triggered(event.pos):
                        self.btn_hit_sound.play()
                        if not len(self.last_moves) == 0:
                            self.coups -= 1
                            carte = self.last_moves.pop()
                            self.retour_state = True
                            self.player_direction = "bottom"    
                        
                    elif self.answer_button.set_triggered(event.pos):
                        loading_image = [sys.path[0]+f"/images/images_jeu/loading{i}.png" for i in range(1,9)]
                         
                        
                        solve_thread = ThreadWithReturnValue(target= carte.solve, args=())     #On creer un Thread qui lance la méthode de resolution de la map actuelle 
                        solve_thread.start()

                        compteur = 0
                        stop_reso = False
                        
                        while solve_thread.is_alive() and not stop_reso:                  #Tant que le Thread de résolution est en cours
                            self.answer_button.image =  aspect_scale(pygame.image.load(loading_image[int(compteur)%len(loading_image)]).convert_alpha(),60,60) 
                            compteur+=0.2

                            for event in pygame.event.get():        #On doit continuer de capter les evenements afin de faire comprendre 
                                if event.type == QUIT:
                                    stop_reso = True
                                    pygame.quit()
                                    sys.exit()
                                elif event.type == pygame.USEREVENT:    #Toutes les secondes on incremente de 1 le nombre de secondes passées
                                    self.clock_counter+=1
                                elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                                    if self.boutton_menu.set_triggered(event.pos):
                                        stop_reso = True
                                        game_is_finished = True
                                        self.run = False    
                                        self.btn_hit_sound.play()
                                        pygame.mixer.music.stop()
                                        self.menu()
                                    elif self.restart_button.set_triggered(event.pos):
                                        close_screen = True
                                        game_is_finished = True
                                        stop_reso = True
                                        self.run = False
                                        self.btn_hit_sound.play()
                                        self.play_level(fichier)

                            self.screen.fill((0,0,0))
                            self.sprites.update()
                            self.sprites.draw(self.screen)
                            pygame.display.flip()                
                                                     
                                                        
                        all_moves = solve_thread.join()                 #On recupere la valeur de retour de la méthode map.solve
                        if type(all_moves) == tuple:    #Cela suppose que le niveau a une solution
                            for move in all_moves[0]:       #On joue automatiquement tout les coups de la solution, 1 coup toute les 0.5 secondes
                                carte = carte.move(move)
                                self.coups+=1
                                self.display_level(carte)
                                pygame.display.flip()
                                self.player_step_sound.play()
                                time.sleep(0.5)
                                
                        
                        game_is_finished = True
                    
                    
                elif event.type == KEYDOWN:
                    if event.key == K_LEFT or event.key == K_q:
                        self.last_moves.append(carte)
                        carte = carte.move("left")
                        self.player_direction = "left"
                        self.coups +=1
                        self.player_step_sound.play()
                        
                    elif event.key == K_RIGHT or event.key == K_d:
                        self.last_moves.append(carte)
                        carte = carte.move("right")
                        self.player_direction = "right"
                        self.coups +=1
                        self.player_step_sound.play()
                        
                    elif event.key == K_UP or event.key == K_z:
                        self.last_moves.append(carte)
                        carte = carte.move("top")
                        self.player_direction = "top"
                        self.coups +=1
                        self.player_step_sound.play()
                        
                    elif event.key == K_DOWN or event.key == K_s:
                        self.last_moves.append(carte)
                        carte = carte.move("bottom")
                        self.player_direction = "bottom"
                        self.coups +=1
                        self.player_step_sound.play()
                                
                    game_is_finished = carte.win_game() or carte.loose_game()
            self.display_level(carte)
            pygame.display.flip()
            
            if game_is_finished:
                time.sleep(0.5) #On attend un peu avant d'afficher l'écran de fin
                self.end_level(carte.win_game())


    def display_level(self, carte):
        ''' fonction qui affiche les sprites pour chaque element de la carte'''
        
        # les .convert() servent à renvoyer une copie convertie de cette image.
        self.sprites.empty() 
        self.screen.fill((0,0,0))
        
        images = {
            "#": pygame.image.load(sys.path[0]+"/images/images_jeu/wall.png").convert(),
            " ": pygame.image.load(sys.path[0]+"/images/images_jeu/ground.png").convert(),
            "@": pygame.image.load(sys.path[0]+"/images/images_jeu/perso.png").convert(),
            "+": pygame.image.load(sys.path[0]+"/images/images_jeu/perso_jaune.png").convert(),
            "$": pygame.image.load(sys.path[0]+"/images/images_jeu/caisse_normale.png").convert(),
            "*": pygame.image.load(sys.path[0]+"/images/images_jeu/caisse_ok.png").convert(),
            ".": pygame.image.load(sys.path[0]+"/images/images_jeu/target.png").convert(),
            "/": pygame.image.load(sys.path[0]+"/images/images_jeu/black.png").convert()
        }
        if self.player_direction == "top":
            images["@"] = pygame.image.load(sys.path[0]+"/images/images_jeu/perso_back.png").convert()
        elif self.player_direction == "left":
            images["@"] = pygame.image.load(sys.path[0]+"/images/images_jeu/perso_left.png").convert()
        elif self.player_direction == "right":
            images["@"] = pygame.image.load(sys.path[0]+"/images/images_jeu/perso_right.png").convert()
        elif self.player_direction == "bottom":
            images["@"] = pygame.image.load(sys.path[0]+"/images/images_jeu/perso.png").convert()
        
        #Interface
        self.bouttons_coups = Button_text((500,40), str(self.coups), (255,255,255), font=self.police)
        self.sprites.add(self.bouttons_coups)
        
        self.text_coups = Button_text((800,40), "coups joués", (255,255,255), font=self.police)
        self.sprites.add(self.text_coups)
        
        min_counter = self.clock_counter//60
        s_counter = self.clock_counter%60
        self.text_counter = Button_text((200,40), f"{min_counter} : {s_counter}", (255,255,255), font=self.police)
        self.sprites.add(self.text_counter)
        
        self.boutton_menu = Button_image((875,900), aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/exit.png").convert_alpha(),75,75))
        self.sprites.add(self.boutton_menu)
        
        self.boutton_retour = Button_image((200,900), aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/return.png").convert_alpha(), 75, 75))
        self.sprites.add(self.boutton_retour)
        
        self.restart_button = Button_image((50,900), aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/retry.png").convert_alpha(),85,85))
        self.sprites.add(self.restart_button)
        
        self.answer_button = Button_image((350,900), aspect_scale(pygame.image.load(sys.path[0]+"/images/images_jeu/answer.png").convert_alpha(),70,70))
        self.sprites.add(self.answer_button)
        
        taille_grid_x = len(carte.map.grid[1])
        taille_grid_y = len(carte.map.grid)

        taille_sprite_x = min(700/taille_grid_x,700/taille_grid_y)
        taille_sprite_y = taille_sprite_x
        # Redimensionner les sprites
        for key, image in images.items():
            images[key] = aspect_scale(image,taille_sprite_x, taille_sprite_y)

        init_x = 150
        init_y = 150

        nl = 0
        for ligne in carte.map.grid:
            nc = 0
            for case in ligne:
                x = nc * taille_sprite_x
                y = nl * taille_sprite_y
                position = (init_x + x, init_y + y)
                self.sprites.add(Button_image(position,images[case]))
                nc += 1
            nl += 1
            
        self.sprites.update()
        self.sprites.draw(self.screen)
        
        
    def end_level(self,win):
        win_sound_effect = pygame.mixer.Sound(sys.path[0]+"/sons/win.mp3") if win else pygame.mixer.Sound(sys.path[0]+"/sons/loose.mp3")
        win_sound_effect.play()
        
        pygame.mixer.music.pause()
        
        self.sprites.empty() 
        self.screen.fill((0,0,0))
        
        back_menu_pos = (500,650) if win and self.count_file+1  == len(self.listeFichiers) else (300,650)
        back_menu_btn = Button_text(back_menu_pos, "Menu principal", (215,232,82), font=self.police)
        self.sprites.add(back_menu_btn)
        
        coup_text = Button_text((500,550), "Nombre de coups : "+str(self.coups), ((255,255,255)), font=self.police)
        self.sprites.add(coup_text)
        
        min_counter = self.clock_counter//60
        s_counter = self.clock_counter%60
        timer_txt = Button_text((500,450), f"Temps {min_counter} : {s_counter}", ((255,255,255)), font=self.police)
        self.sprites.add(timer_txt)
        
        win_text = Button_text((500,250), "bravo" if win else "perdu", (55,217,104) if win else (250,22,28), font=self.titre_menu)
        self.sprites.add(win_text)
        
        action_message = "Niveau suivant" if win and self.count_file+1 != len(self.listeFichiers) else "Vous avez réussi le dernier niveau !" if win and self.count_file+1  == len(self.listeFichiers) else "Recommencer"
        action_pos = (500,350) if win and self.count_file+1  == len(self.listeFichiers) else (700,650)
        action_btn = Button_text(action_pos, action_message , (55,217,104) if win else (250,22,28), font=self.police)
        self.sprites.add(action_btn)
        
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN and win and self.count_file+1 != len(self.listeFichiers):
                        self.count_file +=1
                        self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file])
                        pygame.mixer.music.unpause()
                        
                    elif event.key == K_RETURN and not win:
                        self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file]) 
                        pygame.mixer.music.unpause()
                
                elif (event.type == MOUSEBUTTONDOWN and event.button==1) :
                    if back_menu_btn.set_triggered(event.pos):
                        run = False
                        pygame.mixer.music.stop()
                        self.menu()
                        
                    elif action_btn.set_triggered(event.pos) and win and self.count_file+1 != len(self.listeFichiers):
                        self.count_file +=1
                        self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file])
                        pygame.mixer.music.unpause()
                      
                    elif action_btn.set_triggered(event.pos) and not win:
                        self.play_level(sys.path[0]+"/niveaux/"+self.listeFichiers[self.count_file]) 
                        pygame.mixer.music.unpause()
                        
                    
            self.sprites.update()
            self.sprites.draw(self.screen)
            pygame.display.flip()
        
        
        
def aspect_scale(img,bx,by):
    """ Scales 'img' to fit into box bx/by.
    This method will retain the original image's aspect ratio 
    source : http://www.pygame.org/pcr/transform_scale/
    """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx),int(sy)))

if __name__ == '__main__':
    Interface_graphique()
    
    
