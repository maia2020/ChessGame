import random

PieceScore = {"K" : 0 , "Q" : 10 , "R" : 5 , "B" : 3 , "N" : 3 , "p" : 1} #Defines the value of each piece 
CheckmateScore = 1000
StalemateScore = 0

def FindRandomMove(ValidMoves):
    return ValidMoves[random.randint(0 , len(ValidMoves) - 1)]

def FindGreedyMove(gs , validMoves): #Search for the move based just on the value of the pieces
    TurnMultiplier = 1 if gs.whiteToMove else -1 
    OpponentMinMaxScore = CheckmateScore #Starts with the worts possible score for the AI
    BestPlayerMove = None
    random.shuffle(validMoves)
    for PlayerMove in validMoves:
        gs.MakeMove(PlayerMove)
        OpponentsMoves = gs.ValidMoves()
        OpponentMaxScore = -CheckmateScore
        for oppmove in OpponentsMoves: #This for loop hoes through our opponents best move and find its value or the highest score they can possibly get
            gs.MakeMove(oppmove)
            if gs.CheckMate:
                score = -TurnMultiplier * CheckmateScore
            elif gs.StaleMate:
                score = StalemateScore
            else:
                score = - TurnMultiplier * ScoreMaterial(gs.board)
            if score > OpponentMaxScore:
                OpponentMaxScore = score
            gs.UndoMove()
        if OpponentMaxScore < OpponentMinMaxScore: #If the the best response is worse than its last response, thats our move
            OpponentMinMaxScore = OpponentMaxScore
            BestPlayerMove = PlayerMove
        gs.UndoMove()
    return BestPlayerMove

#Defines the score of the board
def ScoreMaterial(board):
    Score = 0   
    for row in board:
        for square in row:
            if square[0] == 'w':
                Score += PieceScore[square[1]]
            elif square[0] == 'b':
                Score -= PieceScore[square[1]]
    return Score