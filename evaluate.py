import chess

class Evaluation:

    def __init__(self):
        pass

    

    def evaluate(self, board):

        PawnValue = 100
        KnightValue = 300
        BishopValue = 320
        RookValue = 500
        QueenValue = 900

        PieceValueList = (PawnValue, KnightValue, BishopValue, RookValue, QueenValue)
        passedPawnBonuses = (0, 120, 80, 50, 30, 15, 15)
        isolatedPawnPenaltyByCount = (0, -10, -25, -50, -75, -75, -75, -75, -75)
        kingPawnShieldScores = (4, 7, 4, 3, 6, 3)

        endgameMaterialStart = RookValue * 2 + BishopValue + KnightValue


        def countPiece(board, color):
            board_fen = list(board.fen())[0]
            PieceList = ['p', 'n', 'b', 'r', 'q']
            if color == True:
                for i in range(5):
                    PieceList[i] = PieceList[i].upper()

            PawnCount = board_fen.count(PieceList[0])
            KnightCount = board_fen.count(PieceList[1])
            BishopCount = board_fen.count(PieceList[2])
            RookCount = board_fen.count(PieceList[3])
            QueenCount = board_fen.count(PieceList[4])

            return PawnCount, KnightCount, BishopCount, RookCount, QueenCount


        def materialScore(board, color):

            countPieceList = countPiece(board, color)
            materialScore = 0
            for i in range(5):
                evalPiece += countPieceList[i] * PieceValueList[i]

            return materialScore


        def setEndgameT(board, color):

            pieceCountList = countPiece(board, color)
            endgameStartWeight = 125
            endgameWeightSum = pieceCountList[4] * 45 + pieceCountList[3] * 20 + pieceCountList[2] * 10 + pieceCountList[1] * 10
            endgameT = 1 - min(1, endgameWeightSum / endgameStartWeight)

            return endgameT


        def evaluatePieceSquareTables(color, board, endgameT):

            Pawns = (
            (0,   0,   0,   0,   0,   0,   0,   0),
            (50,  50,  50,  50,  50,  50,  50,  50),
            (10,  10,  20,  30,  30,  20,  10,  10),
            (5,   5,  10,  25,  25,  10,   5,   5),
            (0,   0,   0,  20,  20,   0,   0,   0),
            (5,  -5, -10,   0,   0, -10,  -5,   5),
            (5,  10,  10, -20, -20,  10,  10,   5),
            (0,   0,   0,   0,   0,   0,   0,   0)
            )

            PawnsEnd = (
            (0,   0,   0,   0,   0,   0,   0,   0),
            (80,  80,  80,  80,  80,  80,  80,  80),
            (50,  50,  50,  50,  50,  50,  50,  50),
            (30,  30,  30,  30,  30,  30,  30,  30),
            (20,  20,  20,  20,  20,  20,  20,  20),
            (10,  10,  10,  10,  10,  10,  10,  10),
            (10,  10,  10,  10,  10,  10,  10,  10),
            (0,   0,   0,   0,   0,   0,   0,   0)
            )

            Rooks =  (
            (0,  0,  0,  0,  0,  0,  0,  0),
            (5, 10, 10, 10, 10, 10, 10,  5),
            (-5,  0,  0,  0,  0,  0,  0, -5),
            (-5,  0,  0,  0,  0,  0,  0, -5),
            (-5,  0,  0,  0,  0,  0,  0, -5),
            (-5,  0,  0,  0,  0,  0,  0, -5),
            (-5,  0,  0,  0,  0,  0,  0, -5),
            (0,  0,  0,  5,  5,  0,  0,  0)
            )

            Knights = (
            (-50,-40,-30,-30,-30,-30,-40,-50),
            (-40,-20,  0,  0,  0,  0,-20,-40),
            (-30,  0, 10, 15, 15, 10,  0,-30),
            (-30,  5, 15, 20, 20, 15,  5,-30),
            (-30,  0, 15, 20, 20, 15,  0,-30),
            (-30,  5, 10, 15, 15, 10,  5,-30),
            (-40,-20,  0,  5,  5,  0,-20,-40),
            (-50,-40,-30,-30,-30,-30,-40,-50),
            )

            Bishops =  (
            (-20,-10,-10,-10,-10,-10,-10,-20),
            (-10,  0,  0,  0,  0,  0,  0,-10),
            (-10,  0,  5, 10, 10,  5,  0,-10),
            (-10,  5,  5, 10, 10,  5,  5,-10),
            (-10,  0, 10, 10, 10, 10,  0,-10),
            (-10, 10, 10, 10, 10, 10, 10,-10),
            (-10,  5,  0,  0,  0,  0,  5,-10),
            (-20,-10,-10,-10,-10,-10,-10,-20),
            )

            Queens =  (
            (-20,-10,-10, -5, -5,-10,-10,-20),
            (-10,  0,  0,  0,  0,  0,  0,-10),
            (-10,  0,  5,  5,  5,  5,  0,-10),
            (-5,  0,  5,  5,  5,  5,  0, -5),
            (0,  0,  5,  5,  5,  5,  0, -5),
            (-10,  5,  5,  5,  5,  5,  0,-10),
            (-10,  0,  5,  0,  0,  0,  0,-10),
            (-20,-10,-10, -5, -5,-10,-10,-20)
            )

            KingStart = (
            (-80, -70, -70, -70, -70, -70, -70, -80), 
            (-60, -60, -60, -60, -60, -60, -60, -60),
            (-40, -50, -50, -60, -60, -50, -50, -40),
            (-30, -40, -40, -50, -50, -40, -40, -30), 
            (-20, -30, -30, -40, -40, -30, -30, -20), 
            (-10, -20, -20, -20, -20, -20, -20, -10), 
            (20, 20, -5, -5, -5, -5, 20, 20), 
            (20, 30, 10, 0, 0, 10, 30, 20)
            )

            KingEnd = (
            (-20, -10, -10, -10, -10, -10, -10, -20),
            (-5, 0, 5, 5, 5, 5, 0, -5), 
            (-10, -5, 20, 30, 30, 20, -5, -10), 
            (-15, -10, 35, 45, 45, 35, -10, -15), 
            (-20, -15, 30, 40, 40, 30, -15, -20), 
            (-25, -20, 20, 25, 25, 20, -20, -25), 
            (-30, -25, 0, 0, 0, 0, -25, -30), 
            (-50, -30, -30, -30, -30, -30, -30, -50)
            )


            value = 0

            if color == True: # WHITE

                for square in chess.SQUARES:
                    piece = board.piece_at(square)
                    if piece is not None and piece.symbol() == 'P' and piece.color == chess.WHITE
                        value += Pawns[7 - chess.square_rank(square)][chess.square_file(square)] * (1 - endgameT)
                        value += PawnsEnd[7 - chess.square_rank(square)][chess.square_file(square)] * endgameT
                    elif piece is not None and piece.symbol() == 'N' and piece.color == chess.WHITE: 
                        value += Knights[7 - chess.square_rank(square)][chess.square_file(square)]
                    elif piece is not None and piece.symbol() == 'B' and piece.color == chess.WHITE: 
                        value += Bishops[7 - chess.square_rank(square)][chess.square_file(square)]
                    elif piece is not None and piece.symbol() == 'R' and piece.color == chess.WHITE: 
                        value += Rooks[7 - chess.square_rank(square)][chess.square_file(square)]
                    elif piece is not None and piece.symbol() == 'Q' and piece.color == chess.WHITE: 
                        value += Queens[7 - chess.square_rank(square)][chess.square_file(square)]
                    elif piece is not None and piece.symbol() == 'K' and piece.color == chess.WHITE and endgameT == 0:
                        value += KingStart[7 - chess.square_rank(square)][chess.square_file(square)]
                    elif piece is not None and piece.symbol() == 'K' and piece.color == chess.WHITE and endgameT == 1:
                        value += KingEnd[7 - chess.square_rank(square)][chess.square_file(square)]

            else: # BLACK

                    for square in chess.SQUARES:
                        piece = board.piece_at(square)
                        if piece is not None and piece.symbol() == 'p' and piece.color == chess.BLACK:
                            value += Pawns[chess.square_rank(square)][7 - chess.square_file(square)] * (1 - endgameT)
                            value += PawnsEnd[chess.square_rank(square)][7 - chess.square_file(square)] * endgameT
                        elif piece is not None and piece.symbol() == 'n' and piece.color == chess.BLACK: 
                            value += Knights[chess.square_rank(square)][7 - chess.square_file(square)]
                        elif piece is not None and piece.symbol() == 'b' and piece.color == chess.BLACK: 
                            value += Bishops[chess.square_rank(square)][7 - chess.square_file(square)]
                        elif piece is not None and piece.symbol() == 'r' and piece.color == chess.BLACK: 
                            value += Rooks[chess.square_rank(square)][7 - chess.square_file(square)]
                        elif piece is not None and piece.symbol() == 'q' and piece.color == chess.BLACK: 
                            value += Queens[chess.square_rank(square)][7 - chess.square_file(square)]
                        elif piece is not None and piece.symbol() == 'K' and piece.color == chess.BLACK and endgameT == 0:
                            value += KingStart[chess.square_rank(square)][7 - chess.square_file(square)]
                        elif piece is not None and piece.symbol() == 'K' and piece.color == chess.BLACK and endgameT == 1:
                            value += KingEnd[chess.square_rank(square)][7 - chess.square_file(square)]

            return value


        def mopUpEval(color, board, enemyEndgameT, whiteMaterialScore, blackMaterialScore):


            def findKing(board, color):
                
                if color == True:
                    for square in chess.SQUARES:
                        piece = board.piece_at(square)
                        if piece is not None and piece.symbol() == 'K' and piece.color == chess.WHITE:
                            return chess.square_rank(square), chess.square_file(square)
                
                else:
                    for square in chess.SQUARES:
                        piece = board.piece_at(square)
                        if piece is not None and piece.symbol() == 'k' and piece.color == chess.BLACK:
                            return chess.square_rank(square), chess.square_file(square)


            if whiteMaterialScore > blackMaterialScore + PawnValue * 2 and enemyEndgameT > 0:

                mopUpScore = 0
                friendlyColor = color
                enemyColor = not color

                friendlyKingSquare = findKing(board, friendlyColor)
                enemyKingSquare = findKing(board, enemyColor)
                # Encourage moving king closer to opponent king
                mopUpScore += (14 - abs(friendlyKingSquare[0] - enemyKingSquare[0]) - abs(friendlyKingSquare[1] - enemyKingSquare[1]))
                # Encourage pushing opponent king to edge of board
                mopUpScore += (max(3 - enemyKingSquare[0], enemyKingSquare[0] - 4) + max(3 - enemyKingSquare[1], enemyKingSquare[1] - 4)) * 10

                return mopUpScore * enemyEndgameT
            
            return 0


        def evaluatePawns(color, board):


            def findPawn(board, color):

                pawnPosition = []
                    
                if color == True:
                    for square in chess.SQUARES:
                        piece = board.piece_at(square)
                        if piece is not None and piece.symbol() == 'P' and piece.color == chess.WHITE:
                            pawnPosition.append(chess.square_rank(square), chess.square_file(square))
                
                else:
                    for square in chess.SQUARES:
                        piece = board.piece_at(square)
                        if piece is not None and piece.symbol() == 'p' and piece.color == chess.BLACK:
                            pawnPosition.append(chess.square_rank(square), chess.square_file(square))

                return pawnPosition
            
            bonus = 0

            pawnPositions = findPawn(board, color)
            numPassedPawn = 0
            numIsolatedPawn = 0
            numSquaresFromPromotion = []


            for position in pawnPositions:

                passed_pawn = True
                isolated_pawn = True

                if color == True:

                    for file in range(position[1] - 1, position[1] + 2, 1):

                        for rank in range(position[0] + 1, 8, 1):
                            square = chess.square(file, rank)
                            if board.piece_at(square) == 'p':
                                passed_pawn = False
                                break
                        
                        for rank in range(0, 8, 1):
                            square = chess.square(file, rank)
                            if board.piece_at(square) == 'P':
                                isolated_pawn = False
                                break
                        
                        break
                    
                    if passed_pawn:
                        numPassedPawn += 1
                        numSquaresFromPromotion.append(7 - position[0])
                    
                    if isolated_pawn:
                        numIsolatedPawn += 1

                else:

                    for file in range(position[1] - 1, position[1] + 2, 1):
    
                        for rank in range(position[0] - 1, -1, -1):
                            square = chess.square(file, rank)
                            if board.piece_at(square) == 'P':
                                passed_pawn = False
                                break
                        
                        for rank in range(0, 8, 1):
                            square = chess.square(file, rank)
                            if board.piece_at(square) == 'p':
                                isolated_pawn = False
                                break
                        
                        break
                    
                    if passed_pawn:
                        numPassedPawn += 1
                        numSquaresFromPromotion.append(position[0])
                    
                    if isolated_pawn:
                        numIsolatedPawn += 1

            for i in range(numPassedPawn):
                bonus += passedPawnBonuses[numSquaresFromPromotion[i]]

            return bonus + isolatedPawnPenaltyByCount[numIsolatedPawn]


        # endgameT 설정 다시하기
        whiteEndgameT = setEndgameT(board)
        blackEndgameT = setEndgameT(board)

        # Score based on number and type of pieces on board
        whiteMaterialScore = materialScore(board, color=True)
        blackMaterialScore = materialScore(board, color=False)
        # Score based on positions of pieces
        whitePieceSquareScore = evaluatePieceSquareTables(color=True, board=board, endgameT=whiteEndgameT)
        blackPieceSquareScore = evaluatePieceSquareTables(color=False, board=board, endgameT=blackEndgameT)
		# Encourage using own king to push enemy king to edge of board in winning endgame
        whiteMopUpScore = mopUpEval(color=True, board=board, enemyEndgameT=blackEndgameT, whiteMaterialScore=whiteMaterialScore, blackMaterialScore=blackMaterialScore)
        blackMopUpScore = mopUpEval(color=False, board=board, enemyEndgameT=whiteEndgameT, whiteMaterialScore=whiteMaterialScore, blackMaterialScore=blackMaterialScore)

        whitePawnScore = evaluatePawns(color=True, board=board)
        blackPawnScore = evaluatePawns(color=False, board=board)
        
        whiteEval = whiteMaterialScore + whitePieceSquareScore + whiteMopUpScore + whitePawnScore
        blackEval = blackMaterialScore + blackPieceSquareScore + blackMopUpScore + blackPawnScore

        color = board.turn

        if color == chess.WHITE:
            return whiteEval - blackEval
        else:
            return blackEval - whiteEval



