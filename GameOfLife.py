import math
import random
from random import randint
from tkinter import filedialog
from tkinter import messagebox
from collections import deque
from time import time, sleep
# from sound import Sound
import pygame


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


class gakGame:
    def __init__(self):
        # Center window
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # Script's directory:
        self.path = ''
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            path = sys._MEIPASS
        else:
            path = os.path.dirname(os.path.abspath(__file__))
        path += os.sep

        pygame.init()  # Init all imported pygame modules
        iconPath = path + 'icon.png'
        self.windowTitle = 'Goblins & Kittens'
        pygame.display.set_caption(self.windowTitle)
        if os.path.exists(iconPath):
            icon = pygame.image.load(iconPath)
        pygame.display.set_icon(icon)
        # windowSize = 300, 200
        windowSize = 1080, 640
        self.res = 40
        self.max_hp = 3
        self.players = 2
        self.corner = 2
        self.width, self.height = windowSize
        self.safety_radius = 0.7
        self.screen = pygame.display.set_mode(windowSize)
        self.screenColor = white
        self.screen.fill(self.screenColor)

        # Get focus back to main window after dialogs on Windows:
        self.windowHandle = None
        self.updateWindowHandle()

        # Init dialogs:
        self.tkRoot = tkinter.Tk()  # Create Tk main window
        if os.path.exists(iconPath):
            self.tkRoot.iconphoto(True, tkinter.PhotoImage(file=iconPath))  # Set icon
        dx = (self.tkRoot.winfo_screenwidth() - self.width) // 2
        dy = (self.tkRoot.winfo_screenheight() - self.height) // 2
        self.tkRoot.geometry('{}x{}+{}+{}'.format(self.width, self.height, dx, dy))  # Center Tk window
        self.tkRoot.withdraw()  # Hide Tk main window
        self.savesDir = path + 'saves'
        if not os.path.exists(self.savesDir):
            os.makedirs(self.savesDir)

        # Cells per axis
        self.cellsX, self.cellsY = self.width // self.res, self.height // self.res

        # Dimensions of cells:
        self.cellWidth = self.width / self.cellsX
        self.cellHeight = self.height / self.cellsY

        # Create deque to store up to 1000 states
        self.states = deque(maxlen=1000)

        # Cell states: live = 1, dead = 0
        self.gameState = numpy.zeros((self.cellsX, self.cellsY), int)

        # Values to serialize:
        self.stepByStep = False
        self.wraparound = True
        # overlay = False
        self.delayInt = .1  # Speed
        self.max_level = 25

        # Other values:
        self.default_delay = 0.1
        self.delay = self.default_delay
        self.gamePaused = False
        self.mouseClicked = False
        self.fullscreen = False

        # Matrix that holds the cells borders
        self.poly = numpy.full((self.cellsX, self.cellsY), None)


        self.updateCellsBorders()

        # Patterns:

        # Flickering cross
        self.gameState[6, 6] = 1
        self.gameState[7, 6] = 1
        self.gameState[7, 7] = 1
        self.gameState[8, 6] = 1
        # Microscope:
        # gameState[19, 8] = 1
        # gameState[20, 5] = 1
        # gameState[20, 6] = 1
        # gameState[20, 8] = 1
        # gameState[21, 7] = 1
        # gameState[21, 8] = 1
        # Glider:
        self.gameState[self.cellsX - 10 + 1, 8] = 1
        self.gameState[self.cellsX - 10 + 2, 6] = 1
        self.gameState[self.cellsX - 10 + 2, 8] = 1
        self.gameState[self.cellsX - 10 + 3, 7] = 1
        self.gameState[self.cellsX - 10 + 3, 8] = 1
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

        self.circ_rad = 10

    def updateWindowHandle(self):
        if onWindows:
            self.windowHandle = win32gui.FindWindow(None, self.windowTitle)

    def focusWindow(self):
        if onWindows:
            win32gui.SetForegroundWindow(self.windowHandle)

    def updateCellsBorders(self):
        ''' Update cells borders with the current width and height for each cell '''
        for y in range(0, self.cellsY):
            for x in range(0, self.cellsX):
                # Rectangle to be drawn with upper left corner (x, y)
                self.poly[x, y] = [(x * self.cellWidth, y * self.cellHeight), \
                              ((x + 1) * self.cellWidth, y * self.cellHeight), \
                              ((x + 1) * self.cellWidth, (y + 1) * self.cellHeight), \
                              (x * self.cellWidth, (y + 1) * self.cellHeight)]

    def get_coords(self):
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

    def check_if_future_safe(self, choice, future):
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
        if choice == 4:  # Move right
            if future[y_mid][x_mid + 1]:
                return True

    def handle_user_input(self):
        cellValue = 0
        pressed = pygame.key.get_pressed()
        if self.p1:
            prev_action = self.p1.action
            if pressed[pygame.K_UP]:
                print("UP")
                self.p1.action = 1
                self.p1.acc += 0.001
            if pressed[pygame.K_DOWN]:
                self.p1.action = 2
                self.p1.acc += 0.001
            if pressed[pygame.K_LEFT]:
                self.p1.action = 3
                self.p1.acc += 0.001
            if pressed[pygame.K_RIGHT]:
                self.p1.action = 4
                self.p1.acc += 0.001
            if self.p1.action != prev_action:
                self.p1.acc = 0

        for event in pygame.event.get():

            # Close window when close button is pressed
            if event.type == pygame.QUIT:
                sys.exit()

            # Start changing cell states when the mouse buttons are pressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseClicked = event.button == pygame.BUTTON_LEFT \
                               or event.button == pygame.BUTTON_RIGHT
                self.cellX, self.cellY = self.currentCell()
                cellValue = not self.gameState[self.cellX, self.cellY]
                # Save current game state before dragging
                self.states.append(numpy.copy(self.gameState))

            # Stop changing cell states when the mouse buttons are released
            elif event.type == pygame.MOUSEBUTTONUP:
                mouseClicked = False

            # Keyboard input:
            elif event.type == pygame.KEYDOWN:
                # When space bar is pressed
                if event.key == pygame.K_SPACE:
                    # Go to the next generation
                    if self.stepByStep:
                        pass
                        # nextGeneration()
                    # Pause/resume the game
                    else:
                        self.gamePaused = not self.gamePaused
                        if not self.gamePaused:
                            lastTime = time()

                # Go to previous game state when backspace is pressed
                elif event.key == pygame.K_BACKSPACE:
                    if len(self.states) > 0:
                        self.gameState = self.states.pop()
                        self.gamePaused = True
                        self.updateScreen()

                # Kill all cells when c is pressed
                elif event.key == pygame.K_c:
                    newGameState = numpy.zeros((self.cellsX, self.cellsY))
                    # updateGameState(newGameState)
                    self.gamePaused = True
                    self.updateScreen()

                # Generate random game state when r is pressed
                elif event.key == pygame.K_r:
                    self.restart_game()

                # Activate/deactivate wraparound mode when w is pressed
                elif event.key == pygame.K_w:
                    self.wraparound = not self.wraparound

                # Activate/deactivate step-by-step mode when tab is pressed
                elif event.key == pygame.K_TAB:
                    self.stepByStep = not self.stepByStep

                # Accelerate game speed by pressing a
                elif event.key == pygame.K_a:
                    if self.delayInt > 100:
                        self.delayInt -= 50
                    elif self.delayInt >= 25:
                        self.delayInt -= 15
                    elif self.delayInt >= 2:
                        self.delayInt -= 2
                    self.delay = self.delayInt / 100.0

                # Deaccelerate game speed by pressing d
                elif event.key == pygame.K_d:
                    if self.delayInt >= 100:
                        self.delayInt += 50
                    elif self.delayInt >= 10:
                        self.delayInt += 15
                    else:
                        self.delayInt += 2
                    self.delay = self.delayInt / 100.0

                # Save game when s is pressed
                elif event.key == pygame.K_s and not self.fullscreen:
                    filename = filedialog.asksaveasfilename(initialdir=self.savesDir, defaultextension='.dat')
                    if filename:
                        data = (self.gameState, self.states, self.stepByStep, self.wraparound, self.delayInt)
                        try:
                            with open(filename, "wb") as file:
                                pickle.dump(data, file)
                            messagebox.showinfo("Game saved", "The game has been saved")
                            self.tkRoot.update()
                        except pickle.PicklingError:
                            print('Unpicklable object')
                    self.focusWindow()

                # Load saved game when o is pressed
                elif event.key == pygame.K_o and not self.fullscreen:
                    empty = len(os.listdir(self.savesDir)) == 0
                    firstFile = None if empty else sorted(os.listdir(self.savesDir))[0]
                    filename = filedialog.askopenfilename(initialdir=self.savesDir, initialfile=firstFile)
                    if filename:
                        try:
                            data = ()
                            with open(filename, "rb") as file:
                                data = pickle.load(file)
                            self.gameState, self.states, self.stepByStep, self.wraparound, self.delayInt = data
                            self.gamePaused = True
                            self.delay = self.delayInt / 100
                            self.updateScreen()
                        except Exception:  # Too much crap to catch, I took the easy way
                            messagebox.showerror("Read error", "Save data is corrupted")
                            self.tkRoot.update()
                    self.focusWindow()

                # # Toggle screen mode when f is pressed
                # elif event.key == pygame.K_f:
                #     toggleScreenMode()
                #
                # # Go to windowed mode when escape is pressed
                # elif event.key == pygame.K_ESCAPE and fullscreen:
                #     toggleScreenMode()
                #
                # # Show game controls when h is pressed
                # elif event.key == pygame.K_h:
                #     showControls()
                #     updateScreen()
                #
                elif self.p1 and (pressed[pygame.K_UP]):
                    self.p1.action = 1

                elif self.p1 and (pressed[pygame.K_DOWN]):
                    self.p1.action = 2

                elif self.p1 and (pressed[pygame.K_LEFT]):
                    self.p1.action = 3

                elif self.p1 and (pressed[pygame.K_RIGHT]):
                    self.p1.action = 4

                if event.key == pygame.K_e:
                    self.p1.sneak = True
                    self.p1.speed_mod = 2
                    self.p1.color = (0, 0, 95)
                else:
                    self.p1.sneak = False
                    self.p1.speed_mod = 1
                    self.p1.color = (0, 0, 128)

        for student in self.c1.students:
            if student.action != 0 and student.lives >= 0:
                student.living = True

        # Handle mouse dragging
        if self.mouseClicked:
            x, y = self.currentCell()
            self.gameState[x, y] = cellValue
            self.drawCell(x, y)
            pygame.display.update()

    def reset_clouds(self):
        self.newGameState = numpy.random.choice(a=[0, 1], size=(self.cellsX, self.cellsY))
        for x in range(int(self.cellsX // 2), self.cellsX-1):
            for y in range(int(self.cellsY // 2), self.cellsY-1):
                self.newGameState[x, y] = 0


    def restart_game(self):
        self.reset_clouds()
        self.c1.trials += 1
        self.c1.resuscitate()
        self.updateGameState(self.newGameState)
        self.gamePaused = False
        self.updateScreen()
        self.c1.round = 0

    # Define landscape
    def setup_game(self):
        self.locations = []
        castle = player()
        castle.set_castle()
        self.locations.append(castle)
        self.c1 = classroom()
        self.p1 = None
        overlay = False
        self.p1 = player()
        self.p1.set_human()
        # p1.hp = 100000
        self.p1.x = self.cellsX - self.p1.rWall - 1
        self.p1.y = self.cellsY - self.p1.dWall - 1
        self.p1.human = True
        self.p1.color = (0, 0, 128)
        self.c1.moving_sprites.add(self.p1)
        c = player()
        c.set_cat()
        self.c1.cats.append(c)
        self.c1.moving_sprites.add(c)
        self.c1.moving_sprites.add(castle)

        # Overlay, add
        self.screenOverlay = player()
        self.screenOverlay.set_overlay()
        self.c1.moving_sprites.add(self.screenOverlay)
        # self.updateWindowHandle()

    ### Welcome screen and game controls ###

    def textWidth(self, text, font):
        ''' Size in pixels of the given text '''
        textSurf = font.render(text, True, black)
        return textSurf.get_rect().width

    def displayMessage(self, text, font, dx, dy):
        ''' Show a message starting at (dx, dy). If dx=-1 then the message
        will be centered horizontally. '''
        textSurf = font.render(text, True, black)
        textRect = textSurf.get_rect()
        if dx == -1:
            textRect.centerx = self.width / 2
            textRect.top = dy
        else:
            textRect.left = dx
            textRect.top = dy
        self.screen.blit(textSurf, textRect)

    def isTryingToQuit(self):
        ''' Determine whether the user is trying to quit the game with Alt + F4 '''
        pressed_keys = pygame.key.get_pressed()
        alt = pressed_keys[pygame.K_LALT] or \
              pressed_keys[pygame.K_RALT]
        f4 = pressed_keys[pygame.K_F4]
        return alt and f4

    def waitForTheUser(self):
        ''' Wait for the user to press any key to continue '''
        while True:
            if self.isTryingToQuit():
                sys.exit()
            for event in pygame.event.get():
                # Close window when close button is pressed
                if event.type == pygame.QUIT:
                    sys.exit()
                # Go to the next screen when any key is pressed
                elif event.type == pygame.KEYDOWN:
                    return

    def displayContinueMessage(self):
        continueDx = self.width - continueTextWidth - 3
        continueDy = self.height - 21
        self.displayMessage(continueText, continueFont, continueDx, continueDy)

    def showControls(self):
        ''' Show game controls screen '''

        # Clean screen to avoid superposition wih previous state
        self.screen.fill(self.screenColor)

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
        dy = (self.height - titleHeight - lineHeight * len(controls) - 5) // 2
        self.displayMessage('Controls', titleFont, -1, dy)

        longest = 0
        for line in controls:
            longest = max(longest, self.textWidth(line, textFont))
        leftMargin = ((self.width - longest) // 2) + 17

        dy += titleHeight
        for line in controls:
            self.displayMessage(line, textFont, leftMargin, dy)
            dy += lineHeight

        self.displayContinueMessage()

        pygame.display.update()
        self.waitForTheUser()

    def currentCell(self):
        ''' Cell coordinates of the current position of the mouse '''
        posX, posY = pygame.mouse.get_pos()
        return (int(numpy.floor(posX / self.cellWidth)),
                int(numpy.floor(posY / self.cellHeight)))

    def drawCell(self, x, y):
        ''' Draw cell with coordinates (x, y) in the screen '''
        brown_radius = math.sqrt(x ** max(5 - self.c1.battle, 0) + y ** max(5 - self.c1.battle, 0))
        turf = (100 - min(brown_radius, 100), 100, 0)

        pygame.draw.polygon(self.screen, turf, self.poly[x, y], 0)
        if gg.gameState[x, y] == 0:
            # turf = (100-min(10*x, 100), max(10*y, 100)-100, 0)

            # pygame.draw.polygon(screen, grey, poly[x, y], 1)
            if len(gg.states) > 0:
                if gg.states[-1][x, y] == 1:  # Cell just turned off, using lag
                    cloudEdge = (turf[0], turf[1] - 2, 0)
                    pygame.draw.polygon(self.screen, cloudEdge, self.poly[x, y], 0)
                    # pygame.draw.polygon(screen, grey, poly[x, y], 1)
        else:
            cloud = (turf[0], turf[1] - 3, 0)
            pygame.draw.polygon(self.screen, cloud, self.poly[x, y], 0)
            # pygame.draw.polygon(screen, grey, poly[x, y], 1)

    def updateScreen(self):
        ''' Update the screen with the current game state '''
        self.screen.fill(self.screenColor)
        for y in range(0, self.cellsY):
            for x in range(0, self.cellsX):
                self.drawCell(x, y)
        self.c1.draw_living()
        # if overlay:
        #     c1.draw_scoreboard()
        if self.p1:
            self.p1.draw_scoreboard()
        pygame.display.update()

        if self.c1.transition:
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

        self.sound_message()

    def sound_message(self):
        if self.p1 and self.p1.oof or self.c1.battle >= self.max_level:
            pygame.mixer.music.load(oof_sound)
            pygame.mixer.music.play()
            if self.p1:
                self.p1.oof = False
        for student in self.c1.students:
            if student.rawr:
                pygame.mixer.music.load(rawr_sound)
                pygame.mixer.music.play()
                student.rawr = False
                if student.piece_ss == GoblinSS:
                    student.timer = len(gg.states)
                    student.piece_ss = GoblinSwingSS
        for cat in self.c1.cats:
            if cat.meow:
                pygame.mixer.music.load(meow_sound)
                pygame.mixer.music.play()
                cat.meow = False

        if (self.p1 and self.p1.hp <= 0):
            print("You Died!")
            for s in self.c1.students:
                s.kill()
            for c in self.c1.cats:
                c.kill()
            self.c1.students = []
            self.c1.cats = []
            q1 = player()
            self.c1.students.append(q1)
            self.c1.moving_sprites.add(q1)
            q2 = player()
            self.c1.students.append(q2)
            self.c1.moving_sprites.add(q2)
            c = player()
            c.set_cat()
            self.c1.cats.append(c)
            self.c1.moving_sprites.add(c)

            messagebox.showerror('You Died!',
                                 f'{self.c1.battle} Rounds\n{self.p1.saves} Kittens Saved\n{self.p1.kills} Goblin Kills\n{round(self.p1.armor, 2)} Armour\n+{round(self.p1.dmg * 100 - 100)}% Damage')
            self.c1.battle = 0
            self.delay = self.default_delay
            self.focusWindow()
            self.p1.hp = 3
            self.p1.dmg = 1
            self.p1.armor = 0
            self.p1.kills = 0
            self.p1.saves = 0
            self.p1.living = True
            self.p1.x = self.cellsX - self.p1.rWall - 1
            self.p1.y = self.cellsY - self.p1.dWall - 1
            for cat in self.c1.cats:
                cat.scooped = False
                cat.position_cat()

        elif self.c1.battle >= self.max_level:
            # self.setup_game()
            for s in self.c1.students:
                s.kill()
            for k in self.c1.cats:
                k.kill()
            self.c1.cats = []
            self.c1.students = []
            p = player()
            self.c1.students.append(p)
            self.c1.moving_sprites.add(p)
            q = player()
            self.c1.students.append(q)
            self.c1.moving_sprites.add(q)
            messagebox.showerror(f'Level {self.c1.battle} Passed',
                                 f'Goblins took over the land...\n{self.p1.saves} Kittens Saved\n{self.p1.kills} Goblin Kills\n{round(self.p1.armor, 2)} Armour\n+{round(self.p1.dmg * 100 - 100)}% Damage')
            self.c1.battle = 0
            self.delay = self.default_delay
            self.focusWindow()
            self.p1.hp = 3
            self.p1.dmg = 1
            self.p1.armor = 0
            self.p1.saves = 0
            self.p1.kills = 0
            self.p1.living = True
            self.p1.x = self.cellsX - self.p1.rWall - 1
            self.p1.y = self.cellsY - self.p1.dWall - 1

        elif (self.p1 and self.p1.ding) or self.c1.count_living() == 0:
            self.c1.battle += 1

            self.c1.transition = True

            if self.c1.battle % 2:
                self.delay = self.delay * .95

            pygame.mixer.music.load(ding_sound)
            pygame.mixer.music.play()

            self.p1.ding = False
            self.p1.x = self.cellsX - self.p1.rWall - 1
            self.p1.y = self.cellsY - self.p1.dWall - 1

            if self.c1.count_living() == 0:
                messagebox.showinfo('Level Passed', f'Victory!\nWon in {self.c1.battle} rounds')
                self.c1.battle = 0
                self.p1.armor = 0
                self.p1.kills = 0
                self.p1.saves = 0
                self.p1.dmg = 1
                self.reset_clouds()
                self.c1.init_students()
            # SALL GOOD MAN
            elif self.c1.battle < self.max_level and self.p1.hp > 0:
                if self.c1.count_scooped() == len(self.c1.cats):
                    upgrade = random.choice(['Found Weapon!', 'Found Armor!', 'Recover Max HP',
                                             'More and more Goblins\nterrorize the land...'])
                    messagebox.showinfo(f'Level {self.c1.battle} Passed', upgrade)
                    if 'Found Weapon!' == upgrade:
                        self.p1.dmg = min(self.p1.dmg + .25, 2)
                    elif 'Found Armor!' == upgrade:
                        self.p1.armor += 1
                    elif 'Recover Max HP' == upgrade:
                        self.p1.hp = self.max_hp
                    elif 'More and more' in upgrade:
                        p = player()
                        p.drawPlayer()
                        self.c1.students.append(p)
                        self.c1.moving_sprites.add(p)
                    upgrade = None
                elif self.c1.battle > 0:
                    messagebox.showinfo(f'Level {self.c1.battle} Passed', "Some cats were abandoned along the way...")

            for cat in self.c1.cats:
                cat.scooped = False
                cat.position_cat()
            self.focusWindow()

            for x in range(self.cellsX // 2):
                for y in range(self.cellsY // 2):
                    self.gameState[x, y] = random.choice([0, 1])

            # A Cat or high level enemy
            p = player()

            if self.c1.battle >= 4:
                p.x = randint(self.cellsX // 2, self.cellsX - p.rWall - 1)
                p.y = randint(self.cellsY // 2, self.cellsY - p.lWall - 1)
                p.piece_ss = EvilHeadSS
                if self.c1.battle > self.max_level - 20:
                    p.piece_ss = RottingSkullSS
                if self.c1.battle > self.max_level - 15:
                    p.piece_ss = WhiteSkullSS
                if self.c1.battle > self.max_level - 10:
                    p.piece_ss = MosquitoSS

                p.armor = self.c1.battle
                p.hp = p.hp + self.c1.battle * 2
                p.lives = p.lives + self.c1.battle * 2
                p.dmg = self.c1.battle * 2
                p.color = (0, grass[1] / self.c1.battle, 0)
                self.c1.students.append(p)
                self.c1.moving_sprites.add(p)

            else:
                p.set_cat()
                p.position_cat()
                p.cart_pose = self.c1.battle
                self.c1.cats.append(p)
                self.c1.moving_sprites.add(p)

    def liveNeighbors(self, x, y):
        ''' Count the number of live neighbors of cell (x, y) '''
        count = 0
        if self.wraparound:
            for j in range(-1, 2):
                ny = (y + j) % self.cellsY
                for i in range(-1, 2):
                    nx = (x + i) % self.cellsX
                    if self.gameState[nx, ny] == 1:
                        count += 1
        else:
            for j in range(-1, 2):
                ny = y + j
                if 0 <= ny < self.cellsY:
                    for i in range(-1, 2):
                        nx = x + i
                        if 0 <= nx < self.cellsX:
                            if self.gameState[nx, ny] == 1:
                                count += 1
        return count - self.gameState[x, y]

    def updateGameState(self, newGameState):
        ''' Save and replace current game state '''
        self.states.append(self.gameState)
        self.gameState = newGameState

    def nextGeneration(self):
        ''' Set the game state to the new generation and update the screen '''
        newGameState = numpy.copy(self.gameState)
        reward = 0

        ''' Player decides on movement'''
        self.c1.observe(self.gameState)
        self.c1.act()

        ''' The field determines the quality of it's decission '''
        for y in range(0, self.cellsY):
            for x in range(0, self.cellsX):
                neighbors = self.liveNeighbors(x, y)

                # Any dead cell with 3 live neighbors becomes a live cell.
                if self.gameState[x, y] == 0 and neighbors == 3:
                    newGameState[x, y] = 1

                # Any live cell with less than 2 or more than 3 live neighbors dies.
                elif self.gameState[x, y] == 1 and (neighbors < 2 or neighbors > 3):
                    newGameState[x, y] = 0
                    self.c1.punish_living(x, y)

                if newGameState[x, y]:
                    self.c1.reward_living(x, y)

        if self.p1:
            for student in self.c1.students:
                if round(student.x) == round(self.p1.x) and round(student.y) == round(self.p1.y):
                    # student.lives -= p1.dmg
                    student.hp -= self.p1.dmg
                    student.lives -= self.p1.dmg
                    if student.piece_ss == GoblinSS:
                        student.timer = len(self.states)
                        student.piece_ss = GoblinSwingSS

                    if student.hp > 0:
                        self.p1.hp -= max(student.dmg - self.p1.armor, 0)
                        # if student.color == student.b_color:
                        # p1.hp -= round(student.dmg)
                        self.p1.oof = True
                        if self.p1.hp <= 0:
                            # student.rawr = True
                            self.p1.living = False
                    if student.hp <= 0 and student.living:
                        student.rawr = True
                        student.living = False
                        student.piece_ss = GoblinDieSS
                        self.p1.kills += 1
            if round(self.p1.x) <= self.locations[0].x + self.corner and round(self.p1.y) <= self.locations[0].y + self.corner:
                self.p1.ding = True
                for student in self.c1.students:
                    if student.piece_ss == GoblinDieSS:
                        student.kill()

            for cat in self.c1.cats:
                if cat.x == round(self.p1.x) and cat.y == round(self.p1.y):
                    # pygame.mixer.music.load(meow_sound)
                    # pygame.mixer.music.play()
                    cat.meow = True
                    if not cat.cart_pose:
                        cat.cart_pose = randint(3, 5)
                    cat.scooped = self.p1
                    self.p1.saves += 1
                if cat.x <= self.locations[0].x + self.corner and cat.y <= self.locations[0].y + self.corner:
                    # if not cat.pur:
                    #     cat.scooped = False
                    #     cat.meow = True
                    #     cat.pur = True
                    # else:
                    #     cat.x = locations[0].x
                    #     cat.y = locations[0].y
                    cat.scooped = False
                if cat.scooped:
                    cat.x = cat.scooped.x
                    cat.y = cat.scooped.y - .7
                    cat.cat_row = 6
                    # cat.current_sprite = cat.cart_pose
                # p1.hp = min(p1.hp+1, max_hp)

        self.updateGameState(newGameState)
        self.updateScreen()

        return newGameState

    def run(self):
        lastTime = 0.0
        self.discount_factor = 0.95
        self.eps = 0.5
        self.eps_decay_factor = 0.999
        self.learning_rate = 0.8
        self.choices = [0, 1, 2, 3, 4]

        if self.p1:
            # messagebox.showwarning('Goblins & Kittens', f"Rescue the Kittens!\nAvoid Goblins until you're ready..")
            self.focusWindow()

        while True:
            # Event handling:
            if self.isTryingToQuit():
                sys.exit()
            self.handle_user_input()
            before_scores = [s.score for s in self.c1.students]

            if not self.stepByStep and not self.gamePaused:
                if time() - lastTime > self.delay:
                    self.newGameState = self.nextGeneration()
                    if len(self.states) > 1:
                        self.c1.update_model()
                        self.c1.rebase_students()
                        if len(self.states) % 60 == 1 and self.c1.count_living() < 10:
                            self.reset_clouds()
                            pygame.mixer.music.load(rawr_sound)
                            pygame.mixer.music.play()
                            p = player()
                            p.x = randint(self.cellsX // 3, self.cellsX//2)
                            p.y = randint(self.cellsY // 3, self.cellsY//2)
                            p.speed_mod = 2
                            self.c1.students.append(p)
                            self.c1.moving_sprites.add(p)
                    lastTime = time()
                    # self.updateScreen()

            if not self.p1 and (len(self.states) >= 499 or self.c1.stagnation()):
                self.c1.report_best()
                model_json = self.c1.model.to_json()
                with open('gol.json', 'w') as json_file:
                    json_file.write(model_json)
                self.c1.model.save_weights('gol.h5')
                self.restart_game()
                self.c1.reset_students()
                self.states.clear()
                self.eps *= self.eps_decay_factor


class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey = None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert(24)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

gg = gakGame()

mosquito_filename = 'sprites/Mosquito/Mosquito Flying Pose.png'
MosquitoSS = SpriteSheet(mosquito_filename)

goblin_filename = 'sprites/Goblin/$Goblin.png'
GoblinSS = SpriteSheet(goblin_filename)

goblin_swing_filename = 'sprites/Goblin/Goblin Stab 2.png'
GoblinSwingSS = SpriteSheet(goblin_swing_filename)

goblin_die_filename = 'sprites/Goblin/Goblin Dying Pose.png'
GoblinDieSS = SpriteSheet(goblin_die_filename)

evil_head_filename = 'sprites/Evil Head/Evil Head Biting.png'
EvilHeadSS = SpriteSheet(evil_head_filename)

rotting_skull_file = 'sprites/Evil Skull/Skull Rotten Biting.png'
RottingSkullSS = SpriteSheet(rotting_skull_file)

white_skull_file = 'sprites/Evil Skull/Skull Biting.png'
WhiteSkullSS = SpriteSheet(white_skull_file)

cart_filename = 'sprites/CART_2.png'
CartSS = SpriteSheet(cart_filename)

black_cat_filename = 'sprites/Cats/Black.png'
catBlackSS = SpriteSheet(black_cat_filename)

orange_cat_filename = 'sprites/Cats/Orange.png'
catOrangeSS = SpriteSheet(orange_cat_filename)

yellow_cat_filename = 'sprites/Cats/Yellow.png'
catYellowSS = SpriteSheet(yellow_cat_filename)

window_filename = 'sprites/BG112A_W.png'
windowSS = SpriteSheet(window_filename)


class classroom:
    def __init__(self):
        self.moving_sprites = pygame.sprite.Group()
        self.students = []
        self.cats = []
        self.init_students()
        self.reporter = player()
        self.ticker = []
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

        self.r = (gg.height // gg.res) // 2
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

    def count_scooped(self):
        cart_cats = 0
        for cat in self.cats:
            if cat.scooped != False:
                cart_cats += 1
        return cart_cats

    def safe_cats(self):
        house_cats = 0
        for cat in self.cats:
            if round(cat.x) <= gg.locations[0].x + gg.corner and round(cat.y) <= gg.locations[0].y + gg.corner:
                house_cats += 1
        return house_cats

    def cats_all_home(self):
        house_cats = 0
        for cat in self.cats:
            if round(cat.x) <= gg.locations[0].x + gg.corner and round(cat.y) <= gg.locations[0].y + gg.corner:
                house_cats += 1
        if house_cats == len(self.cats):
            return True
        else:
            return False

    def init_students(self):
        for s in self.students:
            s.kill()
        self.students = []
        for _ in range(gg.players):
            p = player()
            p.x = randint(gg.cellsX // 4, gg.cellsX * 3 // 4)
            p.y = randint(gg.cellsX // 4, 3 * gg.cellsY // 4)
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
            if (not gg.p1 and max_living_score > 29):
                pygame.mixer.music.load(ding_sound)
                pygame.mixer.music.play()
                # if p1.x == locations[0].x and p1.y == locations[0].y:
                if gg.p1:
                    gg.p1.x = gg.cellsX - gg.p1.rWall -1
                    gg.p1.y = gg.cellsY - gg.p1.dWall -1
            elif (gg.p1 and not gg.p1.living) or (gg.p1 and max_living_score > 29):
                pygame.mixer.music.load(oof_sound)
                pygame.mixer.music.play()

                sleep(5)

        return {'winner': winner, 'max_score': max_score}

    def draw_scoreboard(self):
        font = pygame.font.Font('freesansbold.ttf', 22)
        self.best = gg.c1.report_best(verbose=False)

        for i, student in enumerate(self.students):
            line = f"P{i + 1} {'I' * student.lives} {student.score}"
            if student.score == self.best['max_score'] and self.best['max_score'] >= 30:
                line += " *"
            if student.gold:
                text = font.render(line, True, (255, 255, 0), grey)
            else:
                text = font.render(line, True, student.color, grey)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.y += i * 22 + 12
            gg.screen.blit(text, textRect)

        report_line = f"Round {self.battle}.{self.trials}.{self.round}"
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(report_line, True, darkgrey, grey)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.y += 0
        gg.screen.blit(text, textRect)

        for i, num in enumerate(self.ticker):
            ticker_line = f"{num}"
            font = pygame.font.Font('freesansbold.ttf', 10)
            text = font.render(ticker_line, True, darkgrey, grey)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.y += gg.height - gg.res // 2
            textRect.x += i * gg.res
            gg.screen.blit(text, textRect)

    def draw_living(self):

        if not gg.p1:
            for student in self.students:
                if student.color == student.b_color and not student.gold:
                    student.drawPlayer()
            for student in self.students:
                if student.color == student.a_color and not student.gold:
                    student.drawPlayer()
            for student in self.students:
                if student.gold:
                    student.drawPlayer()

        if gg.p1:
            for student in self.students:
                # if student.hp > 0:
                student.drawPlayer()

            if gg.p1.living:
                gg.p1.drawPlayer()

            for c in self.cats:
                c.drawPlayer()

            if len(gg.locations) > 0:
                for loc in gg.locations:
                    loc.drawPlayer()

            gg.screenOverlay.drawPlayer()

            self.moving_sprites.draw(gg.screen)
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
        if not still_alive or max_score >= 30 or (gg.p1 and round(gg.p1.x) <= gg.locations[0].x + gg.corner and round(gg.p1.y) <= gg.locations[0].y + gg.corner):
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
                gg.c1.model.fit(observations, tvs, epochs=1, verbose=0)
                self.observations = []
                self.tvs = []

    def rebase_students(self):
        b_score = 0
        if gg.p1:
            gg.p1.action = 0
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
        if gg.p1 and gg.p1.living:
            gg.p1.move_on_prediction(gg.p1.action)

    def reward_living(self, x, y):
        self.best = gg.c1.report_best(verbose=False)
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
                prediction = gg.c1.model.predict(student.observation)[0]
                target = student.reward + gg.discount_factor * np.max(prediction)
                target_vector = prediction
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
            student.x = random.randint(0, int(gg.cellsX * ((1 + self.battle) / (2 + self.battle))))
            student.y = random.randint(0, int(gg.cellsY * ((1 + self.battle) / (2 + self.battle))))
        self.resuscitate()

    def stagnation(self):
        min_stagnation = self.get_min_stag()
        best = self.report_best(verbose=False)


        if not gg.p1:
            if len(gg.states) % 30 == 1:
                gg.gameState = numpy.random.choice(a=[0, 1], size=(gg.cellsX, gg.cellsY))
                for x in range(int(gg.cellsX // 2), gg.cellsX - 1):
                    for y in range(int(gg.cellsY // 2), gg.cellsY - 1):
                        gg.gameState[x, y] = 0

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

            if gg.gameState.sum() == 0:
                print(f"No cloud cover...")
                gameState = numpy.random.choice(a=[0, 1], size=(gg.cellsX, gg.cellsY))
                for x in range(int(gg.cellsX // 2), gg.cellsX - 1):
                    for y in range(int(gg.cellsY // 2), gg.cellsY - 1):
                        gameState[x, y] = 0
                return True

        if gg.p1 and round(gg.p1.x) <= gg.locations[0].x + gg.corner and round(gg.p1.y) <= gg.locations[0].y + gg.corner:
            print("Player found the Castle!!!")
            return True

        if gg.p1 and gg.p1.hp == 0:
            gg.p1.hp = 3
            gg.p1.lives = 3
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
            self.x = 2 * gg.cellsX // 3
            self.y = 2 * gg.cellsY // 3
        else:
            a = randint(0, 128)
            self.a_color = tuple([a, 128, 128 - a])
            # self.a_color = tuple([a, 255-a, randint(0, 255)])
            # self.b_color = tuple([128, max(self.a_color[1]*2, 255), 255-self.a_color[2]])
            self.b_color = (0, grass[1]/2, 0)
            self.color = self.a_color
            self.x = gg.cellsX // 2
            self.y = gg.cellsY // 2
        self.saves = 0
        self.team = None
        self.lives = 3
        self.hp = 3
        self.dmg = 1
        self.acc = 1
        self.score = 0
        self.reward = 0
        self.kills = 0
        self.armor = 0
        self.speed_mod = 1
        self.current_sprite = 0
        self.sprites = []
        self.set_goblin()
        self.uWall = 3
        self.dWall = 4
        self.lWall = 5
        self.rWall = 5
        self.gold = False
        self.sneak = False
        self.oof = False
        self.rawr = False
        self.pur = False
        self.cart_pose = None
        self.goblin_row = 0
        self.ding = False
        self.meow = False
        self.scooped = False
        self.deaths = 0
        self.stagnation = 0
        self.action = 0
        self.living = True
        self.observation = None
        self.cat = False
        self.human = False
        self.castle = False
        # self.image = None
        # self.rect = None

    def set_goblin(self):
        self.human = False
        # self.sprites.append(pygame.image.load("sprites/Goblin/R0Goblin Dying Pose.png"))
        # self.sprites.append(pygame.image.load("sprites/Goblin/R1Goblin Dying Pose.png"))
        # self.filename = 'sprites/Goblin/$Goblin.png'
        self.piece_ss = GoblinSS

    def set_human(self):
        self.human = True
        self.piece_ss = CartSS
        # self.sprites = []
        # self.sprites.append(pygame.image.load("sprites/DL1CART.png"))

    def set_overlay(self):
        # self.y = 11
        # self.x = 27
        self.x = 13
        self.y = 5.5
        self.piece_ss = windowSS

    def position_cat(self):
        self.cat_row = randint(0, 5)
        self.x = gg.cellsX//2+randint(-3, 4)
        self.y = gg.cellsY//2+randint(-2, 3)

    def set_cat(self):
        self.human = False
        self.cat = True
        # self.sprites = []
        self.color = random.choice(['Orange', 'Black', 'Yellow'])
        if self.color == 'Black':
            self.piece_ss = catBlackSS
            self.cat_row = randint(0,5)
        elif self.color == 'Orange':
            self.piece_ss = catOrangeSS
            self.cat_row = randint(0,5)
        elif self.color == 'Yellow':
            self.piece_ss = catYellowSS
            self.cat_row = randint(0,5)

        # self.sprites.append(pygame.image.load(f"sprites/cats/Idle0{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/Idle1{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/Idle2{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/Idle3{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/Crouch0{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/loaf0{self.color}.png"))
        # self.sprites.append(pygame.image.load(f"sprites/cats/loaf1{self.color}.png"))

    def set_castle(self):
        self.human = False
        self.castle = True
        self.color = (0, 0, 0)
        self.x = self.lWall
        self.y = self.uWall
        self.sprites.append(pygame.image.load(f"sprites/castle.png"))
        self.sprites.append(pygame.image.load(f"sprites/castle.png"))

    def drawPlayer(self):
        ''' Draw player's cell with coordinates (x, y) '''

        if self.color == (0, 0, 0):
            # pass

            pygame.draw.rect(gg.screen, black, pygame.Rect(0, 0, gg.res, gg.res))
            pygame.draw.rect(gg.screen, (165, 42, 42), pygame.Rect(gg.res/3+1, gg.res/2,gg. res/3+1, gg.res/2))
            #
            if gg.c1.battle > 0:
                pygame.draw.rect(gg.screen, black, pygame.Rect(gg.res*(gg.cellsX-1), gg.res*(gg.cellsY-1), gg.res, gg.res))
                pygame.draw.rect(gg.screen, (165, 42, 42), pygame.Rect((gg.cellsX-1)*gg.res-1+gg.res/3+2, gg.res*(gg.cellsY-1)+gg.res/2, gg.res/3+1, gg.res/2))

        else:
            if self.armor > 0 and not self.human:
                pass
                # pygame.draw.circle(screen, self.color, [res * self.x + circ_rad, res * self.y + circ_rad], circ_rad)

        self.current_sprite += 1
        # self.image = self.sprites[0]
        # if self.cat:
        #     self.current_sprite = min(self.current_sprite, len(self.sprites)-1)

        if self.cat:
            self.image = self.piece_ss.image_at((self.current_sprite*32%128, 32*self.cat_row, 32, 32), colorkey=(0,0,0))
            # self.image = self.sprites[int((self.current_sprite//(len(self.sprites)-1)) % (len(self.sprites)-1))]
            if self.scooped:
                self.cart_row = 5
                # print(self.cart_pose)
                # self.image = self.sprites[(self.cart_pose+3)%len(self.sprites)]
            if self.pur:
                self.cat_row = 6
                # self.image = self.sprites[int((self.current_sprite//(len(self.sprites)-1)) % (len(self.sprites)+3))]
        elif self.castle:
            self.image = self.sprites[0]
        elif self.piece_ss == CartSS:
            if self.action in [3, 4]:
                self.image = self.piece_ss.image_at((124, 0, 172-124, 48), colorkey=(147,168,222))
            elif self.action in [1, 2]:
                self.image = self.piece_ss.image_at((0, 0, 33, 48), colorkey=(147,168,222))
            else:
                self.image = self.piece_ss.image_at((78, 0, 124-78, 48), colorkey=(147,168,222))
            # self.image = self.sprites[int((self.current_sprite//len(self.sprites)) % len(self.sprites))]
        elif self.piece_ss == windowSS:
            self.image = self.piece_ss.image_at((0, 0, 1920, 1080), colorkey=(255, 255, 255))
        else:
            # Goblins
            if self.piece_ss == GoblinSwingSS:
                self.image = self.piece_ss.image_at((self.current_sprite*84%252, 10, 82, 72), colorkey=(0,0,0))
                if self.timer + 2 < len(gg.states):
                    self.piece_ss = GoblinSS
            elif self.piece_ss == GoblinDieSS:
                # self.current_sprite = 0
                self.current_sprite = min(self.current_sprite*121, 121*4)
                self.image = self.piece_ss.image_at((self.current_sprite*121%605, 10, 121, 80), colorkey=(0,0,0))
            elif self.piece_ss == EvilHeadSS:
                self.image = self.piece_ss.image_at((self.current_sprite*118%354, 20, 118, 116), colorkey=(0,0,0))
            elif self.piece_ss == RottingSkullSS or self.piece_ss == WhiteSkullSS:
                self.image = self.piece_ss.image_at((self.current_sprite*92%460, 20, 92, 95), colorkey=(0,0,0))
            elif self.piece_ss == MosquitoSS:
                self.image = self.piece_ss.image_at((self.current_sprite*94%188, 20, 94, 89), colorkey=(0,0,0))
            else:
                # Else idle Goblin
                self.image = self.piece_ss.image_at((self.current_sprite*48%144, self.goblin_row*64%256, 36, 60), colorkey=(0,0,0))

        self.size = self.image.get_size()

        const = 2
        if self.cat:
            self.image = pygame.transform.scale(self.image, (int(const*self.size[0]), int(const*self.size[1])))
        elif self.castle:
            self.image = pygame.transform.scale(self.image, (int(const*self.size[0]), int(const*self.size[1])))
        elif self.human:
            self.image = pygame.transform.scale(self.image, (int(self.size[0]), int(self.size[1])))
        elif self.piece_ss == windowSS:
            self.image = pygame.transform.scale(self.image, (int(self.size[0] / .4), int(self.size[1] / .4)))
        else: # Goblins
            self.image = pygame.transform.scale(self.image, (int(self.size[0]), int(self.size[1])))
        self.rect = self.image.get_rect()
        self.rect.center = [int(self.x*gg.res)+gg.res//2, self.y*gg.res+gg.res//2]


            # self.students[0].current_sprite += 1
            # self.moving_sprites.image = self.students[0].sprites[self.students[0].current_sprite%len(self.students[0].sprites)]

        # if self.reward < 0 and gg.overlay:
        #     pygame.draw.circle(gg.screen, red, [gg.res * self.x + gg.circ_rad, gg.res * self.y + gg.circ_rad], gg.circ_rad * .5)
        # if self.reward > 0 and gg.overlay:
        #     pygame.draw.rect(gg.screen, white,
        #                      pygame.Rect(gg.res * self.x + gg.circ_rad - 1, gg.res * self.y, gg.circ_rad * .25, gg.circ_rad * 2))
        #     pygame.draw.rect(gg.screen, white,
        #                      pygame.Rect(gg.res * self.x, gg.res * self.y + gg.circ_rad - 1, gg.circ_rad * 2, gg.circ_rad * 0.25))
        if self.lives <= 0 and self.color == self.a_color:
            self.color = self.b_color
            self.dmg = 2
            self.speed_mod = 2
            self.rawr = True
            self.lives = -1
        # if self.gold and gg.overlay:
        #     pygame.draw.rect(gg.screen, (255, 255, 0),
        #                      pygame.Rect(gg.res * self.x + gg.circ_rad // 2, gg.res * self.y - 1, gg.circ_rad, gg.circ_rad // 2))

    def draw_scoreboard(self):
        brown_radius = math.sqrt(gg.width ** max(5 - gg.c1.battle, 0) + gg.height ** max(5 - gg.c1.battle, 0))

        turf = (100 - min(brown_radius, 100), 100, 0)
        font = pygame.font.Font('freesansbold.ttf', 22)
        line = f"Level {gg.c1.battle}"
        text = font.render(line, True, gg.p1.color, turf)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.x += gg.width * 3 // 4 - 12
        textRect.y += 0
        # screen.blit(text, textRect)

        line = f"Lives {'l' * self.hp}"
        text = font.render(line, True, gg.p1.color, turf)
        text.set_alpha(200)
        textRect = text.get_rect()
        textRect.x += gg.width * 3 // 4 - 12
        textRect.y += gg.res
        # screen.blit(text, textRect)

        font = pygame.font.Font('freesansbold.ttf', 12)
        percent = round((float(self.dmg)-1)*100)
        if percent > 0:
            # print(f"DMG {percent} with damage {self.dmg}")
            line = f"+{percent}% DMG"
            text = font.render(line, True, gg.p1.color, turf)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.x += gg.width * 3 // 4 - 12
            textRect.y += gg.res*2 + gg.res*2//3
            # screen.blit(text, textRect)
        if self.armor > 0:
            if self.armor == 1:
                line = f"Light Armor"
            elif self.armor >= 2:
                line = f"Heavy Armor"
                self.armor = 2

            text = font.render(line, True, gg.p1.color, turf)
            text.set_alpha(200)
            textRect = text.get_rect()
            textRect.x += gg.width * 3 // 4 - 12
            textRect.y += gg.res * 2
            # screen.blit(text, textRect)

    def get_observable(self, state):
        if gg.p1:
            state[round(gg.p1.x), round(gg.p1.y)] = 1
        arr = [-1] * gg.c1.n
        map = []
        i = 0
        for row in range(round(self.y) - gg.c1.r, round(self.y) + gg.c1.r + 1):
            temp = []
            for col in range(round(self.x) - gg.c1.r, round(self.x) + gg.c1.r + 1):
                # try:
                if state[col % gg.cellsX, row % gg.cellsY]:
                    arr[i] = state[col % gg.cellsX, row % gg.cellsY]
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

        self.observation = arr.reshape(1, gg.c1.n)

    def get_action(self):
        if np.random.random() < gg.eps or len(gg.states) == 0:
            self.action = np.random.choice(gg.choices)
            if self.piece_ss == GoblinSS and len(gg.states)%10 == 1:
                self.timer = len(gg.states)
                self.piece_ss = GoblinSwingSS
        elif self.x < gg.res//4 and self.y < gg.res//4:
            self.action = random.choice([2, 4])
        elif not self.human and self.x > gg.cellsX-4 and self.y > gg.cellsY-4:
            self.action = random.choice([1, 3])
        else:
            # self.action = np.argmax(c1.model.predict(self.observation)[0])
            pass

    def move_on_prediction(self, prediction):
        if self.human:
            ul_margin = 0.5
            dr_margin = 1.5
        else:
            ul_margin = 1.5
            dr_margin = 3

        if prediction == 1:  # UP
            if self.y > self.uWall+ul_margin:
                self.y -= min(self.acc*2/self.speed_mod, 1)
        if prediction == 2:  # DOWN
            if self.y <= gg.cellsY - self.dWall - dr_margin:
                self.y += min(self.acc*2/self.speed_mod, 1)
        if prediction == 3:  # LEFT
            if self.x > self.lWall+ul_margin:
                self.x -= min(self.acc*2/self.speed_mod, 1)
        if prediction == 4:  # RIGHT
            if self.x <= gg.cellsX - self.rWall - dr_margin:
                self.x += min(self.acc*2/self.speed_mod, 1)




# # Fonts:
textFont = pygame.font.SysFont('arial', 17)
continueFont = pygame.font.SysFont('arial', 14)
# # titleFont = pygame.font.Font(pygame.font.get_default_font(), 25)
# # I was forced to replace the line above for the line below
# # because Pyinstaller would find an error otherwise
titleFont = pygame.font.SysFont('arial', 25)

continueText = '[Press any key to continue]'
continueTextWidth = gg.textWidth(continueText, continueFont)




# showControls()
oof_sound = gg.path + 'music' + os.sep + 'OOF.wav'
ding_sound = gg.path + 'music' + os.sep + 'ding.wav'
rawr_sound = gg.path + 'music' + os.sep + 'RAWR.wav'
meow_sound = gg.path + 'music' + os.sep + 'meow.wav'
flipper = False
pygame.mixer.init()
pygame.mixer.music.set_volume(.3)


### Game execution ###




# def toggleScreenMode():
#     ''' Toggle between windowed and fullscreen mode '''
#     global screen, width, height, fullscreen
#     global cellWidth, cellHeight, windowHandle
#     pygame.display.quit()
#     pygame.display.init()
#     pygame.display.set_caption(windowTitle)
#     if os.path.exists(iconPath):
#         icon = pygame.image.load(iconPath)
#         pygame.display.set_icon(icon)
#     if fullscreen:
#         screen = pygame.display.set_mode(windowSize)
#         width, height = windowSize
#         updateWindowHandle()
#     else:
#         screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#         displayInfo = pygame.display.Info()
#         width = displayInfo.current_w
#         height = displayInfo.current_h
#     fullscreen = not fullscreen
#     cellWidth = width / cellsX
#     cellHeight = height / cellsY
#     updateCellsBorders()
#     updateScreen()


# Show initial game state
# updateScreen()





if __name__ == '__main__':
    mygame = gg
    mygame.setup_game()
    mygame.run()