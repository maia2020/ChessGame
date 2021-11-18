import pygame as p
import Engine 

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
    get_images() #Will load our images into our board
    running = True
    Square_Selected = () #No square is selected yet, keep track of the last click of the user -> tuple: (row , col)
    Player_Clicks = [] #Keep track of where player clicks -> two tuples: [(6 , 4) , (4 , 4)]

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:# Makes it possible for us to close the game 
                running = False 
            #Mouse Events:
            elif e.type == p.MOUSEBUTTONDOWN:
                Mouse_Pos = p.mouse.get_pos() # Keeps Track of the mouse's position (x,y)
                col = Mouse_Pos[0] // Square_Size
                row = Mouse_Pos[1] // Square_Size
                if Square_Selected == (row , col): #The user clicked the same square twice in the same turn
                    Square_Selected = () #Deselect the sqare
                    Player_Clicks = () #Clear Player_Clicks
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
                            Square_Selected = () #Reset the user clicks
                            Player_Clicks = []
                    if not movemade: 
                        Player_Clicks = [Square_Selected]
            #Key Handlers:
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo when 'z' is pressed 
                    gs.UndoMove()
                    movemade = True

        if movemade:
            validmoves = gs.ValidMoves() # Get the net validmoves after a move was made
            movemade = False

        DrawGame(Screen , gs)
        clock.tick(Max_Fps)
        p.display.flip()
    
def DrawGame(screen , gs): #Responsible for all the graphics
    DrawBoard(screen) #Drawn the squares that form the board
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


if __name__ == '__main__':
    main()