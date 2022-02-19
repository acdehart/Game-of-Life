from tkinter import filedialog
from tkinter import messagebox
from collections import deque
from time import time, sleep
import pygame, numpy, tkinter
import os, sys, pickle

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

# Colors:
white = 240, 240, 240
grey = 128, 128, 128
darkgrey = 200, 200, 200
black = 0, 0, 0
blue = 0, 0, 128
red = 128, 0, 0

# Window creation:
pygame.init()  # Init all imported pygame modules
iconPath = path + 'icon.png'
windowTitle = 'Game of Life'
pygame.display.set_caption(windowTitle)
if os.path.exists(iconPath):
    icon = pygame.image.load(iconPath)
    pygame.display.set_icon(icon)
windowSize = 600, 600
res = 20
width, height = windowSize
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
gameState = numpy.zeros((cellsX, cellsY), bool)

# Values to serialize:
stepByStep = False
wraparound = True
delayInt = 1  # Speed

# Other values:
delay = 0.001
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
gameState[19, 8] = 1
gameState[20, 5] = 1
gameState[20, 6] = 1
gameState[20, 8] = 1
gameState[21, 7] = 1
gameState[21, 8] = 1
# Glider:
gameState[cellsX - 10 + 1, 8] = 1
gameState[cellsX - 10 + 2, 6] = 1
gameState[cellsX - 10 + 2, 8] = 1
gameState[cellsX - 10 + 3, 7] = 1
gameState[cellsX - 10 + 3, 8] = 1
# Lotus flower
gameState[6, 20] = 1
gameState[6, 21] = 1
gameState[7, 19] = 1
gameState[7, 20] = 1
gameState[7, 22] = 1
gameState[8, 20] = 1
gameState[8, 21] = 1
# Pentadecathlon
gameState[19, 17] = 1
gameState[19, 18] = 1
gameState[19, 19] = 1
gameState[19, 20] = 1
gameState[19, 21] = 1
gameState[19, 22] = 1
gameState[19, 23] = 1
gameState[19, 24] = 1
gameState[20, 17] = 1
gameState[20, 19] = 1
gameState[20, 20] = 1
gameState[20, 21] = 1
gameState[20, 22] = 1
gameState[20, 24] = 1
gameState[21, 17] = 1
gameState[21, 18] = 1
gameState[21, 19] = 1
gameState[21, 20] = 1
gameState[21, 21] = 1
gameState[21, 22] = 1
gameState[21, 23] = 1
gameState[21, 24] = 1
# Blinker:
gameState[cellsX - 10 + 2, 19] = 1
gameState[cellsX - 10 + 2, 20] = 1
gameState[cellsX - 10 + 2, 21] = 1

r = 10


class player:
    def __init__(self):
        self.living = True
        self.x = cellsX // 2
        self.y = cellsY // 2

    def drawPlayer(self):
        ''' Draw player's cell with coordinates (x, y) '''
        pygame.draw.circle(screen, blue, [res * self.x + r, res * self.y + r], r)
        # pygame.draw.circle(screen, blue, [0, 0], 10)


p1 = player()


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
pygame.mixer.init()
pygame.mixer.music.load(oof_sound)


### Game execution ###

def currentCell():
    ''' Cell coordinates of the current position of the mouse '''
    posX, posY = pygame.mouse.get_pos()
    return (int(numpy.floor(posX / cellWidth)),
            int(numpy.floor(posY / cellHeight)))


def drawCell(x, y):
    ''' Draw cell with coordinates (x, y) in the screen '''
    if gameState[x, y] == 0:
        pygame.draw.polygon(screen, grey, poly[x, y], 0)
        pygame.draw.polygon(screen, grey, poly[x, y], 1)
        if len(states) > 0:
            if states[-1][x, y] == 1:
                pygame.draw.polygon(screen, red, poly[x, y], 0)
                pygame.draw.polygon(screen, grey, poly[x, y], 1)
    else:
        pygame.draw.polygon(screen, darkgrey, poly[x, y], 0)
        pygame.draw.polygon(screen, grey, poly[x, y], 1)


def updateScreen():
    ''' Update the screen with the current game state '''
    global gamePaused
    screen.fill(screenColor)
    for y in range(0, cellsY):
        for x in range(0, cellsX):
            drawCell(x, y)
    if p1.living:
        p1.drawPlayer()

    pygame.display.update()

    if not p1.living:
        sleep(0.5)
        restart_game()

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
    for y in range(0, cellsY):
        for x in range(0, cellsX):
            neighbors = liveNeighbors(x, y)
            # Any dead cell with 3 live neighbors becomes a live cell.
            if gameState[x, y] == 0 and neighbors == 3:
                newGameState[x, y] = 1
            # Any live cell with less than 2 or more than 3 live neighbors dies.
            elif gameState[x, y] == 1 and (neighbors < 2 or neighbors > 3):
                newGameState[x, y] = 0
                if p1.x == x and p1.y == y and p1.living:
                    p1.living = False
                    pygame.mixer.music.play()

    updateGameState(newGameState)
    updateScreen()


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
                    nextGeneration()
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
                updateGameState(newGameState)
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
                filename = filedialog.asksaveasfilename(initialdir=savesDir, \
                                                        defaultextension='.dat')
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
                filename = filedialog.askopenfilename(initialdir=savesDir, \
                                                      initialfile=firstFile)
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
    # Handle mouse dragging
    if mouseClicked:
        x, y = currentCell()
        gameState[x, y] = cellValue
        drawCell(x, y)
        pygame.display.update()


def restart_game():
    global gamePaused
    newGameState = numpy.random.choice \
        (a=[0, 1], size=(cellsX, cellsY))
    p1.living = True
    updateGameState(newGameState)
    gamePaused = False
    updateScreen()


while True:
    # Event handling:
    if isTryingToQuit():
        sys.exit()
    handle_user_input()

    if not stepByStep and not gamePaused:
        if time() - lastTime > delay:
            nextGeneration()
            lastTime = time()

    # Sleep for a moment to avoid unnecessary computation
    sleep(0.01)
