import pygame as p
import pygame_menu as pm
from Chess import ChessEngine
import random

WIDTH = HEIGHT = 512  # or 400
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}
MODE = 1
COLOR = 1

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def set_difficulty(value, difficulty):
    global MODE
    MODE = difficulty


def set_color(value, color):
    global COLOR
    COLOR = color


def start_the_game():
    print(MODE)
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()  # no square is selected, keep track of the last user click
    playerClicks = []  # keep track of player clicks
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    if gameOver:
                        gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # same square twice
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if move.isPawnPromotion:


                                    flag = True
                                    while flag:
                                        for s in p.event.get():
                                            piecePromoted = 'Q'
                                            if s.type == p.KEYDOWN:

                                                if s.key == p.K_q:
                                                    piecePromoted = 'Q'

                                                elif s.key == p.K_n:
                                                    piecePromoted = 'N'

                                                elif s.key == p.K_o:
                                                    piecePromoted = 'R'

                                                elif s.key == p.K_b:
                                                    piecePromoted = 'B'
                                                flag = False
                                                gs.makeMove(validMoves[i], piecePromoted)
                                else:
                                    gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif COLOR == 1:
                if not gs.whiteToMove and MODE == 1 and not gameOver:
                    validMoves = gs.getValidMoves()
                    if not gameOver:
                        move = random.choice(validMoves)
                        if move.isPawnPromotion:
                            x = random.randint(0, 3)
                            print(x)
                            if x == 0:
                                gs.makeMove(move, 'Q')
                            elif x == 1:
                                gs.makeMove(move, 'R')
                            elif x == 2:
                                gs.makeMove(move, 'B')
                            elif x == 1:
                                gs.makeMove(move, 'N')
                        else:
                            gs.makeMove(move)
                        moveMade = True
                        animate = True
            elif COLOR == 2:
                if gs.whiteToMove and MODE == 1 and not gameOver:
                    validMoves = gs.getValidMoves()
                    if not gameOver:
                        move = random.choice(validMoves)
                        if move.isPawnPromotion:
                            x = random.randint(0, 3)
                            print(x)
                            if x == 0:
                                gs.makeMove(move, 'Q')
                            elif x == 1:
                                gs.makeMove(move, 'R')
                            elif x == 2:
                                gs.makeMove(move, 'B')
                            elif x == 1:
                                gs.makeMove(move, 'N')
                        else:
                            gs.makeMove(move)
                        moveMade = True
                        animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, ' Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    menu = pm.Menu(WIDTH, HEIGHT, 'Chess', theme=pm.themes.THEME_DARK)
    menu.add_button('Play', start_the_game)
    menu.add_selector('Difficulty :', [('VS Computer', 1), ('VS Player', 2)], onchange=set_difficulty)
    menu.add_selector('Color :', [('White', 1), ('Black', 2)], onchange=set_color)
    menu.add_button('Quit', pm.events.EXIT)
    menu.mainloop(screen)


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))





def drawText(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, False, p.Color('Red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == '__main__':
    main()
