import math
import random
from random import randint
from tkinter import filedialog
from tkinter import messagebox
from collections import deque
from time import time, sleep
# from sound import Sound

import cv2
import numpy as np
import pandas as pd
import pygame, numpy, tkinter
import os, sys, pickle

import tensorflow as tf
from PySide2.QtWidgets import QMessageBox
from tensorflow.keras.models import model_from_json

tf.get_logger().setLevel('INFO')
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import InputLayer
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential

# from nn import create_and_save_ai, Model

onWindows = sys.platform.startswith('win')
if onWindows:
    import win32gui

### Initialize stuff ###

# Center window
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Script's directory:
path = ''
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    path = sys._MEIPASS
else:
    path = os.path.dirname(os.path.abspath(__file__))
path += os.sep

white = 240, 240, 240
grey = 128, 128, 128
darkgrey = 200, 200, 200
black = 0, 0, 0
red = 128, 0, 0
grass = 0, 100, 0
brown_radius = 0

colors = {}
colors['blue'] = 0, 0, 128
colors['green'] = 0, 165, 0
colors['orange'] = 255, 165, 0
colors['yellow'] = 128, 128, 0
colors['purple'] = 128, 0, 128
colors['brown'] = 130, 90, 44
colors['teal'] = 0, 128, 128
colors['pink'] = 255, 128, 255
colors['cyan'] = 0, 128, 255

# Window creation:
pygame.init()  # Init all imported pygame modules
iconPath = path + 'icon.png'
windowTitle = 'Goblins & Kittens'
pygame.display.set_caption(windowTitle)
if os.path.exists(iconPath):
    icon = pygame.image.load(iconPath)
    pygame.display.set_icon(icon)
windowSize = 300, 200
res = 20
max_hp = 3
players = 2
width, height = windowSize
safety_radius = 0.7
screen = pygame.display.set_mode(windowSize)
screenColor = white
screen.fill(screenColor)

# Get focus back to main window after dialogs on Windows:
windowHandle = None


def updateWindowHandle():
    global windowHandle
    if onWindows:
        windowHandle = win32gui.FindWindow(None, windowTitle)


updateWindowHandle()


def focusWindow():
    if onWindows:
        win32gui.SetForegroundWindow(windowHandle)


# Init dialogs:
tkRoot = tkinter.Tk()  # Create Tk main window
if os.path.exists(iconPath):
    tkRoot.iconphoto(True, tkinter.PhotoImage(file=iconPath))  # Set icon
dx = (tkRoot.winfo_screenwidth() - width) // 2
dy = (tkRoot.winfo_screenheight() - height) // 2
tkRoot.geometry('{}x{}+{}+{}'.format(width, height, dx, dy))  # Center Tk window
tkRoot.withdraw()  # Hide Tk main window
savesDir = path + 'saves'
if not os.path.exists(savesDir):
    os.makedirs(savesDir)

# Cells per axis
cellsX, cellsY = width // res, height // res

# Dimensions of cells:
cellWidth = width / cellsX
cellHeight = height / cellsY

# Create deque to store up to 1000 states
states = deque(maxlen=1000)

# Cell states: live = 1, dead = 0
gameState = numpy.zeros((cellsX, cellsY), int)

# Values to serialize:
stepByStep = False
wraparound = True
# overlay = False
delayInt = 1  # Speed
max_level = 25

# Other values:
default_delay = 0.1
delay = default_delay
gamePaused = False
mouseClicked = False
fullscreen = False
cellValue = 0
lastTime = 0.0

# Matrix that holds the cells borders
poly = numpy.full((cellsX, cellsY), None)


def updateCellsBorders():
    ''' Update cells borders with the current width and height for each cell '''
    for y in range(0, cellsY):
        for x in range(0, cellsX):
            # Rectangle to be drawn with upper left corner (x, y)
            poly[x, y] = [(x * cellWidth, y * cellHeight), \
                          ((x + 1) * cellWidth, y * cellHeight), \
                          ((x + 1) * cellWidth, (y + 1) * cellHeight), \
                          (x * cellWidth, (y + 1) * cellHeight)]


updateCellsBorders()

# Patterns:

# Flickering cross
gameState[6, 6] = 1
gameState[7, 6] = 1
gameState[7, 7] = 1
gameState[8, 6] = 1
# Microscope:
# gameState[19, 8] = 1
# gameState[20, 5] = 1
# gameState[20, 6] = 1
# gameState[20, 8] = 1
# gameState[21, 7] = 1
# gameState[21, 8] = 1
# Glider:
gameState[cellsX - 10 + 1, 8] = 1
gameState[cellsX - 10 + 2, 6] = 1
gameState[cellsX - 10 + 2, 8] = 1
gameState[cellsX - 10 + 3, 7] = 1
gameState[cellsX - 10 + 3, 8] = 1
# Lotus flower
# gameState[6, 20] = 1
# gameState[6, 21] = 1
# gameState[7, 19] = 1
# gameState[7, 20] = 1
# gameState[7, 22] = 1
# gameState[8, 20] = 1
# gameState[8, 21] = 1
# Pentadecathlon
# gameState[19, 17] = 1
# gameState[19, 18] = 1
# gameState[19, 19] = 1
# gameState[19, 20] = 1
# gameState[19, 21] = 1
# gameState[19, 22] = 1
# gameState[19, 23] = 1
# gameState[19, 24] = 1
# gameState[20, 17] = 1
# gameState[20, 19] = 1
# gameState[20, 20] = 1
# gameState[20, 21] = 1
# gameState[20, 22] = 1
# gameState[20, 24] = 1
# gameState[21, 17] = 1
# gameState[21, 18] = 1
# gameState[21, 19] = 1
# gameState[21, 20] = 1
# gameState[21, 21] = 1
# gameState[21, 22] = 1
# gameState[21, 23] = 1
# gameState[21, 24] = 1
# Blinker:
# gameState[cellsX - 10 + 2, 19] = 1
# gameState[cellsX - 10 + 2, 20] = 1
# gameState[cellsX - 10 + 2, 21] = 1

circ_rad = 10


def get_coords():
    coords = [(7, 7),
              (7, 15),
              (7, 21),
              (15, 7),
              (15, 15),
              (15, 21),
              (21, 7),
              (21, 15),
              (21, 21)]

    for i in range(20):
        coords.append((randint(4, 26), randint(4, 26)))
    return coords


def check_if_future_safe(choice, future):
    x_mid = round(len(future[0]) / 2)
    y_mid = x_mid

    if choice == 0:  # Stay put
        if future[y_mid][x_mid]:
            return True
    if choice == 1:  # Move up
        if future[y_mid - 1][x_mid]:
            return True
    if choice == 2:  # Move down
        if future[y_mid + 1][x_mid]:
            return True
    if choice == 3:  # Move left
        if future[y_mid][x_mid - 1]:
            return True
    if choice == 4:  # Move down
        if future[y_mid][x_mid + 1]:
            return True


class classroom:
    def __init__(self):
        self.moving_sprites = pygame.sprite.Group()
        self.students = []
        self.init_students()
        self.reporter = player()
        self.ticker = []
        self.ticker_norm = None
        self.reporter.color = self.reporter.b_color
        self.reporter.living = False
        self.transition = False
        self.reporter.lives = -1
        self.battle = 0
        self.trials = 0
        self.round = 0
        self.observations = []
        self.tvs = []

        self.r = (windowSize[1] // res) // 2
        self.n = (self.r * 2 + 1) ** 2
        if os.path.isfile('gol.h5'):
            json_file = open('gol.json', 'r')
            load_model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(load_model_json)
            self.model.load_weights('gol.h5')
            print('Loaded existing model')
        else:
            self.model = Sequential()

            self.model.add(InputLayer(batch_input_shape=(1, self.n)))
            # self.model.add(Dropout(0.2, batch_input_shape=(1, self.n)))
            self.model.add(
                Dense(self.n * 3, activation='relu', kernel_initializer='random_normal', bias_initializer='zeros'))
            self.model.add(Dropout(0.2))
            self.model.add(
                Dense(self.n * 3, activation='relu', kernel_initializer='random_normal', bias_initializer='zeros'))
            self.model.add(Dropout(0.2))
            self.model.add(
                Dense(self.n * 3, activation='relu', kernel_initializer='random_normal', bias_initializer='zeros'))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(5, activation='linear'))

        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    def init_students(self):
        for s in self.students:
            s.kill()
        self.students = []
        for _ in range(players):
            p = player()
            p.x = randint(0, cellsX // 2)
            p.y = randint(0, cellsY // 2)
            self.students.append(p)
            self.moving_sprites.add(p)

    def report_best(self, verbose=True):
        max_score = 0
        max_living_score = 0
        winner = None
        living_winner = None
        report = ""
        for i, student in enumerate(self.students):
            if student.score > max_score:
                max_score = student.score
                winner = i + 1
                student.gold = True

                living_winner = winner
                max_living_score = max_score
                if student.living:
                    living_winner = i + 1
                    max_living_score = student.score
        for student in self.students:
            if student.living and student.score != max_score:
                student.gold = False
            if not student.living and student.score != max_score:
                student.gold = False

        report = f"P{winner} in the lead with {max_score}!"

        if living_winner:
            report = f"P{living_winner} wins with {max_living_score}!"

        if verbose:
            print(report)
            if (not p1 and max_living_score > 29):
                pygame.mixer.music.load(ding_sound)
                pygame.mixer.music.play()
                # if p1.x == locations[0].x and p1.y == locations[0].y:
                if p1:
                    p1.x = cellsX - 1
                    p1.y = cellsY - 1
            elif (p1 and not p1.living) or (p1 and max_living_score > 29):
                pygame.mixer.music.load(oof_sound)
                pygame.mixer.music.play()

                sleep(5)

        return {'winner': winner, 'max_score': max_score}

    def draw_scoreboard(self):
        font = pygame.font.Font('freesansbold.ttf', 22)
        best = c1.report_best(verbose=False)

        for i, student in enumerate(self.students):
            line = f"P{i + 1} {'I' * student.lives} {student.score}"
            if student.score == best['max_score'] and best['max_score'] >= 30:
                line += " *"
            if student.gold:
                text = font.render(line, True, (255, 255, 0), grey)
            else:
                text = font.render(line, True, student.color, grey)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.y += i * 22 + 12
            screen.blit(text, textRect)

        report_line = f"Round {self.battle}.{self.trials}.{self.round}"
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(report_line, True, darkgrey, grey)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.y += 0
        screen.blit(text, textRect)

        for i, num in enumerate(self.ticker):
            ticker_line = f"{num}"
            font = pygame.font.Font('freesansbold.ttf', 10)
            text = font.render(ticker_line, True, darkgrey, grey)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.y += windowSize[1] - res // 2
            textRect.x += i * res
            screen.blit(text, textRect)

    def draw_living(self):
        if len(locations) > 0:
            for loc in locations:
                loc.drawPlayer()
        if not p1:
            for student in self.students:
                if student.color == student.b_color and not student.gold:
                    student.drawPlayer()
            for student in self.students:
                if student.color == student.a_color and not student.gold:
                    student.drawPlayer()
            for student in self.students:
                if student.gold:
                    student.drawPlayer()

        if p1:
            for student in self.students:
                if student.hp > 0:
                    student.drawPlayer()
            if p1.living:
                p1.drawPlayer()

            self.moving_sprites.image = self.students[0].sprites[self.students[0].current_sprite]
            self.moving_sprites.draw(screen)
            self.moving_sprites.update()
            pygame.display.flip()

    def count_living(self):
        living_count = 0
        for student in self.students:
            if student.living:
                living_count += 1
        return living_count

    def count_living_ratio(self):
        return self.count_living() / len(self.students)

    def resuscitate(self):
        still_alive = False
        max_score = 0
        for student in self.students:
            if student.score > max_score:
                max_score = student.score
            student.living = True
            student.lives = 3
            if student.color == student.a_color:
                still_alive = True
        if not still_alive or max_score >= 30 or (p1 and round(p1.x) == locations[0].x and round(p1.y) == locations[0].y):
            if max_score >= 30:
                self.ticker.append(len(self.observations))
            self.round = 0
            self.trials = 0
            self.battle += 1
            for student in self.students:
                student.color = student.a_color
                student.score = 0
            if len(self.observations) > 0:
                observations = np.array(self.observations)[:, 0, :]
                tvs = np.array(self.tvs)[:, 0, :]
                c1.model.fit(observations, tvs, epochs=1, verbose=0)
                self.observations = []
                self.tvs = []

    def rebase_students(self):
        b_score = 0
        if p1:
            p1.action = 0
        for student in self.students:
            if student.color == student.b_color:
                b_score += student.score
            student.reward = 0
            student.action = 0
            student.observation = None
        self.reporter.score = b_score
        self.round += 1

    def observe(self, gameState):
        for student in self.students:
            if student.living:
                student.stagnation += 1
                student.get_observable(gameState)
            else:
                student.stagnation = 1000

    def act(self):
        global flipper
        for i, student in enumerate(self.students):
            if student.living:
                student.get_action()
            if student.living:

                if not student.human:
                    student.move_on_prediction(student.action)
        if p1 and p1.living:
            p1.move_on_prediction(p1.action)

    def reward_living(self, x, y):
        best = c1.report_best(verbose=False)
        for student in self.students:
            if x == student.x and y == student.y and student.living:
                student.stagnation = 0
                student.reward = student.score
                if student.action == 0:
                    student.reward *= 2
                student.score += 1

    def punish_living(self, x, y):
        for student in self.students:
            if student.x == x and student.y == y and student.living:
                student.lives -= 1
                student.reward = -.5
                # student.living = False

                if student.lives <= 0:
                    student.stagnation = 0
                    # student.score = 0
                    # student.x = random.choice([-cellsX, 2*cellsX])
                    # student.y = random.choice([-cellsY, 2*cellsY])
                    # student.x = cellsX*2
                    # student.y = cellsY*2

    def update_model(self):
        for student in self.students:
            if student.living and student.reward != 0:
                target = student.reward + discount_factor * np.max(c1.model.predict(student.observation)[0])
                target_vector = c1.model.predict(student.observation)[0]
                target_vector[student.action] = target
                tv = target_vector.reshape(-1, 5)
                self.observations.append(student.observation)
                self.tvs.append(tv)

    def reset_students(self):
        b_count = 0
        for s in self.students:
            if s.color[0] == 128:
                b_count += 1

        for student in self.students:
            if b_count == len(self.students):
                student.color = student.a_color
            # student.score = 0
            student.stagnation = 0
            student.deaths = 0
            # student.x = cellsX//2 + randint(-5, 5)
            # student.y = cellsY//2 + randint(-5, 5)
            # x_window = int(cellsX - (cellsX/2)**self.battle)
            student.x = random.randint(0, int(cellsX * ((1 + self.battle) / (2 + self.battle))))
            student.y = random.randint(0, int(cellsY * ((1 + self.battle) / (2 + self.battle))))
        self.resuscitate()

    def stagnation(self):
        min_stagnation = self.get_min_stag()
        best = self.report_best(verbose=False)

        global gameState

        if not p1:
            if len(states) % 30 == 1:
                gameState = numpy.random.choice(a=[0, 1], size=(cellsX, cellsY))
                for x in range(int(cellsX // 2), cellsX - 1):
                    for y in range(int(cellsY // 2), cellsY - 1):
                        gameState[x, y] = 0

            if self.count_living() <= 1:
                print(f"P{best['winner']} Last Alive with {best['max_score']}")
                return True

            if min_stagnation > 30:
                print("Stagnation... No points scored in 30 rounds")
                return True

            for student in self.students:
                if student.score >= 30:
                    print(f"Winner!... {student.score} points scored")
                    return True

            if gameState.sum() == 0:
                print(f"No cloud cover...")
                gameState = numpy.random.choice(a=[0, 1], size=(cellsX, cellsY))
                for x in range(int(cellsX // 2), cellsX - 1):
                    for y in range(int(cellsY // 2), cellsY - 1):
                        gameState[x, y] = 0
                return True

        if p1 and round(p1.x) == locations[0].x and round(p1.y) == locations[0].y:
            print("Player found the Castle!!!")
            return True

        if p1 and p1.hp == 0:
            p1.hp = 3
            p1.lives = 3
            return True

        return False

    def get_min_stag(self):
        min_stagnation = 1000
        for student in self.students:
            if student.stagnation < min_stagnation:
                min_stagnation = student.stagnation
        return min_stagnation

    def report(self):
        for i, s in enumerate(self.students):
            if s.living:
                print(f"P{i + 1} {'I' * s.lives} {s.score} | ", end='')
            else:
                print(f"   {'I' * s.lives}    {s.score} | ", end='')
        print()


class player(pygame.sprite.Sprite):
    def __init__(self, color=None):
        pygame.sprite.Sprite.__init__(self)
        if color:
            self.color = (0, 0, 255)
            self.x = 2 * cellsX // 3
            self.y = cellsY // 3
        else:
            a = randint(0, 128)
            self.a_color = tuple([a, 128, 128 - a])
            # self.a_color = tuple([a, 255-a, randint(0, 255)])
            # self.b_color = tuple([128, max(self.a_color[1]*2, 255), 255-self.a_color[2]])
            self.b_color = (0, grass[1]/2, 0)
            self.color = self.a_color
            self.x = cellsX // 2
            self.y = cellsY // 2
        self.team = None
        self.lives = 3
        self.hp = 3
        self.dmg = 1
        self.score = 0
        self.reward = 0
        self.kills = 0
        self.armor = 0
        self.speed_mod = 1
        self.current_sprite = 0
        self.sprites = []
        self.set_goblin()
        self.gold = False
        self.sneak = False
        self.oof = False
        self.rawr = False
        self.ding = False
        self.deaths = 0
        self.stagnation = 0
        self.action = 0
        self.living = True
        self.observation = None
        self.human = False

    def set_goblin(self):
        self.human = False
        self.sprites.append(pygame.image.load("sprites/Goblin/R0Goblin Dying Pose.png"))
        self.sprites.append(pygame.image.load("sprites/Goblin/R0Goblin Dying Pose.png"))
        self.sprites.append(pygame.image.load("sprites/Goblin/R0Goblin Dying Pose.png"))
        self.sprites.append(pygame.image.load("sprites/Goblin/R1Goblin Dying Pose.png"))
        self.sprites.append(pygame.image.load("sprites/Goblin/R1Goblin Dying Pose.png"))
        self.sprites.append(pygame.image.load("sprites/Goblin/R1Goblin Dying Pose.png"))

    def drawPlayer(self):
        ''' Draw player's cell with coordinates (x, y) '''

        if self.color == (0, 0, 0):
            pygame.draw.rect(screen, black, pygame.Rect(0, 0, res, res))
            pygame.draw.rect(screen, (165, 42, 42), pygame.Rect(res/3+1, res/2, res/3+1, res/2))

            if c1.battle > 0:
                pygame.draw.rect(screen, black, pygame.Rect(res*(cellsX-1), res*(cellsY-1), res, res))
                pygame.draw.rect(screen, (165, 42, 42), pygame.Rect((cellsX-1)*res-1+res/3+2, res*(cellsY-1)+res/2, res/3+1, res/2))

        else:
            pygame.draw.circle(screen, self.color, [res * self.x + circ_rad, res * self.y + circ_rad], circ_rad)

            self.current_sprite += 0
            # self.image = self.sprites[0]
            self.image = self.sprites[int((self.current_sprite//len(self.sprites)) % len(self.sprites))]
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (int(self.size[0]/3), int(self.size[1]/3)))
            self.rect = self.image.get_rect()
            self.rect.center = [int(self.x*res)+res//2, self.y*res+res//2]


        if self.reward < 0 and overlay:
            pygame.draw.circle(screen, red, [res * self.x + circ_rad, res * self.y + circ_rad], circ_rad * .5)
        if self.reward > 0 and overlay:
            pygame.draw.rect(screen, white,
                             pygame.Rect(res * self.x + circ_rad - 1, res * self.y, circ_rad * .25, circ_rad * 2))
            pygame.draw.rect(screen, white,
                             pygame.Rect(res * self.x, res * self.y + circ_rad - 1, circ_rad * 2, circ_rad * 0.25))
        if self.lives <= 0 and self.color == self.a_color:
            self.color = self.b_color
            self.dmg = 2
            self.speed_mod = 2
            self.rawr = True
            self.lives = -1
        if self.gold and overlay:
            pygame.draw.rect(screen, (255, 255, 0),
                             pygame.Rect(res * self.x + circ_rad // 2, res * self.y - 1, circ_rad, circ_rad // 2))

    def draw_scoreboard(self):
        global brown_radius
        turf = (100 - min(brown_radius, 100), 100, 0)
        font = pygame.font.Font('freesansbold.ttf', 22)
        line = f"Level {c1.battle}"
        text = font.render(line, True, p1.color, turf)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.x += windowSize[0] * 3 // 4 - 12
        textRect.y += 0
        screen.blit(text, textRect)

        line = f"Lives {'l' * self.hp}"
        text = font.render(line, True, p1.color, turf)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.x += windowSize[0] * 3 // 4 - 12
        textRect.y += res
        screen.blit(text, textRect)

        font = pygame.font.Font('freesansbold.ttf', 12)
        percent = round((float(self.dmg)-1)*100)
        if percent > 0:
            # print(f"DMG {percent} with damage {self.dmg}")
            line = f"+{percent}% DMG"
            text = font.render(line, True, p1.color, turf)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.x += windowSize[0] * 3 // 4 - 12
            textRect.y += res*2 + res*2//3
            screen.blit(text, textRect)
        if self.armor > 0:
            if self.armor == 1:
                line = f"Light Armor"
            elif self.armor >= 2:
                line = f"Heavy Armor"
                self.armor = 2

            text = font.render(line, True, p1.color, turf)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.x += windowSize[0]* 3 // 4 - 12
            textRect.y += res * 2
            screen.blit(text, textRect)

    def get_observable(self, state):
        if p1:
            state[round(p1.x), round(p1.y)] = 1
        arr = [-1] * c1.n
        map = []
        i = 0
        for row in range(round(self.y) - c1.r, round(self.y) + c1.r + 1):
            temp = []
            for col in range(round(self.x) - c1.r, round(self.x) + c1.r + 1):
                # try:
                if state[col % cellsX, row % cellsY]:
                    arr[i] = state[col % cellsX, row % cellsY]
                # except IndexError:
                #     pass
                inverse_radius = 1 / (1 + math.sqrt((row - self.y) ** 2 + (col - self.x) ** 2) / 2)
                if arr[i] == -1:
                    arr[i] *= inverse_radius
                temp.append(arr[i])
                i += 1
            map.append(temp)
        map = np.array(map, np.float)
        arr = np.array(arr, np.float)

        self.observation = arr.reshape(1, c1.n)

    def get_action(self):
        if np.random.random() < eps or len(states) == 0:
            self.action = np.random.choice(choices)
        else:
            self.action = np.argmax(c1.model.predict(self.observation)[0])

    def move_on_prediction(self, prediction):
        wall = 0
        if prediction == 1:  # UP
            if self.y > wall:
                self.y -= 1/self.speed_mod
            elif self != p1:
                self.y = cellsY - 1
        if prediction == 2:  # DOWN
            if self.y <= cellsY - wall - 2:
                self.y += 1/self.speed_mod
            elif self != p1:
                self.y = 0
        if prediction == 3:  # LEFT
            if self.x > wall:
                self.x -= 1/self.speed_mod
            elif self != p1:
                self.x = cellsX - 1
        if prediction == 4:  # RIGHT
            if self.x <= cellsX - wall - 2:
                self.x += 1/self.speed_mod
            elif self != p1:
                self.x = 0


# Define landscape
locations = []
castle = player()
# castle.set_goblin()
castle.color = (0, 0, 0)
castle.x = 0
castle.y = 0
locations.append(castle)
c1 = classroom()
p1 = None
overlay = False
p1 = player()
# p1.set_goblin()
p1.x = cellsX - 1
p1.y = cellsY - 1
p1.human = True
p1.color = (0, 0, 128)


### Welcome screen and game controls ###

def textWidth(text, font):
    ''' Size in pixels of the given text '''
    textSurf = font.render(text, True, black)
    return textSurf.get_rect().width


def displayMessage(text, font, dx, dy):
    ''' Show a message starting at (dx, dy). If dx=-1 then the message
    will be centered horizontally. '''
    textSurf = font.render(text, True, black)
    textRect = textSurf.get_rect()
    if dx == -1:
        textRect.centerx = width / 2
        textRect.top = dy
    else:
        textRect.left = dx
        textRect.top = dy
    screen.blit(textSurf, textRect)


def isTryingToQuit():
    ''' Determine whether the user is trying to quit the game with Alt + F4 '''
    pressed_keys = pygame.key.get_pressed()
    alt = pressed_keys[pygame.K_LALT] or \
          pressed_keys[pygame.K_RALT]
    f4 = pressed_keys[pygame.K_F4]
    return alt and f4


def waitForTheUser():
    ''' Wait for the user to press any key to continue '''
    while True:
        if isTryingToQuit():
            sys.exit()
        for event in pygame.event.get():
            # Close window when close button is pressed
            if event.type == pygame.QUIT:
                sys.exit()
            # Go to the next screen when any key is pressed
            elif event.type == pygame.KEYDOWN:
                return


# # Fonts:
textFont = pygame.font.SysFont('arial', 17)
continueFont = pygame.font.SysFont('arial', 14)
# # titleFont = pygame.font.Font(pygame.font.get_default_font(), 25)
# # I was forced to replace the line above for the line below
# # because Pyinstaller would find an error otherwise
titleFont = pygame.font.SysFont('arial', 25)

continueText = '[Press any key to continue]'
continueTextWidth = textWidth(continueText, continueFont)


def displayContinueMessage():
    continueDx = width - continueTextWidth - 3
    continueDy = height - 21
    displayMessage(continueText, continueFont, continueDx, continueDy)


def showControls():
    ''' Show game controls screen '''

    # Clean screen to avoid superposition wih previous state
    screen.fill(screenColor)

    controls = ['* Use the mouse to toggle cell states. Drag the mouse from a dead cell',
                'and move around to make cells you hover over become alive. Similarly,',
                'drag the mouse from a live cell to kill the cells you touch.', '',
                '* Press space bar to pause/resume the game.', '',
                '* Press C to kill all cells.', '',
                '* Use A and D to accelerate and deaccelerate the game.', '',
                '* Press M to mute/unmute.', '',
                '* Use the left and right arrow keys to play previous and next song.', '',
                '* Press R to generate a random game state.', '',
                '* Use tab to activate/deactivate step-by-step mode, then use space bar',
                'to go to the next generation.', '',
                '* Hit backspace whenever you want to return to the previous game state.', '',
                '* Press W to toggle wrapping and non-wrapping versions of the grid.', '',
                '* Use S to save the game and O to open saved games.', '',
                '* Use F to toggle between windowed and fullscreen mode, you can also',
                'press escape to go back to windowed mode. Keep in mind that you can\'t',
                'save or load games when you are in fullscreen mode.', '',
                '* Use H to show this screen again with the game controls.']

    lineHeight = 18
    titleHeight = 35
    dy = (height - titleHeight - lineHeight * len(controls) - 5) // 2
    displayMessage('Controls', titleFont, -1, dy)

    longest = 0
    for line in controls:
        longest = max(longest, textWidth(line, textFont))
    leftMargin = ((width - longest) // 2) + 17

    dy += titleHeight
    for line in controls:
        displayMessage(line, textFont, leftMargin, dy)
        dy += lineHeight

    displayContinueMessage()

    pygame.display.update()
    waitForTheUser()


# showControls()
oof_sound = path + 'music' + os.sep + 'OOF.wav'
ding_sound = path + 'music' + os.sep + 'ding.wav'
rawr_sound = path + 'music' + os.sep + 'RAWR.wav'
flipper = False
pygame.mixer.init()
pygame.mixer.music.set_volume(1)


### Game execution ###

def currentCell():
    ''' Cell coordinates of the current position of the mouse '''
    posX, posY = pygame.mouse.get_pos()
    return (int(numpy.floor(posX / cellWidth)),
            int(numpy.floor(posY / cellHeight)))


def drawCell(x, y):
    ''' Draw cell with coordinates (x, y) in the screen '''
    global brown_radius
    brown_radius = math.sqrt(x**max(10-c1.battle, 0)+y**max(10-c1.battle, 0))
    turf = (100-min(brown_radius, 100), 100, 0)

    pygame.draw.polygon(screen, turf, poly[x, y], 0)
    if gameState[x, y] == 0:
        # turf = (100-min(10*x, 100), max(10*y, 100)-100, 0)

        # pygame.draw.polygon(screen, grey, poly[x, y], 1)
        if len(states) > 0:
            if states[-1][x, y] == 1:  # Cell just turned off, using lag
                cloudEdge = (turf[0], turf[1]-2, 0)
                pygame.draw.polygon(screen, cloudEdge, poly[x, y], 0)
                # pygame.draw.polygon(screen, grey, poly[x, y], 1)
    else:
        cloud = (turf[0], turf[1]-3, 0)
        pygame.draw.polygon(screen, cloud, poly[x, y], 0)
        # pygame.draw.polygon(screen, grey, poly[x, y], 1)


def updateScreen():
    ''' Update the screen with the current game state '''
    global gamePaused
    screen.fill(screenColor)
    for y in range(0, cellsY):
        for x in range(0, cellsX):
            drawCell(x, y)
    c1.draw_living()
    if overlay:
        c1.draw_scoreboard()
    if p1:
        p1.draw_scoreboard()
    pygame.display.update()

    if c1.transition:
        pass
        # p1.x = 0
        # p1.y = 0
        # for x in range(cellsX-1):
        #
        #     p1.x += 1
        #     # print(f"For {cellsX}, {p1.x}")
        #     p1.y += int(cellsY/cellsX)
        #     c1.draw_living()
        #     pygame.display.update()
        #     sleep(.1)
        # c1.transition = False

    sound_message()


def sound_message():
    global delay
    if p1 and p1.oof or c1.battle >= max_level:
        pygame.mixer.music.load(oof_sound)
        pygame.mixer.music.play()
        if p1:
            p1.oof = False
    for student in c1.students:
        if student.rawr:
            pygame.mixer.music.load(rawr_sound)
            pygame.mixer.music.play()
            student.rawr = False
    if (p1 and p1.hp <= 0):
        print("You Died!")
        for s in c1.students:
            s.kill()
        c1.students = []
        p = player()
        c1.students.append(p)
        c1.moving_sprites.add(p)
        q = player()
        c1.students.append(q)
        c1.moving_sprites.add(q)
        # Sound.mute()
        messagebox.showerror('You Died!', f'Score {c1.battle + p1.kills}')
        c1.battle = 0
        delay = default_delay
        focusWindow()
        p1.hp = 3
        p1.dmg = 1
        p1.armor = 0
        p1.living = True
        p1.x = cellsX - 1
        p1.y = cellsY - 1

    elif c1.battle >= max_level:
        for s in students:
            s.kill()
        c1.students = []
        c1.students.append(player())
        c1.students.append(player())
        messagebox.showerror('Game Over', f'Goblins took over the land...\nScore {c1.battle + p1.kills}')
        c1.battle = 0
        delay = default_delay
        focusWindow()
        p1.hp = 3
        p1.dmg = 1
        p1.armor = 0
        p1.living = True
        p1.x = cellsX -1
        p1.y = cellsY -1

    if (p1 and p1.ding) or c1.count_living() == 0:
        c1.battle += 1
        c1.transition = True

        if c1.battle % 2:
            delay = delay*.95

        pygame.mixer.music.load(ding_sound)
        pygame.mixer.music.play()

        p1.ding = False
        p1.x = cellsX - 1
        p1.y = cellsY - 1

        # message_window = tkinter.Toplevel(tkRoot)
        # message_window.positionfrom()
        # message_window.title("Level Passed")
        # label = tkinter.Label(message_window, text='Chose Upgrade')
        # dmg_btn = tkinter.Button(message_window, text = "+1 DMG")
        # dmg_btn.pack(side=tkinter.LEFT)
        # arm_btn = tkinter.Button(message_window, text="+1 Armor")
        # arm_btn.pack(side=tkinter.LEFT)
        # hp_btn = tkinter.Button(message_window, text="+1 Max HP")
        # hp_btn.pack(side=tkinter.RIGHT)
        # label.pack(side=tkinter.TOP)
        # tkRoot.mainloop()
        if c1.count_living() == 0:
            messagebox.showinfo('Level Passed', f'Victory!\nWon in {c1.battle} rounds')
            c1.battle = 0
            p1.armor = 0
            p1.kills = 0
            p1.dmg = 1
            reset_clouds()
            c1.init_students()
        elif c1.battle < max_level and p1.hp > 0:
            upgrade = random.choice(['Found Weapon!', 'Found Armor!', 'Recover Max HP', 'More and more Goblins\nterrorize the land...'])
            messagebox.showinfo('Level Passed', upgrade)
            if 'Found Weapon!' == upgrade:
                p1.dmg = min(p1.dmg + .25, 2)
            elif 'Found Armor!' == upgrade:
                p1.armor += 1
            elif 'Recover Max HP' == upgrade:
                p1.hp = max_hp
            elif 'More and more' in upgrade:
                c1.students.append(player())

            print(f"Upgrade: {upgrade}, arm {p1.armor}")
            upgrade = None

        focusWindow()

        for x in range(cellsX//2):
            for y in range(cellsY//2):
                gameState[x, y] = random.choice([0, 1])

        p = player()
        p.x = randint(0, cellsX // (1 + c1.battle))
        p.y = randint(0, cellsY // (1 + c1.battle))

        if c1.battle >= 4:
            p.armor = c1.battle
            p.hp = p.hp + c1.battle * 2
            p.lives = p.lives + c1.battle*2
            p.dmg = c1.battle*2
            p.color = (0, grass[1]/c1.battle, 0)

        if c1.count_living() < 16:
            c1.students.append(p)
            c1.moving_sprites.add(p)

        # new_castle = player()
        # castle.color = (0, 0, 0)
        # castle.x = 0
        # castle.y = cellsY-1
        # locations.insert(0, castle)
        # locations[1].x = cellsX-1
        # p1.x = locations[1].x
        # p1.y = locations[1].y


def liveNeighbors(x, y):
    ''' Count the number of live neighbors of cell (x, y) '''
    count = 0
    if wraparound:
        for j in range(-1, 2):
            ny = (y + j) % cellsY
            for i in range(-1, 2):
                nx = (x + i) % cellsX
                if gameState[nx, ny] == 1:
                    count += 1
    else:
        for j in range(-1, 2):
            ny = y + j
            if 0 <= ny < cellsY:
                for i in range(-1, 2):
                    nx = x + i
                    if 0 <= nx < cellsX:
                        if gameState[nx, ny] == 1:
                            count += 1
    return count - gameState[x, y]


def updateGameState(newGameState):
    ''' Save and replace current game state '''
    global states, gameState
    states.append(gameState)
    gameState = newGameState


def nextGeneration():
    ''' Set the game state to the new generation and update the screen '''
    newGameState = numpy.copy(gameState)
    reward = 0

    ''' Player decides on movement'''
    c1.observe(gameState)
    c1.act()

    ''' The field determines the quality of it's decission '''
    for y in range(0, cellsY):
        for x in range(0, cellsX):
            neighbors = liveNeighbors(x, y)

            # Any dead cell with 3 live neighbors becomes a live cell.
            if gameState[x, y] == 0 and neighbors == 3:
                newGameState[x, y] = 1

            # Any live cell with less than 2 or more than 3 live neighbors dies.
            elif gameState[x, y] == 1 and (neighbors < 2 or neighbors > 3):
                newGameState[x, y] = 0
                c1.punish_living(x, y)

            if newGameState[x, y]:
                c1.reward_living(x, y)

    if p1:
        for student in c1.students:
            if round(student.x) == round(p1.x) and round(student.y) == round(p1.y):
                # student.lives -= p1.dmg
                student.hp -= p1.dmg
                student.lives -= p1.dmg

                if student.hp > 0:
                    p1.hp -= max(student.dmg-p1.armor, 0)
                    # if student.color == student.b_color:
                        # p1.hp -= round(student.dmg)
                    p1.oof = True
                    if p1.hp <= 0:
                        # student.rawr = True
                        p1.living = False
                        c1.moving_sprites.remove(p1)
                if student.hp <= 0 and student.living:
                    student.rawr = True
                    student.living = False
                    c1.moving_sprites.remove(student)
                    p1.kills += 1
        if round(p1.x) == locations[0].x and round(p1.y) == locations[0].y:
            p1.ding = True
            # p1.hp = min(p1.hp+1, max_hp)

    updateGameState(newGameState)
    updateScreen()

    return newGameState


def toggleScreenMode():
    ''' Toggle between windowed and fullscreen mode '''
    global screen, width, height, fullscreen
    global cellWidth, cellHeight, windowHandle
    pygame.display.quit()
    pygame.display.init()
    pygame.display.set_caption(windowTitle)
    if os.path.exists(iconPath):
        icon = pygame.image.load(iconPath)
        pygame.display.set_icon(icon)
    if fullscreen:
        screen = pygame.display.set_mode(windowSize)
        width, height = windowSize
        updateWindowHandle()
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        displayInfo = pygame.display.Info()
        width = displayInfo.current_w
        height = displayInfo.current_h
    fullscreen = not fullscreen
    cellWidth = width / cellsX
    cellHeight = height / cellsY
    updateCellsBorders()
    updateScreen()


# Show initial game state
updateScreen()


def handle_user_input():
    global mouseClicked, cellValue, gamePaused, lastTime, gameState, wraparound, stepByStep, delay, states, delayInt

    pressed = pygame.key.get_pressed()
    if p1:
        if pressed[pygame.K_UP]:
            p1.action = 1
        if pressed[pygame.K_DOWN]:
            p1.action = 2
        if pressed[pygame.K_LEFT]:
            p1.action = 3
        if pressed[pygame.K_RIGHT]:
            p1.action = 4

    for event in pygame.event.get():

        # Close window when close button is pressed
        if event.type == pygame.QUIT:
            sys.exit()

        # Start changing cell states when the mouse buttons are pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouseClicked = event.button == pygame.BUTTON_LEFT \
                           or event.button == pygame.BUTTON_RIGHT
            cellX, cellY = currentCell()
            cellValue = not gameState[cellX, cellY]
            # Save current game state before dragging
            states.append(numpy.copy(gameState))

        # Stop changing cell states when the mouse buttons are released
        elif event.type == pygame.MOUSEBUTTONUP:
            mouseClicked = False

        # Keyboard input:
        elif event.type == pygame.KEYDOWN:
            # When space bar is pressed
            if event.key == pygame.K_SPACE:
                # Go to the next generation
                if stepByStep:
                    pass
                    # nextGeneration()
                # Pause/resume the game
                else:
                    gamePaused = not gamePaused
                    if not gamePaused:
                        lastTime = time()

            # Go to previous game state when backspace is pressed
            elif event.key == pygame.K_BACKSPACE:
                if len(states) > 0:
                    gameState = states.pop()
                    gamePaused = True
                    updateScreen()

            # Kill all cells when c is pressed
            elif event.key == pygame.K_c:
                newGameState = numpy.zeros((cellsX, cellsY))
                # updateGameState(newGameState)
                gamePaused = True
                updateScreen()

            # Generate random game state when r is pressed
            elif event.key == pygame.K_r:
                restart_game()

            # Activate/deactivate wraparound mode when w is pressed
            elif event.key == pygame.K_w:
                wraparound = not wraparound

            # Activate/deactivate step-by-step mode when tab is pressed
            elif event.key == pygame.K_TAB:
                stepByStep = not stepByStep

            # Accelerate game speed by pressing a
            elif event.key == pygame.K_a:
                if delayInt > 100:
                    delayInt -= 50
                elif delayInt >= 25:
                    delayInt -= 15
                elif delayInt >= 2:
                    delayInt -= 2
                delay = delayInt / 100.0

            # Deaccelerate game speed by pressing d
            elif event.key == pygame.K_d:
                if delayInt >= 100:
                    delayInt += 50
                elif delayInt >= 10:
                    delayInt += 15
                else:
                    delayInt += 2
                delay = delayInt / 100.0

            # Save game when s is pressed
            elif event.key == pygame.K_s and not fullscreen:
                filename = filedialog.asksaveasfilename(initialdir=savesDir, defaultextension='.dat')
                if filename:
                    data = (gameState, states, stepByStep, wraparound, delayInt)
                    try:
                        with open(filename, "wb") as file:
                            pickle.dump(data, file)
                        messagebox.showinfo("Game saved", "The game has been saved")
                        tkRoot.update()
                    except pickle.PicklingError:
                        print('Unpicklable object')
                focusWindow()

            # Load saved game when o is pressed
            elif event.key == pygame.K_o and not fullscreen:
                empty = len(os.listdir(savesDir)) == 0
                firstFile = None if empty else sorted(os.listdir(savesDir))[0]
                filename = filedialog.askopenfilename(initialdir=savesDir, initialfile=firstFile)
                if filename:
                    try:
                        data = ()
                        with open(filename, "rb") as file:
                            data = pickle.load(file)
                        gameState, states, stepByStep, wraparound, delayInt = data
                        gamePaused = True
                        delay = delayInt / 100
                        updateScreen()
                    except Exception:  # Too much crap to catch, I took the easy way
                        messagebox.showerror("Read error", "Save data is corrupted")
                        tkRoot.update()
                focusWindow()

            # Toggle screen mode when f is pressed
            elif event.key == pygame.K_f:
                toggleScreenMode()

            # Go to windowed mode when escape is pressed
            elif event.key == pygame.K_ESCAPE and fullscreen:
                toggleScreenMode()

            # Show game controls when h is pressed
            elif event.key == pygame.K_h:
                showControls()
                updateScreen()

            elif p1 and (pressed[pygame.K_UP]):
                p1.action = 1

            elif p1 and (pressed[pygame.K_DOWN]):
                p1.action = 2

            elif p1 and (pressed[pygame.K_LEFT]):
                p1.action = 3

            elif p1 and (pressed[pygame.K_RIGHT]):
                p1.action = 4

            if event.key == pygame.K_e:
                p1.sneak = True
                p1.speed_mod = 2
                p1.color = (0, 0, 95)
            else:
                p1.sneak = False
                p1.speed_mod = 1
                p1.color = (0, 0, 128)

    for student in c1.students:
        if student.action != 0 and student.lives >= 0:
            student.living = True

    # Handle mouse dragging
    if mouseClicked:
        x, y = currentCell()
        gameState[x, y] = cellValue
        drawCell(x, y)
        pygame.display.update()


def reset_clouds():
    global gamePaused, safety_radius
    newGameState = numpy.random.choice(a=[0, 1], size=(cellsX, cellsY))
    for x in range(int(cellsX // 2), cellsX-1):
        for y in range(int(cellsY // 2), cellsY-1):
            newGameState[x, y] = 0


def restart_game():
    reset_clouds()
    c1.trials += 1
    c1.resuscitate()
    updateGameState(newGameState)
    gamePaused = False
    updateScreen()
    c1.round = 0


discount_factor = 0.95
eps = 0.5
eps_decay_factor = 0.999
learning_rate = 0.8
choices = [0, 1, 2, 3, 4]

if p1:
    messagebox.showwarning('Goblins & Kittens', f"Get to the safehouse!\nAvoid Goblins until you're ready..")
    focusWindow()

while True:
    # Event handling:
    if isTryingToQuit():
        sys.exit()
    handle_user_input()
    before_scores = [s.score for s in c1.students]

    if not stepByStep and not gamePaused:
        if time() - lastTime > delay:
            newGameState = nextGeneration()
            if len(states) > 1:
                c1.update_model()
                c1.rebase_students()
                if len(states) % 60 == 1 and c1.count_living() < 20:
                    reset_clouds()
                    pygame.mixer.music.load(rawr_sound)
                    pygame.mixer.music.play()
                    p = player()
                    p.x = random.choice([0, 1])
                    p.y = random.choice([0, 1])
                    p.speed_mod = 2
                    c1.students.append(p)
                    c1.moving_sprites.add(p)
            lastTime = time()

    if not p1 and (len(states) >= 499 or c1.stagnation()):
        c1.report_best()
        model_json = c1.model.to_json()
        with open('gol.json', 'w') as json_file:
            json_file.write(model_json)
        c1.model.save_weights('gol.h5')
        restart_game()
        c1.reset_students()
        states.clear()
        eps *= eps_decay_factor
