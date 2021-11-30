import random

PieceScore = {"K" : 0 , "Q" : 10 , "R" : 5 , "B" : 3 , "N" : 3 , "p" : 1} #Defines the value of each piece 
CheckmateScore = 1000
StalemateScore = 0
DEPTH =  1
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
        if gs.StaleMate: #makes the AI faster because, if the game situation is a stalemate or a checkmate, there is no need to go and check all the opponents moves
            OpponentMaxScore = StalemateScore
        elif gs.CheckMate:
            OpponentMaxScore = - CheckmateScore
        else: 
            OpponentMaxScore = -CheckmateScore
            for oppmove in OpponentsMoves: #This for loop hoes through our opponents best move and find its value or the highest score they can possibly get
                gs.MakeMove(oppmove)
                gs.ValidMoves()
                if gs.CheckMate:
                    score = CheckmateScore
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

def FindBestMove(gs, validMoves): #Helper method to make the first recursive call NOT WORKING FOR SOME REASON
    global NextMove
    NextMove = None
    #MoveMinMax(gs, validMoves, DEPTH , gs.whiteToMove)
    MoveNegaMax(gs , validMoves , DEPTH , 1 if gs.whiteToMove else -1)
    return NextMove


def MoveMinMax(gs , validMoves , depth , WhiteToMove): #Pretty similar to what we did above, but way cleaner
    global NextMove 
    if depth == 0:
        return ScoreMaterial(gs.board)

    if WhiteToMove:
        MaxScore = -CheckmateScore
        for move in validMoves:
            gs.MakeMove(move)
            NextMove = gs.ValidMoves()
            score = MoveMinMax(gs, NextMove , depth - 1 , False)
            if score > MaxScore: 
                MaxScore = score
                if depth == DEPTH:
                    NextMove = move
            gs.UndoMove()
        return MaxScore

    else:
        MinScore = CheckmateScore
        for move in validMoves:
            gs.MakeMove(move)
            NextMove = gs.ValidMoves()
            score = MoveMinMax(gs , NextMove , depth - 1 , True)
            if score < MinScore:
                MinScore = score
                if depth == DEPTH:
                    NextMove = move
            gs.UndoMove()
        return MinScore

def MoveNegaMax(gs , validMoves , depth , TurnMultiplier):
    global NextMove
    if depth == 0:
        return TurnMultiplier * ScoreBoard(gs)

    MaxScore = -CheckmateScore
    for move in validMoves:
        gs.MakeMove(move)
        NextMove = gs.ValidMoves()
        score = -MoveNegaMax(gs,NextMove , depth - 1 , -TurnMultiplier)
        if score > MaxScore:
            MaxScore = score
            if depth == DEPTH:
                NextMove = move
        gs.UndoMove()
    return MaxScore

def ScoreBoard(gs): #Positive Score is good for white, a negative score is good for black
    if gs.CheckMate: #Check if it is a checkmate, because if it is, there is no meaning to score the pieces
        if gs.WhiteToMove: 
            return -CheckmateScore #Black wins
        else: 
            return CheckmateScore #White Wins
    elif gs.StaleMate:
        return StalemateScore

    Score = 0   
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                Score += PieceScore[square[1]]
            elif square[0] == 'b':
                Score -= PieceScore[square[1]]
    return Score


#Defines the score of the board based on the material
def ScoreMaterial(board):
    Score = 0   
    for row in board:
        for square in row:
            if square[0] == 'w':
                Score += PieceScore[square[1]]
            elif square[0] == 'b':
                Score -= PieceScore[square[1]]
    return Score