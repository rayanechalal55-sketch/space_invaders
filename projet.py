import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random 
   
        
 #--------------Class pouur entrer le nom du joueur--------------
class enter_player(object): 
    #fonction d'enitialisation   
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nom du joueur")
        frame = tk.Frame(self.root, padx=100, pady=100  , bg="black")
        frame.pack(padx=10, pady=10)
        title = tk.Label(frame,text="SPACE INVADERS",bg="black",fg="lime",font=("Arial", 28, "bold"))
        title.grid(row=0, column=0, pady=(0, 30))
        score_button = tk.Button(frame, text="Voir les scores", command=self.afficher_scores)
        score_button.grid(row=4, column=0, columnspan=2, pady=10)
        label = tk.Label(frame, text="Entrez votre nom :", bg="black", fg="white")
        label.grid(row=1, column=0)
        self.entry = tk.Entry(frame)
        self.entry.grid(row=2, column=0)
        button = tk.Button(frame, text="Valider", command=self.valider)
        button.grid(row=3, column=0, pady=10)
        self.name = None
        self.root.mainloop()
    #fonction pour Valider le nom du joueur et passer a la page jeu
    def valider(self):
        self.name = self.entry.get()
        if self.name != "":   
            self.root.destroy()
    #fonction pour afficher la liste des joueurs et leurs scores
    def afficher_scores(self):
        try:
            f = open("score.json", "r")
            liste = json.load(f)
            f.close()
        except (FileNotFoundError, json.JSONDecodeError):
            liste = []

        fenetre = tk.Toplevel(self.root)
        fenetre.title("liste des joueur plus leur Scores")

        title = tk.Label(fenetre, text="Liste des joueurs", font=("Arial", 18, "bold"))
        title.pack(pady=10)           
        for item in liste:
            texte = str(item['joueur'])+" : "+str(item['score']     )
            tk.Label(fenetre, text=texte, font=("Arial", 14)).pack()
    
  
#-----------------class pour gerer le nombre de vie du defender---------------
class heart(object):
    #fonction d'initialisation
    def __init__(self):
        self.radius = 5
        self.color = "red"
        self.number= 3
        self.id = None
        self.list=[]
        
    #fonction pour afficher le nombre de vie sur l'ecran en haur a droite 
    def install_in(self, canvas):
        self.canvas = canvas
        canvas_width = int(canvas.cget("width"))
        
        x = canvas_width - 30  
        y = 30
        img = Image.open("images.jpg")
        img = img.resize((30, 30))
        self.heart = ImageTk.PhotoImage(img)
        for i in range(self.number):
             x = x - 40 
             self.list.append(canvas.create_image(x, y, image=self.heart, tags="heart"))
    #fonction pour gerer la suppression d'un coeur a chque fois que le defender est toucher 
    def touched_by(self):
        if self.list:
            coeur = self.list.pop()
            self.canvas.delete(coeur)
            self.number -= 1  
            
            if self.number <= 0:
                return True   
        return False
            
#--------------------class gerer les aliens un par un------------------    
class Alien(object):
    #fonction d'initialisation
    def __init__(self):
        self.id = None
        self.alive = True
    #fonction pour gerer la suppression de l'alien en cas d'etre toucher par le tire du defender  
    def touched_by(self):
        if self.canvas and self.id:
            self.canvas.delete(self.id)
            self.id = None
            self.alive = False
    #fonction pour afficher les aliens
    def install_in(self, canvas, x, y, width, height):
        self.canvas = canvas
        img = Image.open("alien.gif")
        img = img.resize((width, height))
        self.alien = ImageTk.PhotoImage(img)
        self.id = canvas.create_image(x, y, image=self.alien ,tags="alien")

#--------------------class pour gerer les tires des aliens------------------
class alien_bullet(object):
    #fonction d'initialisation
    def __init__(self,shooter):
        self.radius = 5
        self.color = "white"
        self.speed = 5
        self.id = None
        self.shooter = shooter

    #fonction pour creer la bullet    
    def install_in(self, canvas):
        self.canvas_height = int(canvas.cget("height"))    
        if self.shooter.alive:
            x, y = self.shooter.canvas.coords(self.shooter.id)
            
            self.canvas = canvas
            self.id = canvas.create_oval(x - self.radius, y - self.radius,x + self.radius, y + self.radius,fill=self.color)
            self.move_in()
     #fonction pour gerer le mouvemment de la bullet    
    def move_in(self):
        if self.id is not None:
            self.canvas.move(self.id, 0, self.speed)
            x1, y1, x2, y2    = self.canvas.coords(self.id)
            if y1 > self.canvas_height:
                self.canvas.delete(self.id)
                self.id = None 

            else:
                self.canvas.after(30, self.move_in)
        
    

#--------------------class pour gerer la flotte d'aliens--------------------------
class Fleet(object):
    #fonction d'initialisation
    def __init__(self):
        self.aliens_lines =2
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        fleet_size =self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * fleet_size
        self.alien_width = 40
        self.alien_height = 30
        self.direction=-1
        self.jeu=True
        self.score=0
        self.gagner=False
        self.size=fleet_size
        self.alien_bullets=[]

    #fonction pour recuperer la taille de la flotte
    def get_width(self):
        alien_width = 50
        total_width = self.aliens_columns * alien_width + (self.aliens_columns - 1) * self.aliens_inner_gap
        return total_width
    #fonction pour instaler la flotte   
    def install_in(self, canvas):
        self.canvas = canvas
        for i in range(self.aliens_lines):
            for j in range(self.aliens_columns):
                x = 50 + j * (self.alien_width + self.aliens_inner_gap)
                y = 50 + i * (self.alien_height + self.aliens_inner_gap)
                alien = Alien()
                alien.install_in(canvas, x, y, self.alien_width, self.alien_height)
                self.aliens_fleet[i * self.aliens_columns + j] = alien
            
    #fonction pour gerer le mouvement de la flotte    
    def move_in(self, defender):
        dx1, dy1, dx2, dy2 = self.canvas.coords(defender.id)
        x1, y1, x2, y2 = self.canvas.bbox("alien")
        if self.jeu:
            if y2<dy1:
                self.canvas.move("alien", self.direction * self.alien_x_delta, 0)
            
                canvas_width = int(self.canvas.cget('width'))
                if x2 >= canvas_width - 5:
                    self.direction = -1
                    self.canvas.move("alien", 0, self.alien_y_delta)
                if x1 <= 5:
                    self.direction = 1
                    self.canvas.move("alien", 0, self.alien_y_delta)
                
                
            else:
                self.jeu=False
    
    #fonction qui gere les aliens en cas dde collision             
    def manage_touched_aliens_by(self,canvas,defender):
         for alien in self.aliens_fleet:
            if alien.alive:
                x1, y1, x2, y2 = canvas.bbox(alien.id)
                for bullet in defender.fired_bullets:
                    bx1, by1, bx2, by2 = canvas.coords(bullet.id)
                    if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                        alien.touched_by()       
                        alien.alive = False
                        self.score+=1
                        self.size-=1
                        canvas.delete(bullet.id)      
                        defender.fired_bullets.remove(bullet)
                        if self.size == 0:
                            self.gagner = True
    
    #fonction qui gere les alien qui tire                         
    def alien_fire(self,defender):   
        if  defender.defender_alive:
            aliens_vivants = [a for a in self.aliens_fleet if a.alive]
            if aliens_vivants:
              tireur = random.choice(aliens_vivants)
              bullet = alien_bullet(tireur)
              self.alien_bullets.append(bullet) 
              bullet.install_in(self.canvas)

        
        delai = random.randint(1200, 3000) 
        self.canvas.after(delai,lambda: self.alien_fire(defender))
                   

    
#-------------------------class du defender-----------------
class Defender(object):
    #fonction d'initialisation
    def __init__(self):
        self.width = 20
        self.height = 20
        self.move_delta = 20
        self.id = None
        self.max_fired_bullets = 8
        self.fired_bullets = []
        self.alive = True
        self.defender_alive=True

    #fonction qui installe le defender    
    def install_in(self, canvas):
        self.canvas=canvas
        canvas_width = int(canvas.cget('width'))
        canvas_height = int(canvas.cget('height'))
        self.id = canvas.create_rectangle(canvas_width/2 - self.width/2,canvas_height - self.height,canvas_width/2 + self.width/2,canvas_height,fill="white")
        self.canvas.focus_set()
        self.canvas.bind("<Key>", self.move_in)

    #fonction qui gere le mouvemment du defender    
    def move_in(self,event):
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        canvas_width = int(self.canvas.cget('width'))
        if event.keysym == "Left" and x1 - self.move_delta >= 0 :
            self.canvas.move(self.id, -self.move_delta, 0)
        
        elif event.keysym == "Right" and x1 <canvas_width-10:
            self.canvas.move(self.id,self.move_delta , 0)
        
        elif event.keysym == "space":
            self.fire()
        
       
    #fonction qui gere les tire du defender    
    def fire(self):
        if len(self.fired_bullets)<self.max_fired_bullets:
            bullet = Bullet(self)
            bullet.install_in(self.canvas)
            self.fired_bullets.append(bullet)
    
    #fonction qui gere les vie du defender
    def manage_touched_aliens_by(self,canvas,defender):
            if self.defender_alive:
                x1, y1, x2, y2 = canvas.bbox(defender.id)
                for bullet in defender.fired_bullets:
                    bx1, by1, bx2, by2 = canvas.coords(bullet.id)
                    if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                        self.heart.touched_by()       
                        
                        canvas.delete(self.heart.id) 
                        self.heart.number-=1     
                        
                            

                            

#----------------------class Bullet-----------------------
class Bullet(object):
    #fonction d'initialisation
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 8
        self.id = None
        self.shooter = shooter
    #fonction qui instale la bullet     
    def install_in(self, canvas):
        x1, y1, x2, y2 = self.shooter.canvas.coords(self.shooter.id)
        x = (x1 + x2) / 2  
        y = y1 
        self.canvas = canvas
        self.id = canvas.create_oval(x - self.radius, y - self.radius,x + self.radius, y + self.radius,fill=self.color)
        
    #fonction qui gere le mouvement de ma bullet   
    def move_in(self):
        if self.id is not None:
            self.canvas.move(self.id, 0, -self.speed)
            x1, y1, x2, y2 = self.canvas.coords(self.id)
            if y2 < 0:
                self.canvas.delete(self.id)
                self.id = None

                if self in self.shooter.fired_bullets:
                    self.shooter.fired_bullets.remove(self)

#-------------------class game---------------------------     
class Game(object):
    #fonction d'initialisation
    def __init__(self, frame,player_name):
        self.player_name = player_name
        self.frame = frame
        self.fleet = Fleet()
        self.heart=heart()
        self.defender = Defender()
        self.defender.heart = self.heart
        self.height =400
        self.width = self.fleet.get_width()
        self.canvas = tk.Canvas(self.frame, width=self.width,height=self.height,bg="black")
        self.canvas.grid()
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)
        self.fleet.alien_fire(self.defender)
        self.heart.install_in(self.canvas)
        self.score_text = self.canvas.create_text(60, 20, fill="white", font=("Arial", 16),text="Score: "+str(self.fleet.score))
        self.savedscore=False
        self.best_score=0
        self.check_alien_bullets()
    #fonction qui appele les fonction du mouvement 
    def animation(self):
        self.move_bullets()
        self.move_aliens_fleet()
    #fonction qui fait appel a animation chque 10ms
    def start_animation(self):
        self.canvas.after(10, self.animation)
       
    #fonction qui gere le score et le cas de victiore et de perte et fait appel ou mouvement de la bullet
    def move_bullets(self):
        if self.fleet.jeu:
            for bullet in self.defender.fired_bullets:
                bullet.move_in()
            self.canvas.after(10, self.move_bullets)
            self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        elif not self.fleet.jeu and not self.savedscore :
            self.save_score()
            self.savedscore=True
            canvas_width = int(self.canvas.cget("width"))
            canvas_height = int(self.canvas.cget("height"))
            self.perdu = self.canvas.create_text(canvas_width // 2,canvas_height // 2,text="GAME OVER",fill="#FF0000",font=("Arial Black", 48, "bold"),anchor="center")
            self.Best_score()
            self.afficher_bouton_menu()    
        if self.fleet.gagner and not self.savedscore:
            self.save_score()
            self.savedscore=True
            canvas_width = int(self.canvas.cget("width"))
            canvas_height = int(self.canvas.cget("height"))

            self.win = self.canvas.create_text(canvas_width // 2,canvas_height // 2,text="WIN",fill="#33FF33",font=("Arial Black", 48, "bold"),anchor="center")

            self.Best_score()
            self.afficher_bouton_menu() 
            
           
    #fonction qui gere le mouvemment des aliens
    def move_aliens_fleet(self):
        if self.fleet.jeu:
            self.fleet.move_in(self.defender)
            self.canvas.after(200, self.move_aliens_fleet)
            self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        self.jeu_score()
    #fonction qui affiche le score sur l'ecran durant la partie
    def jeu_score(self):
        self.canvas.itemconfig(self.score_text, text="Score: " + str(self.fleet.score))

    #fonction qui enregistre le nom du joueur et son score dans un fichier json   
    def save_score(self):
        try:
            self.f = open("score.json", "r")
            tmp = json.load(self.f)  
            self.f.close()
        except (FileNotFoundError, json.JSONDecodeError):
            tmp = []
        joueur_trouve = False
        for j in tmp:
            if j["joueur"] == self.player_name:
                j["score"] = self.fleet.score   
                joueur_trouve = True
                break
        if not joueur_trouve:
            tmp.append({"joueur": self.player_name, "score": self.fleet.score})
        self.f = open("score.json", "w")
        json.dump(tmp, self.f)                
        for i in tmp:
            if i["score"] > self.best_score:
                self.best_score = i["score"]
        self.f.close()
    #fonction qui affiche le meilleur score 
    def Best_score(self):
        canvas_width = int(self.canvas.cget("width"))
        canvas_height = int(self.canvas.cget("height"))
        
        self.m_score = self.canvas.create_text(canvas_width // 2,canvas_height // 2 + 40,fill="white",font=("Arial", 24, "bold"),text="Best Score:"+ str(self.best_score),anchor="center")

      
    #fonction qui verifie le nombre de vie et defaite si y'as plus de coeur 
    def check_alien_bullets(self):
        if self.fleet.jeu:
            for bullet in self.fleet.alien_bullets:
                if bullet.id is None:
                    continue

                x1, y1, x2, y2 = self.canvas.coords(self.defender.id)
                bx1, by1, bx2, by2 = self.canvas.coords(bullet.id)
                if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                    plus_de_vie = self.defender.heart.touched_by()
                    self.canvas.delete(bullet.id)
                    bullet.id = None
                    if plus_de_vie:
                        self.defender.defender_alive = False
                        self.fleet.jeu = False
                        break 

        self.canvas.after(50, self.check_alien_bullets)
        #retour main menu
    def afficher_bouton_menu(self):
        canvas_width = int(self.canvas.cget("width"))
        canvas_height = int(self.canvas.cget("height"))

 
        self.menu_button = tk.Button(self.frame,text="Menu principal",font=("Arial", 14, "bold"),command=self.retour_menu)
        self.menu_button.place(x=canvas_width // 2 - 60,y=canvas_height // 2 + 100)
    def retour_menu(self):
        self.canvas.destroy()     
        self.menu_button.destroy()
        player = enter_player()
        self.__init__(self.frame, player.name)
        self.start_animation()


#-----------class spaceInvaders--------------------
class SpaceInvaders(object):
    #fonction d'initialisation
    def __init__(self):
        player = enter_player()
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame,player.name)
    #fonction qui appel game et commence le jeu
    def play(self):
        self.game.start_animation()
        self.root.mainloop()
SpaceInvaders().play()