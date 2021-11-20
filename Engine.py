'''
    Here we'll store the information about the position, determine the valid moves and keep a move log.
'''
class GameState():
    def __init__(self):
        '''
        Our chess board we'll be a 8x8 2d list in which each element has 2 characters, the first one beeing the colour of the piece
        and the second one beeing the piece "name"
        And to represent the empty space on the board we'll just use "--"
        '''
        self.board = [
            ["bR" , "bN" , "bB" , "bQ" , "bK" , "bB" , "bN" , "bR"],
            ["bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp" , "bp"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["--" , "--" , "--" , "--" , "--" , "--" , "--" , "--"],
            ["wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp" , "wp"],
            ["wR" , "wN" , "wB" , "wQ" , "wK" , "wB" , "wN" , "wR"]]    

        self.MoveFunctions = {'p' : self.GetPawnMoves , 'R' : self.GetRookMoves , 'N' : self.GetKnightMoves , 
                              'B' : self.GetBishopMoves , 'Q' : self.GetQueenMoves , 'K' : self.GetKingMoves} #remove lots of if statemants that are commented bellow

        self.whiteToMove = True #Define that white is the first to move
        self.movelog = [] #Keep track of each move that was made
        self.whitekinglocation = (7,4)   #We'll keep track of the king's position so we can implement some valid moves.
        self.blackkinglocation = (0,4)
        self.CheckMate = False
        self.StaleMate = False
        self.enpassant = () #Keeps track of the square where en passant capture is possible
        self.CurrentCastlingRight = CastleRights(True,True,True,True)
        self.CastleRightsLog = [CastleRights(self.CurrentCastlingRight.wks , self.CurrentCastlingRight.bks , self.CurrentCastlingRight.wqs , self.CurrentCastlingRight.bqs)]
    
    def MakeMove(self, move): #Takes a move an execute it (Don't work for castling, pawn promotion and en-passant)
        self.board[move.StartRow][move.StartCol] = "--"
        self.board[move.EndRow][move.EndCol] = move.PieceMoved
        self.movelog.append(move) #Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #Swap Players
        if move.PieceMoved == "wK": #Updates the king's position
            self.whitekinglocation = (move.EndRow , move.EndCol)
        if move.PieceMoved == "bK": 
            self.blackkinglocation = (move.EndRow , move.EndCol)
        
        #Pawn Promotion:
        if move.IsPawnPromotion:
             self.board[move.EndRow][move.EndCol] = move.PieceMoved[0] + 'Q' #For now you can only promoto to a queen,but I will fix this later
        
        #En Passant Move:
        if move.isEnpassant: 
            self.board[move.StartRow][move.EndCol] = '--' #Capturing the pawn

        #Update enpassant variable:
        if move.PieceMoved[1] == 'p' and abs(move.StartRow - move.EndRow) == 2: #2 square pawn advances
            self.enpassant = ((move.EndRow - 1 , move.StartCol)) #The "middle" square 
        else:
            self.enpassant = () #If any other move is made we reset our enpassant list to be empty

        #Castle Move:
        if move.IsCastle:
            if move.EndCol - move.StartCol == 2: #Kingside Castle
                self.board[move.EndRow][move.EndCol-1] = self.board[move.EndRow][move.EndCol+1] #Moves the rook
                self.board[move.EndRow][move.EndCol+1] = '--' #Delete the 'old' rook
            else: #Queenside Castle
                self.board[move.EndRow][move.EndCol+1] = self.board[move.EndRow][move.EndCol-2] #Moves the rook
                self.board[move.EndRow][move.EndCol-2] = '--'

        #Update Castling Rights when a rook or a king move
        self.UpdateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.CurrentCastlingRight.wks , self.CurrentCastlingRight.bks , self.CurrentCastlingRight.wqs , self.CurrentCastlingRight.bqs))


    def UndoMove(self):
        if len(self.movelog) != 0: #make shure that there is a move to undu
            move = self.movelog.pop()
            self.board[move.StartRow][move.StartCol] = move.PieceMoved
            self.board[move.EndRow][move.EndCol] = move.PieceCaptured
            self.whiteToMove = not self.whiteToMove #Switch back turns
            if move.PieceMoved == "wK": #Updates the king's position
                self.whitekinglocation = (move.StartRow , move.StartCol)
            if move.PieceMoved == "bK": 
                self.blackkinglocation = (move.StartRow , move.StartCol)
            #Undo en passant moves:
            if move.isEnpassant:
                self.board[move.EndRow][move.EndCol] = '--' #Leave the square that the pawn took en passant blank
                self.board[move.StartRow][move.EndCol] = move.PieceCaptured
                self.enpassant = (move.EndRow , move.EndCol) #Makes it possible for us to redo our en passant
            #Undo a 2 square pawn advance
            if move.PieceMoved[1] == 'p' and abs(move.StartRow - move.EndRow) == 2:
                self.enpassant = ()
            #Undo Castling rights
            self.CastleRightsLog.pop() #Get rid of the new castle rights of the move we undid
            self.CurrentCastlingRight = self.CastleRightsLog[-1] #Set the caslte rights to it's last value
            #Undo Castle Moves
            if move.IsCastle:
                if move.EndCol - move.StartCol == 2: #KingSide
                    self.board[move.EndRow][move.EndCol+1] = self.board[move.EndRow][move.EndCol-1]
                    self.board[move.EndRow][move.EndCol-1] = '--'
                else: #Queenside 
                    self.board[move.EndRow][move.EndCol-2] = self.board[move.EndRow][move.EndCol+1]
                    self.board[move.EndRow][move.EndCol+1] = '--'

            

    def UpdateCastleRights(self , move): #Updates the castle rights given the move that was made
        if move.PieceMoved == 'wK':
            self.CurrentCastlingRight.wks = False
            self.CurrentCastlingRight.wqs = False
        elif move.PieceMoved == 'bK':
            self.CurrentCastlingRight.bks = False
            self.CurrentCastlingRight.bqs = False 
        elif move.PieceMoved == 'wR':
            if move.StartRow == 7: 
                if move.StartCol == 0:
                    self.CurrentCastlingRight.wqs = False
                if move.StartCol == 7:
                    self.CurrentCastlingRight.wks = False
        elif move.PieceMoved == 'bR':
            if move.StartRow == 0: 
                if move.StartCol == 0:
                    self.CurrentCastlingRight.bqs = False
                elif move.StartCol == 7:
                    self.CurrentCastlingRight.bks = False  
        #if a rook is captured
        if move.PieceCaptured == 'wR':
            if move.EndRow == 7:
                if move.EndCol == 0:
                    self.CurrentCastlingRight.wqs = False
                elif move.EndCol == 7:
                    self.CurrentCastlingRight.wks = False
        elif move.PieceCaptured == 'bR':
            if move.EndRow == 0:
                if move.EndCol == 0:
                    self.CurrentCastlingRight.bqs = False
                elif move.EndCol == 7:
                    self.CurrentCastlingRight.bks = False  
                    

    #All moves considering checks
    def ValidMoves(self):
        TempEnpassant = self.enpassant
        TempCastle = CastleRights(self.CurrentCastlingRight.wks , self.CurrentCastlingRight.bks ,
                                 self.CurrentCastlingRight.wqs , self.CurrentCastlingRight.bqs) #Copy the current castle rights
        #1) Generate all possible moves
        moves = self.AllPossibleMoves() 
        if self.whiteToMove:
            self.CastleMoves(self.whitekinglocation[0] , self.whitekinglocation[1] , moves)
        else:
            self.CastleMoves(self.blackkinglocation[0] , self.blackkinglocation[1] , moves)
        #2) For each move, make the move
        for i in range(len(moves)-1,-1,-1): #When removing from a list, go backwards through that list
            self.MakeMove(moves[i])
            #3) Generate all opponent's moves
            #4) For each of your opponent's moves,see if they attack your king
            #When whe use self.makemove() we actually changed to the other player's turn, so we have to change it again
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  #5) If they do attack your king, that's not a valid move
            self.whiteToMove = not self.whiteToMove #Changes back to the other player's turn so we can undo the move
            self.UndoMove()   
        
        if len(moves) == 0: #Either Checkmate ou Stalemate
            if self.inCheck():
                self.CheckMate = True
            else:
                self.StaleMate = True
        else:  
            self.CheckMate = False
            self.StaleMate = False

        self.enpassant = TempEnpassant
        self.CurrentCastlingRight = TempCastle
        return moves

    def AllPossibleMoves(self):     #All moves without considering checks
        moves = []
        for r in range(len(self.board)): #Number of rows
            for c in range(len(self.board[r])): #Number of columns in the current row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    '''if piece == 'p':
                        self.GetPawnMoves(r , c , moves)                     This statemants were simplifed by the dictionary MoveFunctions 
                    elif piece =='R':
                        self.GetRookMoves(r , c , moves)'''
                    self.MoveFunctions[piece](r , c , moves) #calls the appropriate move funciton based on piece type
        return moves

    def inCheck(self): #Determine if the current player is in check
        if self.whiteToMove:
            return self.SquareUnderAttack(self.whitekinglocation[0] , self.whitekinglocation[1])
        else:  
            return self.SquareUnderAttack(self.blackkinglocation[0] , self.blackkinglocation[1])
        
    def SquareUnderAttack(self , r , c): #Determine if the enemy can attack the square r ,c 
        self.whiteToMove = not self.whiteToMove #switch to the opponent' POV
        oppmoves = self.AllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #Switch turns back
        for move in oppmoves:
            if move.EndRow == r and move.EndCol == c: #Square is under attack
                return True
        return False 
        


 #--------------------------------Define the possible moves for each piece---------------------------------------------------#

    def GetPawnMoves(self , r , c , moves):
        if self.whiteToMove: #WHITE PAWN MOVES
            if self.board[r-1][c] == '--': # the square in front of the pawn is empty
                moves.append(Move((r,c) , (r-1,c) , self.board))
                if r == 6 and self.board[r-2][c] == '--': #Makes it possible for the paw to moove two squares on the first round
                    moves.append(Move((r,c) , (r-2,c) , self.board))
            if c - 1 >= 0: #we don't want the piece to go off the board
                if self.board[r-1][c-1][0] == 'b': #Just makes it possible to capture if the piece is black (LEFT)
                    moves.append(Move((r,c) , (r-1,c-1) , self.board))
                elif (r-1 , c-1) == self.enpassant:
                    moves.append(Move((r,c) , (r-1,c-1) , self.board , enpassant = True))
            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == 'b': #Just makes it possible to capture if the piece is black (RIGHT)
                    moves.append(Move((r,c) , (r-1,c+1) , self.board))
                elif (r-1 , c+1) == self.enpassant:
                    moves.append(Move((r,c) , (r-1,c+1) , self.board , enpassant = True))
        else: #BLACK PAWN MOVES
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c) , (r+1,c) , self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r,c) , (r+2,c) , self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c) , (r+1,c-1) , self.board))
                elif (r+1 , c-1) == self.enpassant:
                    moves.append(Move((r,c) , (r+1,c-1) , self.board , enpassant = True))
            if c + 1 <= 7: 
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c) , (r+1,c+1), self.board))
                elif (r+1 , c+1) == self.enpassant:
                    moves.append(Move((r,c) , (r+1,c+1) , self.board , enpassant = True))




    def GetRookMoves(self, r , c , moves): 
        directions = ((-1,0) , (0, -1) , (1,0) , (0,1))  #UP LEFT DOWN RIGHT
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8: #Respect the limit of the board
                    endpiece = self.board[endrow][endcol]
                    if endpiece == '--': #If the square is empty
                        moves.append(Move((r,c) , (endrow,endcol) , self.board))
                    elif endpiece[0] == enemy: #If there is a opposite color piece in the square:
                        moves.append(Move((r,c) , (endrow,endcol) , self.board))
                        break #this brake is important so the rook can't jump over pieces.
                    else: #if there is a friendly piece
                        break
                else: #Off board
                    break

    def GetBishopMoves(self, r , c , moves): #Basically the same process as the rook moves but changing the directions so it moves in diagonals
        directions = ((-1,-1) , (-1, 1) , (1,-1) , (1,1)) #UPLEFT UPRIGHT DOWNLEFT DOWNRIGHT
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8: 
                    endpiece = self.board[endrow][endcol]
                    if endpiece == '--': 
                        moves.append(Move((r,c) , (endrow,endcol) , self.board))
                    elif endpiece[0] == enemy: 
                        moves.append(Move((r,c) , (endrow,endcol) , self.board))
                        break 
                    else: 
                        break
                else: 
                    break
                
    def GetQueenMoves(self, r , c , moves):
        self.GetRookMoves(r , c , moves)
        self.GetBishopMoves(r , c , moves)

    def GetKnightMoves(self, r , c , moves):
        directions = ((-1,-2) , (1,-2) , (-1,2) , (1,2) , (-2,-1) , (2,-1) , (-2,1) , (2,1))#Responsible for those 'L'-shaped moves 
        ally = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endrow = r + d[0]
            endcol = c + d[1]
            if 0 <= endrow < 8 and 0 <= endcol <8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != ally:
                    moves.append(Move((r,c) , (endrow,endcol) , self.board))

    def GetKingMoves(self, r , c , moves):
        directions = ((-1,-1) , (-1,0) , (-1,1) , (0,-1), (0,1) , (1,-1) , (1,0) , (1,1))
        ally = "w" if self.whiteToMove else "b"
        for i in range(8):
            endrow = r + directions[i][0]
            endcol = c + directions[i][1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != ally:
                    moves.append(Move((r,c) , (endrow,endcol) , self.board))
          
    def CastleMoves(self , r , c , moves): #Generate all valid castle moves for the king at the given square (r,c) and add the to the list of moves
        if self.SquareUnderAttack(r,c): #If we use the "SquareUnderAtack" or "InCheck" functions we would end up with a infinity recursion
            return #Can't castle while in check
        if (self.whiteToMove and self.CurrentCastlingRight.wks) or (not self.whiteToMove and self.CurrentCastlingRight.bks):
            self.KingSideCastle(r , c , moves)
        if (self.whiteToMove and self.CurrentCastlingRight.wqs) or (not self.whiteToMove and self.CurrentCastlingRight.bqs):
            self.QueenSideCastle(r , c , moves)
    
    def KingSideCastle(self, r , c , moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.SquareUnderAttack(r , c+1) and not self.SquareUnderAttack(r , c+2):
                moves.append(Move((r,c) , (r,c+2) , self.board , IsCastle = True))
    
    def QueenSideCastle(self , r , c , moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.SquareUnderAttack(r , c-1) and not self.SquareUnderAttack(r , c-2):
                moves.append(Move((r,c) , (r,c-2) , self.board , IsCastle = True))


 #--------------------------------Define the possible moves for each piece---------------------------------------------------#
 
class CastleRights():
    def __init__(self , wks ,  wqs  , bks , bqs): #White king or queen side / Black king or queen side
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

class Move():
    '''
    First, let's implement the chess board notation.
    Using numbers (1-8) for the row and letters (a-h) for the columns. 
    '''
    RanksToRows = {"1" : 7 , "2" : 6 , "3" : 5 , "4" : 4 , "5" : 3 , "6" : 2 , "7" : 1 , "8" : 0}
    RowsToRanks = {v: k for k, v in RanksToRows.items()} #Cool way to invert a dictionary
    FileToCols = {"a" : 0 , "b" : 1 , "c" : 2 , "d" : 3 , "e" : 4 , "f" : 5 , "g" : 6 , "h" : 7}
    ColsToFile = {v: k for k, v in FileToCols.items()} 

    def __init__(self , Start_Square , End_Square , board , enpassant = False , IsCastle = False):
        #Some variables that will make it easier for us to work with the tuples
        self.StartRow = Start_Square[0]
        self.StartCol = Start_Square[1]
        self.EndRow = End_Square[0]
        self.EndCol = End_Square[1] 
        self.PieceMoved = board[self.StartRow][self.StartCol]
        self.PieceCaptured = board[self.EndRow][self.EndCol]
        #Pawn Promo:
        self.IsPawnPromotion = False
        
        if (self.PieceMoved == 'wp' and self.EndRow == 0) or (self.PieceMoved == 'bp' and self.EndRow == 7):
            self.IsPawnPromotion = True
        #En passant:
        self.isEnpassant = enpassant
        if self.isEnpassant:
            self.PieceCaptured = 'wp' if self.PieceMoved == 'bp' else 'bp'
        self.moveID = self.StartRow * 1000 + self.StartCol * 100 + self.EndRow * 10 + self.EndCol
        #Castle:
        self.IsCastle = IsCastle

    '''
    Overriding the equals methos due to the use of the "move" as a class and not a string.
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False



    def GetChessNotation(self):
        return self.GetRankFile(self.StartRow , self.StartCol) + self.GetRankFile(self.EndRow , self.EndCol)

    def GetRankFile(self , r , c):
        return self.ColsToFile[c] + self.RowsToRanks[r]