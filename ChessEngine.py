import random
import time
import datetime
import json
import os

from tqdm import tqdm
import chess
import chess.pgn

'''
- 필요한 변수
	- self.state
	- self.action
	- self.quality_value : Q(s, a)
	- self.cumulative_weight : C(s, a)
	- pi[state_index] -> 최적 action
	- b[state_index] -> 각 action에 관한 array
    - b[state_index][action_index] -> 특정한 action에 관한 확률
	- G
	- W

- 필요한 함수
	- 에피소드 생성 함수
	- 1. state만나면 self.state에 추가하는 함수 (o)
	- 2. state에서의 legal_moves를 self.action에 추가하는 함수 (o)
	- 5. pi를 정하는 함수 (o)
	- 3. 어떤 list에서 state의 index값을 반환하는 함수 (안해도 될듯?)
	- 4. 임의의 소프트 정책을 만드는 함수 (o)
	- 6. 에피소드를 생성하는 함수
	- 7. 에피소드의 각 단계에 대한 루프를 돌리는 함수
	- 8. 최대가 되는 a가 여러 개일 경우 한가지 행동만 선택하도록 하는 함수
'''

class ChessEngine():
    
    def __init__(self):
        self.white = {}
        self.black = {}


    def judgement_end(self, board : str, turn : int) -> tuple[bool, bool] or tuple[6, 6]:
        """
        board의 현재 상황이 무승부인지, 체크 메이트인지, 끝나지 않았는지 확인한다.
        시간복잡도 : O(1)
        """

        if board.is_stalemate() == True or board.is_insufficient_material() == True or board.can_claim_draw == True:

            if turn % 2 == 0:
                return True, False
            else:
                return False, False
            
        elif board.is_checkmate() == True:

            if turn % 2 == 0:
                return True, True
            else:
                return False, True

        else:

            return (6, 6)


    def legal_move(self, board : str, movement : str) -> bool:
        """
        board에서 movement가 가능한 움직임인지 아닌지 판별한다.
        시간복잡도 : O(n)
        """

        move = chess.Move.from_uci(movement)

        if move in board.legal_moves:
            return True
        
        return False


    def move_agent(self, board : str, movement : str) -> tuple[str, int]:
        """
        board에 movement를 반영한다.
        agent가 학습을 할 때에만 사용하는 함수이다.(movement가 이미 검증된 함수)
        시간복잡도 : O(1)
        """

        board.push_san(movement)

        return board


    def move_player(self, board : str, movement : str, turn : int) -> tuple[bool, str, int]:
        """
        board에 movement를 반영한다.
        player가 play를 할 때만 사용한다.(movement가 검증되지 않음)
        시간복잡도 : O(n)
        """

        if self.legal_move(board, movement) == True:
            board.push_san(movement)
            turn += 1
            return True, board, turn
        else:
            return False, board, turn


    def evaluate(self, board, color):
    
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
            board_fen = board.fen().split(" ")[0]
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
                    if piece is not None and piece.symbol() == 'P' and piece.color == chess.WHITE:
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

        if color == True:
            return whiteEval - blackEval
        else:
            return blackEval - whiteEval


    def judgement_state(self, board : str, color : bool) -> bool:
        """
        특정 color의 state가 self.color안에 있는 지 확인하고 있으면 True를 반환하고 
        없으면 state_color에 state를 추가하고 False를 반환한다.
        시간복잡도 : O(n)
        """

        state = board

        if type(state) != str:
            state = state.fen()

        state = self.state_converter(state)

        if color == True: # 백

            if state in self.white:
                self.white[state][3] = self.generate_probability(len=len(action_list))
                return True
            else:
                action_list = self.legal_action(board)
                self.white[state] = [action_list, 
                                            [0 for i in range(len(action_list))], 
                                            [0 for i in range(len(action_list))], 
                                            self.generate_probability(len=len(action_list), index_pi=0, param=True), 
                                            [None]]
                return False
            
        else:

            if state in self.black:
                self.black[state][3] = self.generate_probability(len=len(action_list))
                return True
            else:
                action_list = self.legal_action(board)
                self.black[state] = [action_list,
                                            [0 for i in range(len(action_list))], 
                                            [0 for i in range(len(action_list))], 
                                            self.generate_probability(len=len(action_list), index_pi=0, param=True), 
                                            [None]]
                return False


    def judgement_action(self, state : str, action : str, color : bool) -> int:
        """
        특정 color에서의 state에서 action의 index값을 알아낸다.
        시간복잡도 : O(n)
        """

        if color == True: # 백

            return self.white[state][0].index(action)

        else:
            
            return self.black[state][0].index(action)


    def legal_action(self, board : str) -> list:
        """
        state에서 가능한 Action 반환한다.
        시간복잡도 : O(n)
        """

        legal_moves_raw = list(board.legal_moves)
        legal_moves = []

        for i in range(len(legal_moves_raw)):
            append_legal_move = str(legal_moves_raw[i]).replace('Move.from_uci(', '')
            append_legal_move = append_legal_move.replace(')', '')
            legal_moves.append(append_legal_move)

        return legal_moves


    def find_optimal_policy(self, state : str, color : bool) -> str:
        """
        특정한 color의 최적 정책(pi)을 찾아 대입한다.
        시간복잡도 : O(n)
        """

        if color == True: # 백이라면

            quality_value_list = [lambda i: self.white[state][2][i]]
            argmax_action_index = quality_value_list.index(max(quality_value_list))

            self.white[state][4] = self.white[state][0][argmax_action_index]
            return self.white[state][4]
        
        else:

            quality_value_list = [lambda i: self.black[state][2][i]]
            argmax_action_index = quality_value_list.index(max(quality_value_list))

            self.black[state][4] = self.black[state][0][argmax_action_index]
            return self.black[state][4]


    def generate_probability(self, len : int, index_pi : int, param : bool) -> list:
        """
        b의 확률을 구해준다.
        시간복잡도 : O(n)
        """

        epslion = 0.1

        if param:
            return [1 / len for i in range(len)]
        else:
            probabilty = [epslion / len for i in range(len)]
            probabilty[index_pi] += 1 - epslion
            return probabilty


    def state_converter(self, raw_state : str) -> str:
        """
        state를 맨 마지막 값을 뺀 상태로 반환시킴
        시간복잡도 :O(1)
        """

        dummy_state = raw_state.split(' ')

        state = " ".join(dummy_state[:4])

        return state


    def choose_action(self, state : str, color : bool) -> str:
        """
        b에 따른 확률로 state에서의 action을 골라준다.
        시간복잡도 : O(1)
        """

        if color == True:

            action = random.choices(self.white[state][0], weights = self.white[state][3], k=1)

            return action[0]

        else:

            action = random.choices(self.black[state][0], weights = self.black[state][3], k=1)

            return action[0]


    def calcV(self, state, color):

        V = 0

        if color == True:
            
            white_list = self.white[state]

            for i in range(white_list[0]):

                V += white_list[3][i] * white_list[2][i]

            return V

        else:

            black_list = self.black[state]

            for i in range(black_list[0]):

                V += black_list[3][i] * black_list[2][i]

            return V


    def learning(self, times=10 ** 8 + 1):

        if self.black == {} or self.white == {}:
            self.load_text_data(file_path_white='D:/database/data2_white.txt', file_path_black='D:/database/data2_black.txt')

        discount_rate = 0.9

        for time in range(times):

            state_list = []
            action_list = []
            reward_list = [None]
            T = float('inf')
            t = 0
            n = 1

            board = chess.Board()

            if self.judgement_state(board, color=True):
                action = self.choose_action(state=self.state_converter(board.fen()))

            state_list.append(self.state_converter(board.fen()))
            action_list.append(action)

            while t != r:
                
                if t < T:
                    # 행동 A_t를 취하고, 다음 보상과 상태를 R_t+1, S_t+1로 측정하고 저장
                    board.push_san(action)
                    self.judgement_state(board, color=(board.turn))
                    state_list.append(self.state_converter(board.fen()))
                    reward_list.append(self.evaluate(board, color=(not board.turn)))

                    if self.judgement_end(board, turn=t+1) != (6, 6):
                        T = t + 1
                    else:
                        action = self.choose_action(state=self.state_converter(board.fen()))
                        action_list.append(action)

                r = t - n + 1

                if r >= 0:

                    if t + 1 < T:

                        if (t + 1) % 2 == 0: # white

                            G = self.white[state_list[t + 1]][2][self.judgement_action(state=state_list[t + 1], action=action_list[t + 1], color=True)]

                        else:

                            G = self.black[state_list[t + 1]][2][self.judgement_action(state=state_list[t + 1], action=action_list[t + 1], color=False)]

                    for k in range(min(t + 1, T), r + 2):

                        if k == T:

                            G = reward_list[T]
                        
                        else:

                            V = self.calcV(state=state_list[k], color=(k % 2 == 0))
                            G = reward_list[k] + discount_rate * (discount_rate ** k + (1 - discount_rate ** k) * self.)


        



            
                


        
            
                    

            


    def save_as_txt_file(self, file_name : str):

        print('save_start')

        start = time.time()

        # white 파일 쓰기
        with open(f'D:/database/{file_name}_white.txt', "w", buffering=100*1024*1024) as white_file:
            for key, value in tqdm(self.white.items(), desc='white file writing'):
                white_file.write(f'{key}\t{value}\n')

        # black 파일 쓰기
        with open(f'D:/database/{file_name}_black.txt', "w", buffering=100*1024*1024) as black_file:
            for key, value in tqdm(self.black.items(), desc='black file writing'):
                black_file.write(f'{key}\t{value}\n')

        print('save_done')
        print(f'{time.time() - start}s')


    def load_text_data(self, file_path_white: str, file_path_black: str, chunk_size=10*1024*1024):
        print('load_start')

        start = time.time()
        remaining_text = ""  # 이전 청크에서 남은 텍스트

        def process_chunk(chunk, data_dict):
            nonlocal remaining_text
            chunk = remaining_text + chunk
            lines = chunk.split('\n')
            for i in range(len(lines) - 1):
                line = lines[i]
                if line:
                    key, value = line.strip().split('\t')
                    try:
                        data_dict[key] = eval(value)
                    except:
                        try:
                            data_dict[key] = eval(value + ']')
                        except:
                            data_dict[key] = eval(value + ']]')
            remaining_text = lines[-1]  # 마지막 줄은 다음 청크와 합쳐집니다.

        with open(file_path_white, 'r') as file:
            file_size = os.path.getsize(file_path_white)
            with tqdm(total=file_size, desc='white file loading', unit='B', unit_scale=True) as pbar:
                chunk = file.read(chunk_size)
                while chunk:
                    process_chunk(chunk, self.white)
                    pbar.update(len(chunk))
                    chunk = file.read(chunk_size)

        print(f'white done {time.time() - start}s')

        with open(file_path_black, 'r') as file:
            file_size = os.path.getsize(file_path_black)
            with tqdm(total=file_size, desc='black file loading', unit='B', unit_scale=True) as pbar:
                chunk = file.read(chunk_size)
                while chunk:
                    process_chunk(chunk, self.black)
                    pbar.update(len(chunk))
                    chunk = file.read(chunk_size)

        print(f'black done {time.time() - start}s')

        print('load_done')
        

    def playing(self):
    
        if self.black == {} or self.white == {}:
            self.load_text_data(file_path_white='D:/database/data1_white.txt', file_path_black='D:/database/data1_black.txt')

        player_color = input('white, black\t')
        board = chess.Board()

        pgn_list = chess.pgn.Game()
        if player_color:
            pgn_list.headers["White"] = input('Write Player Name\t')
            pgn_list.headers["Black"] = "AI"
        else:
            pgn_list.headers["Black"] = input("Write Player Name\t")
            pgn_list.headers["White"] = "AI"

        pgn_list.headers["Event"] = input('Write Event Name\t')
        pgn_list.headers["Date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        turn = 0

        if player_color == 'white': # 플레이어가 백을 잡았을 때

            while self.judgement_end(board, turn) == (6, 6):

                if turn % 2 == 0: # 백 차례라면

                    movement = input('enter UCI\t')

                    if movement == "exit":
                        break

                    try:
                        result_move_player = self.move_player(board, movement, turn)

                        if result_move_player[0] == True:
                            board = result_move_player[1]
                            turn = result_move_player[2]
                            if turn == 1:
                                node = pgn_list.add_variation(chess.Move.from_uci(movement))
                            else:
                                node = node.add_variation(chess.Move.from_uci(movement))
                            print(board)
                        else:
                            print('illegal_move')
                        
                    except:
                        print('error')
                        pass
                
                else: # 흑 차례라면
                    
                    state = self.state_converter(board.fen())
                    try:
                        movement = self.black[state][4][0]
                        if movement[0] == None: 
                            movement = self.choose_action(state, color=False)
                    except:
                        self.judgement_state(board, color=False)
                        movement = self.choose_action(state, color=False)
                    
                    result_move_agent = self.move_agent(board, movement, turn)
                    board = result_move_agent[0]
                    turn = result_move_agent[1]

                    node = node.add_variation(chess.Move.from_uci(movement))

                    print(movement)
                    print(board)

        elif player_color == 'black': # 플레이어가 흑을 잡았을 때

            while self.judgement_end(board, turn) == (6, 6):
    
                if turn % 2 == 1: # 흑 차례라면

                    try:

                        movement = input('enter UCI\t')

                        if movement == "exit":
                            break

                        result_move_player = self.move_player(board, movement, turn)

                        if result_move_player[0] == True:
                            board = result_move_player[1]
                            turn = result_move_player[2]
                            node = node.add_variation(chess.Move.from_uci(movement))

                            print(board)
                        else:
                            print('illegal_move')

                    except:
                        print('error')
                        pass
                
                else: # 백 차례라면
                    
                    state = self.state_converter(board.fen())
                    try:
                        movement = self.white[state][4][0]
                        if movement == None:
                            movement = self.choose_action(state, color=True)
                    except:
                        self.judgement_state(board, color=True)
                        movement = self.choose_action(state, color=True)
                    
                    result_move_agent = self.move_agent(board, movement, turn)
                    board = result_move_agent[0]
                    turn = result_move_agent[1]

                    if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(movement))
                    else:
                        node = node.add_variation(chess.Move.from_uci(movement))

                    print(movement)
                    print(board)

        else:
            print('error')
            
        print(pgn_list)
        self.save_pgn(pgn_list)


    def save_pgn(self, pgn_list):
        with open('D:/database/data1_pgn_list.txt', 'a') as file:
            file.write(str(pgn_list))


    def run(self):
        self.learning(times=50000)
        while True:
            self.playing()


if __name__ == '__main__':
    a = ChessEngine()
    a.run()
