import time
import api_uno as api
import tkinter as tk
import random
import sys

from PIL import Image, ImageTk
from threading import Thread
from base64 import b64decode

WIDTH = 1000
HEIGHT = 625  # format 8/5

USER = None


class UnoApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.title("NOU")
        self.maxsize(WIDTH, HEIGHT)

        self._frame = None
        self.switch_frame(FrameUsername)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.pack_forget()
        self._frame = new_frame
        self._frame.pack()


class FrameUsername(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.color = 'red'
        self.configure(bg=self.color)
        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.image = tk.PhotoImage(file='assets\\background.png')
        tk.Label(master=self, image=self.image).pack()

        self.button_image = ImageTk.PhotoImage(Image.open('assets\\button_login.png').resize((200, 50)))
        label_pseudo = tk.Label(master=self, text="Entrez votre pseudo", bg=self.color)
        label_pseudo.config(font=("Courier", 44))

        self.username_entry = tk.Entry(master=self)
        self.username_entry.config(font=("Courier", 30))

        button_login = tk.Button(master=self, command=self.login, image=self.button_image)

        self.label_error = tk.Label(master=self, bg=self.color)
        self.label_error.config(font=("Arial", 15))

        label_pseudo.place(x=WIDTH / 2 - 300, y=0)
        self.username_entry.place(x=WIDTH / 2 - 250, y=80)
        button_login.place(x=WIDTH / 2 - 125, y=150)
        self.label_error.place(x=WIDTH / 2 - 175, y=200)

    def login(self):
        global USER
        text_recup = self.username_entry.get()
        if text_recup and 30 > len(text_recup) > 2:
            USER = api.Player(text_recup)
            self.master.switch_frame(FrameChooseGame)
        else:
            self.label_error['text'] = "Rentrez un nom d'utilisateur valide"


class FrameChooseGame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, width=WIDTH, height=HEIGHT)
        self.master = master
        self.pack(fill='both', expand=True)
        self.color = 'red'
        self.configure(bg=self.color)
        self.create_widgets()

    def create_widgets(self):
        self.image = tk.PhotoImage(file='assets\\background.png')
        tk.Label(master=self, image=self.image).pack()
        self.button_image = ImageTk.PhotoImage(Image.open('assets\\button_login.png').resize((200, 50)))

        label_join_game = tk.Label(master=self, text="Join Game", bg=self.color)
        label_join_game.config(font=("Courier", 44))
        label_join_game.place(x=WIDTH / 2 - 200, y=0)

        self.entry_join_game = tk.Entry(master=self)
        self.entry_join_game.config(font=("Courier", 30))
        self.entry_join_game.place(x=WIDTH / 2 - 275, y=100)

        tk.Button(master=self, command=self.join_game, image=self.button_image).place(x=WIDTH / 2 - 150, y=200)

        self.label_error = tk.Label(master=self, fg='black', bg=self.color)
        self.label_error.config(font=("Arial", 15))
        self.label_error.place(x=WIDTH / 2 - 150, y=150)

        tk.Button(master=self,
                  command=self.create_game, text="Create Game", width=28,
                  height=2, bg='#e25c00').place(x=WIDTH / 2 - 150, y=275)

    def join_game(self):
        global USER
        text = str(self.entry_join_game.get()).upper()
        if len(text) == 6:
            if USER.join_game(text):
                self.master.switch_frame(FrameGame)
            else:
                self.label_error['text'] = "Rentrez un code valide"
        else:
            self.label_error['text'] = "Rentrez un code valide"

    def create_game(self):
        self.master.switch_frame(FrameCreateGame)


class FrameCreateGame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.color = 'red'
        self.configure(bg=self.color)
        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.image = tk.PhotoImage(file='assets\\background.png')
        tk.Label(master=self, image=self.image).pack()
        self.button_image = ImageTk.PhotoImage(Image.open('assets\\button_login.png').resize((200, 50)))

        label_title = tk.Label(master=self, text='Create Game', bg=self.color)
        label_title.config(font=("Arial", 30))
        label_title.place(x=WIDTH / 2 - 155, y=0)

        label_create_game = tk.Label(master=self, text='Nombre de joueurs', bg=self.color)
        label_create_game.config(font=("Courier", 20))

        self.entry_get_number_of_players = tk.Entry(master=self)
        self.entry_get_number_of_players.config(font=("Courier", 20))

        label_create_game.place(x=WIDTH / 2 - 180, y=80)
        self.entry_get_number_of_players.place(x=WIDTH / 2 - 205, y=120)

        tk.Button(master=self, text="Create game", command=self.create_game).place(x=WIDTH / 2 - 90, y=170)

        self.label_error = tk.Label(master=self, bg=self.color)
        self.label_error.config(font=("Courier", 20))
        self.label_error.place(x=WIDTH / 2 - 280, y=190)

    def create_game(self):
        global USER
        try:
            nb_players = int(self.entry_get_number_of_players.get())
        except ValueError:
            self.label_error['text'] = "Rentrez un nombre valable de joueurs"
        else:
            if 7 > nb_players > 1:
                if USER.create_game(nb_players, 'all'):
                    self.master.switch_frame(FrameGame)
                else:
                    self.label_error['text'] = "Erreur de connection"
            else:
                self.label_error['text'] = "Rentrez un nombre valable de joueurs"


class FrameGame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.stack_coords = (600, 250)
        self.heap_coords = (400, 250)
        self.card_box = {
            'x': (0, 700),
            'y': (HEIGHT, HEIGHT - 200)
        }
        self.images_dic = {}
        self.list_photos = []

        image = Image.open('assets/cards/back.png')
        self.hauteur = image.size[1]
        self.largeur = image.size[0]

        self.create_widgets()

    def create_widgets(self):
        self.button = tk.Button(master=self.master, text="Leave game", command=self.leave_game)
        self.button.pack()

        self.image = 1
        self.detection_clic = False

        self.canevas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg='#427728')
        self.draw_limits()

        self.canevas.bind('<Button-1>', self.clic)
        self.canevas.bind('<B1-Motion>', self.drag)
        self.canevas.bind('<ButtonRelease-1>', self.release)
        self.canevas.bind('<Key>', self.pick)

        self.canevas.focus_set()
        self.canevas.pack()

        image = Image.open('assets/cards/back.png')
        self.list_photos.append(ImageTk.PhotoImage(image))
        self.canevas.create_image(self.heap_coords[0] - self.largeur,
                                  self.heap_coords[1] - self.hauteur, image=self.list_photos[-1])
        self.images_dic[self.canevas.find_all()[self.nb_base:][-1]] = image.filename

        self.thread_create_card = Thread(target=self.check_users_in_game)
        self.thread_create_card.start()

    def draw_limits(self):
        global USER
        self.canevas.create_line(self.card_box['x'][0], self.card_box['y'][1],
                                 WIDTH, self.card_box['y'][1])

        self.canevas.create_line(self.card_box['x'][1], self.card_box['y'][0],
                                 self.card_box['x'][1], self.card_box['y'][1])
        self.canevas.create_text(self.card_box['x'][1] + 150, self.card_box['y'][1] + 100,
                                 text="Play", font="Times 30 italic bold")
        self.canevas.create_text(50, 50, font="Times 30 italic bold")
        self.canevas.create_text(WIDTH / 2, 50, font="Arial 10 bold")
        self.canevas.create_text(self.card_box['x'][1] - 200, self.card_box['y'][1] - 10, font="Arial 10 bold")
        self.canevas.create_text(100, 150, font="Arial 20 bold")
        self.canevas.create_text(WIDTH - 75, 20, font="Arial 20 bold", text=USER.game.game_code)

        self.nb_base = len(self.canevas.find_all())

    def clic(self, event):
        self.image = 1
        x = event.x
        y = event.y

        if self.heap_coords[0] - 2 * self.largeur <= x <= self.heap_coords[0] \
                and self.heap_coords[1] - 2 * self.hauteur < y < self.heap_coords[1]:
            return None
        if self.stack_coords[0] - 2 * self.largeur <= x <= self.stack_coords[0] \
                and self.stack_coords[1] - 2 * self.hauteur < y < self.stack_coords[1]:
            return None
        for card in self.canevas.find_all()[self.nb_base:]:
            x_min, y_min = self.canevas.coords(card)
            x_min -= self.largeur / 2
            y_min -= self.hauteur / 2
            if x_min <= x <= x_min + self.largeur and y_min <= y < y_min + self.hauteur:
                self.detection_clic = True
                self.image = card
                break
            else:
                self.detection_clic = False

    def drag(self, event):
        x = event.x + (self.largeur / 2)
        y = event.y + (self.hauteur / 2)
        if self.detection_clic:
            if x < self.largeur:
                x = self.largeur
            if y < self.hauteur:
                y = self.hauteur
            if y > HEIGHT + self.hauteur / 2:
                y = HEIGHT + self.hauteur / 2
            if y < self.card_box['y'][1] + self.hauteur * 1.5:
                y = self.card_box['y'][1] + self.hauteur * 1.5
            if not self.can_play(self.image):
                if x > self.card_box['x'][1] + self.largeur / 2:
                    x = self.card_box['x'][1] + self.largeur / 2
            else:
                if x > WIDTH + self.largeur / 2:
                    x = WIDTH + self.largeur / 2

            self.canevas.coords(self.image, x - self.largeur, y - self.hauteur)

    def release(self, event):
        if self.detection_clic:
            x = event.x + (self.largeur / 2)
            y = event.y + (self.hauteur / 2)

            hold_card_infos = self.images_dic[self.image][self.images_dic[self.image].rfind('/') + 1:-4].split('_')
            card = {
                'color': hold_card_infos[0],
                'number': int(hold_card_infos[1])
            }
            if x > self.card_box['x'][1] + self.largeur / 2 and self.can_play(self.image):
                main = False
                if card['color'] == 'black':
                    trad = {'bleu': 'blue', 'rouge': 'red', 'jaune': 'yellow', 'vert': 'green'}
                    card['color_changement'] = trad[self.ask_color()]
                    main = True
                rep = USER.play(card)
                if rep:
                    Thread(target=self.clean_timer).start()
                    Thread(
                        target=self.smooth_deplacement,
                        args=
                        ([x, y], (self.stack_coords[0] - self.largeur, self.stack_coords[1] - self.hauteur))).start()
                    self.must_play = False
                if main:
                    self.master.mainloop()

    def check_users_in_game(self):
        global USER
        self.continue_thread = True
        modif = True
        while True:
            if not self.continue_thread:
                sys.exit(0)
            if USER.new_users:
                self.canevas.itemconfig(5, text=f'{USER.new_users} join game')
                USER.new_users = ""
                modif = True
            if USER.gone_user:
                self.canevas.itemconfig(5, text=f'{USER.gone_user} left the game')
                modif = True
            if modif:
                self.canevas.itemconfig(4, text=f'{len(USER.users)}/{USER.game.max_users}')
                modif = False
            if USER.has_started:
                self.canevas.itemconfig(4, text="", font="Arial 10 bold")
                self.canevas.itemconfig(5, text="Game have started")
                break
        thread_game = Thread(target=self.game)
        thread_game.start()

    def game(self):
        global USER
        self.button.destroy()
        self.show_cards()
        self.must_play = False
        while True:
            if USER.winner:
                self.game_ending()

            if USER.cards != self.mycards:
                diff = len(USER.cards) - len(self.mycards)
                if diff > 0:
                    for i in range(1, diff + 1):
                        self.place_card(USER.cards[-i])
                self.mycards = USER.cards

            if self.cards != USER.player_number_of_cards:
                self.cards = USER.player_number_of_cards
                self.canevas.itemconfig(5, text=' '.join([f'{player[2]}: {player[1]}'
                                                          for player in self.cards]), font="Arial 20 bold")
            if self.last_card != USER.last_card:
                self.place_card(USER.last_card, place='stack')
                self.last_card = USER.last_card

            if self.current_user != USER.actual_player and USER.actual_player:
                self.current_user = USER.actual_player
                self.canevas.itemconfig(6, text=f'Au tour de {self.current_user}')

            if USER.can_play_var and not self.must_play:
                self.timer = Timer(20, 'down', func=self.print_timer_to_screen)
                self.timer.start()
                USER.can_play_var = False
                self.must_play = True
                self.canevas.itemconfig(7, text='A votre tour !!!\nAppuyez sur p \npour piocher')
            if self.must_play:
                if self.timer.is_finish():
                    USER.pick()
                    Thread(target=self.clean_timer).start()
                    self.must_play = False

    def can_play(self, card_id):
        hold_card_infos = self.images_dic[card_id][self.images_dic[card_id].rfind('/') + 1:-4].split('_')
        if hold_card_infos[0] == self.last_card['color'] or int(hold_card_infos[1]) == self.last_card['number'] or\
                self.last_card['color'] == 'black' or hold_card_infos[0] == 'black':
            return True
        else:
            return False

    def leave_game(self):
        global USER
        if self.thread_create_card.is_alive():
            if USER.leave_game():
                self.continue_thread = False
                self.master.switch_frame(FrameChooseGame)

    def show_cards(self):
        while True:
            if USER.cards:
                for card in USER.cards:
                    self.place_card(card)
                self.last_card = ""
                self.cards = ""
                self.mycards = USER.cards
                self.current_user = ""
                break

    def place_card(self, card, place="base"):
        self.image_choice = Image.open(f'assets/cards/{card["color"]}_{card["number"]}.png')
        self.list_photos.append(ImageTk.PhotoImage(self.image_choice))
        if place == 'stack':
            self.canevas.create_image(self.stack_coords[0] - self.largeur,
                                      self.stack_coords[1] - self.hauteur, image=self.list_photos[-1])
        else:
            self.canevas.create_image(random.randint(self.card_box['x'][0] + 20, self.card_box['x'][1] - 20),
                                      random.randint(self.card_box['y'][1] + 30, self.card_box['y'][0]),
                                      image=self.list_photos[-1])

        self.images_dic[self.canevas.find_all()[self.nb_base:][-1]] = self.image_choice.filename

    def smooth_deplacement(self, start: list, arrived: tuple, delta_time=25):
        vector = (start[0] - arrived[0]) / delta_time, (start[1] - arrived[1]) / delta_time
        for _ in range(delta_time):
            start[0] -= vector[0]
            start[1] -= vector[1]
            self.canevas.coords(self.image, start[0], start[1])

    def print_timer_to_screen(self, count=None):
        self.canevas.itemconfig(4, text=count, font='Arial 30 bold')

    def clean_timer(self):
        self.timer.stop()
        self.canevas.itemconfig(4, text='')
        self.canevas.itemconfig(7, text='')

    def ask_color(self):
        self.ask_toplevel = tk.Toplevel(master=self, bg='#427728')
        var_recup = tk.StringVar(value='bleu')

        for option in ['bleu', 'rouge', 'vert', 'jaune']:
            tk.Radiobutton(master=self.ask_toplevel,
                           text=option,
                           variable=var_recup,
                           value=option,
                           bg='#427728', ).pack(anchor="w")
        tk.Button(master=self.ask_toplevel, text='Submit', command=self.quit_asktoplevel).pack()

        self.ask_toplevel.mainloop()
        return str(var_recup.get())

    def quit_asktoplevel(self):
        self.ask_toplevel.quit()
        self.ask_toplevel.destroy()

    def pick(self, event):
        if event.keysym == 'p' and self.must_play:
            USER.pick()
            Thread(target=self.clean_timer).start()
            self.must_play = False

    def game_ending(self):
        self.canevas.itemconfig(5, text=f'{USER.winner} has won')
        tk.Button(master=self, text='Accueil', command=self.return_to_main).pack()

    def return_to_main(self):
        self.master.switch(FrameChooseGame)


class Timer:
    def __init__(self, delta_time, sens='up', func=None):
        self._time_reset = delta_time
        self.time_compteur = 0 if sens == 'up' else delta_time
        self.sens = sens
        self._restart = False
        self.callback = func

    def _start(self):
        if self.sens == 'up':
            for self.time_compteur in range(self._time_reset + 1):
                if self._restart:
                    break
                time.sleep(1)
                if self.callback is not None:
                    self.callback(count=self.time_compteur)
        else:
            for self.time_compteur in reversed(range(self._time_reset + 1)):
                if self._restart:
                    break
                time.sleep(1)
                if self.callback is not None:
                    self.callback(count=self.time_compteur)
        self._restart = False

    def start(self):
        self._restart = False
        Thread(target=self._start).start()

    def is_finish(self):
        if self.sens == 'up':
            return True if self.time_compteur == self._time_reset + 1 else False
        else:
            return True if self.time_compteur == 0 else False

    def restart(self):
        self._restart = True
        while self._restart:
            pass
        self.time_compteur = 0 if self.sens == 'up' else self._time_reset
        self.start()

    def __int__(self):
        return self.time_compteur

    def stop(self):
        self._restart = True
        while self._restart:
            pass


if __name__ == '__main__':
    app = UnoApp()
    app.iconbitmap('assets/icon.ico')
    app.mainloop()
