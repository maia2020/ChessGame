import pygame as p
import Engine 
import ChessAI

p.init()
Width = Height = 512
Grid = 8 #Variable we'll use later to make a 8X8 chess board
Square_Size = Height // Grid #Size of each square that will form the board
Max_Fps = 15 #For some animations later on 
Images = {}

'''
Let's make a function to call the images just one time in the main loop.
It could be done directly in the loop, but I have plans to make it possible for the player to chose it's own set of pieces later on, 
so making it into a function will help with that
'''
def get_images():
    Pieces = ['bB' , 'bK' , 'bN' , 'bp' , 'bQ' , 'bR' , 'wB' , 'wK' , 'wN' , 'wp' , 'wQ' , 'wR'] #List with all the pieces
    for piece in Pieces: #For loop that will load all the pieces with the pygame function 'load_images'
        Images[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png") , (Square_Size , Square_Size)) 
        '''Save the image of the piece in the dictionary with the key beeing the name of the piece
        This way we can access an piece by using "Images['wp']" for example    '''
    

def main(): #Update our graphics and handle user inputs
    p.init()
    Screen = p.display.set_mode((Width , Height))
    clock = p.time.Clock()
    Screen.fill(p.Color("white")) # Just a background colour for the moment
    gs = Engine.GameState() # Just a simplification of the method's name 
    validmoves = gs.ValidMoves()
    movemade = False #Variable that will warn us when the player makes a move
    animate = False #Flag variable for when we should animate a move
    get_images() #Will load our images into our board
    running = True
    Square_Selected = () #No square is selected yet, keep track of the last click of the user -> tuple: (row , col)
    Player_Clicks = [] #Keep track of where player clicks -> two tuples: [(6 , 4) , (4 , 4)]
    GameOver = False #Flag variable for when the game is over
    PlayerOne = True #If a human is playin white = true , Ai playing white = false
    PlayerTwo = False #Same as above but for black

    while running:
        HumanTurn = (gs.whiteToMove and PlayerOne) or (not gs.whiteToMove and PlayerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:# Makes it possible for us to close the game 
                running = False 
            #Mouse Events:
            elif e.type == p.MOUSEBUTTONDOWN:
                if not GameOver and HumanTurn:
                    Mouse_Pos = p.mouse.get_pos() # Keeps Track of the mouse's position (x,y)
                    col = Mouse_Pos[0] // Square_Size
                    row = Mouse_Pos[1] // Square_Size
                    if Square_Selected == (row , col): #The user clicked the same square twice in the same turn
                        Square_Selected = () #Deselect the sqare
                        Player_Clicks = [] #Clear Player_Clicks
                    else: 
                        Square_Selected = (row , col)
                        Player_Clicks.append(Square_Selected) #Append for both, first and second click
                    if len(Player_Clicks) == 2: #After the second Click
                        move = Engine.Move(Player_Clicks[0] , Player_Clicks[1] , gs.board)
                        print(move.GetChessNotation())
                        for i in range(len(validmoves)):
                            if move == validmoves[i]:
                                gs.MakeMove(validmoves[i])
                                movemade = True
                                animate = True
                                Square_Selected = () #Reset the user clicks
                                Player_Clicks = []
                        if not movemade: 
                            Player_Clicks = [Square_Selected]
            #Key Handlers:
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo when 'z' is pressed 
                    gs.UndoMove()
                    movemade = True
                    animate = False #Don't animate the last move if we undo it 
                    GameOver = False
                if e.key == p.K_r: #Reset the board when 'r' is pressed:
                    gs = Engine.GameState() #Reinitialize our whole Game state
                    validmoves = gs.ValidMoves()
                    Square_Selected = ()
                    Player_Clicks = []
                    movemade = False
                    animate = False
                    GameOver = False

        #AI move finder logic:
        '''START of the RANDOM MOVE ai'''
        if not GameOver and not HumanTurn:
            AIMove = ChessAI.FindBestMove(gs , validmoves)
            if AIMove is None:
                AIMove = ChessAI.FindRandomMove(validmoves)
            gs.MakeMove(AIMove)
            movemade = True
            animate = True

        '''END of the RANDOM MOVE ai'''

        if movemade:
            if animate:
                AnimateMove(gs.movelog[-1] , Screen , gs.board , clock)
            validmoves = gs.ValidMoves() # Get the net validmoves after a move was made
            movemade = False
            animate = False

        DrawGame(Screen , gs , validmoves , Square_Selected)

        if gs.CheckMate:
            GameOver = True
            if gs.whiteToMove:
                DrawText(Screen , 'Black wins by checkmate')
            else:
                DrawText(Screen , 'White wins by checkmate')
        elif gs.StaleMate:
            GameOver = True
            DrawText(Screen , 'Stalemate')

        clock.tick(Max_Fps)
        p.display.flip()

#Highlight possible moves
def HighlightSquares(screen, gs , validmoves , Square_Selected):
    if Square_Selected != ():
       r ,  c = Square_Selected #Save the row and collum the user has selected
       if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b' ): #The piece selected is the player's colour
           #Highlight selected square
           s = p.Surface((Square_Size , Square_Size)) 
           s.set_alpha(100) #Transperance value -> 0 = transparent ; 255 = opaque
           s.fill(p.Color('blue'))
           screen.blit(s , (c*Square_Size , r*Square_Size))
           #Highlight moves from that square
           s.fill(p.Color(23 , 141 , 192))
           for move in validmoves:
               if move.StartRow == r and move.StartCol == c:
                   screen.blit(s , (move.EndCol*Square_Size , move.EndRow*Square_Size))

        


def DrawGame(screen , gs , validmoves , Square_Selected): #Responsible for all the graphics
    DrawBoard(screen) #Drawn the squares that form the board
    HighlightSquares(screen , gs , validmoves , Square_Selected) 
    DrawPieces(screen, gs.board) #Drawn pieces on top of the sqares

def DrawBoard(screen): 
    Colors = [p.Color("white") , p.Color("gray")]  
    for row in range(Grid): 
        for column in range(Grid): 
            color = Colors[((row + column) % 2)] # If the sum modded by 2 is even, then the colour is white, if it's odd then the colour is green
            p.draw.rect(screen , color , p.Rect(column*Square_Size , row*Square_Size , Square_Size , Square_Size))
def DrawPieces(screen, board):
    for row in range(Grid): 
        for column in range(Grid): 
            piece = board[row][column]
            if piece != "--": # If it isn't a empty square
                screen.blit(Images[piece] , p.Rect(column*Square_Size , row*Square_Size , Square_Size , Square_Size))

#Animating a move
def AnimateMove(move , screen , board , clock):
    Colors = [p.Color("white") , p.Color("gray")]  
    coords = [] #List of coordinates the animation will move through
    DeltaR = move.EndRow - move.StartRow
    DeltaC = move.EndCol - move.StartCol
    FramesPerSquare = 10 #Frames to Move one square
    FrameCount = (abs(DeltaR) + abs(DeltaC)) * FramesPerSquare
    for frame in range(FrameCount + 1):
        r , c = (move.StartRow + DeltaR*frame/FrameCount , move.StartCol + DeltaC*frame/FrameCount)
        DrawBoard(screen)
        DrawPieces(screen , board)
        #Erase the piece moved from its ending square
        color = Colors[(move.EndRow + move.EndCol) % 2 ]
        EndSquare = p.Rect(move.EndCol*Square_Size , move.EndRow*Square_Size , Square_Size , Square_Size)
        p.draw.rect(screen , color , EndSquare)
        #Drawn captured piece onto rectangle
        if move.PieceCaptured != '--':
            screen.blit(Images[move.PieceCaptured] , EndSquare)
        #Drawn the moving piece
        screen.blit(Images[move.PieceMoved] , p.Rect(c*Square_Size , r*Square_Size , Square_Size , Square_Size))
        p.display.flip()
        clock.tick(60)
    

def DrawText(screen , text):
#-----------------------------Display the dark text-----------------------------#
    font = p.font.SysFont("Helvitca" , 32 , True , False)
    TextObject = font.render(text , 0 , p.Color('Black'))
    TextLocation = p.Rect(0 , 0 , Width , Height).move(Width/2 - TextObject.get_width()/2 , Height/2 - TextObject.get_height()/2)
    screen.blit(TextObject , TextLocation)
#-----------------------------Display the dark text-----------------------------#
    TextObject = font.render(text , 0 , p.Color('Gray'))
    screen.blit(TextObject , TextLocation.move(2,2)) #Display the text with a different colour and a slightly different position, making a shadow effect
    
if __name__ == '__main__':
    main()