import chess

class ChessBoard:

    def __init__(self):
        self.own_board = chess.Board()
        self.turn = 0

    def transSanPosition(self, x, y):
        # @brief RawPosition을 SanPosition으로 변환
        # @date 23/11/03 
        # @return "".join([trans_x, trans_y]) : 변환된 체스 좌표 값.
        # @param x : 변환하려는 x 좌표값, y : 변환하려는 y 좌표값.

        # print('transSanPosition')

        if x == 0:
            trans_x = "a"
        elif  x == 1:
            trans_x = "b"
        elif  x == 2:
            trans_x = "c"
        elif  x == 3:
            trans_x = "d"
        elif  x == 4:
            trans_x = "e"
        elif  x == 5:
            trans_x = "f"
        elif  x == 6:
            trans_x = "g"
        elif  x == 7:
            trans_x = "h"

        trans_y = str(8 - y)

        return "".join([trans_x, trans_y])

    def judgementEnd(self, board, turn):
        # @brief 체크메이트, 스테일메이트, 기물 부족, 75수 규칙, 5수반복인지 아닌지 판별
        # @date 23/11/03 
        # @return White or Black, Stalemate or Checkmate
        # @param self

        # print('judgementEnd')

        if board.is_stalemate() == True or board.is_insufficient_material() == True or board.is_fivefold_repetition() == True or board.is_seventyfive_moves():

            if turn % 2 == 0:
                return True, False
            else:
                return False, False
            
        elif board.is_checkmate() == True:

            if turn % 2 == 0:
                return True, True
            else:
                return False, True

        return (6, 6)

    def legalMove(self, board, movement):
        # @brief board에서 movement가 가능한 움직임인지 아닌지 판별해줌
        # @date 23/11/03 
        # @return boolean : 가능한 움직임 여부
        # @param self, position : 포지션

        # print('legalMove')

        move = chess.Move.from_uci(movement)

        if move in board.legal_moves:
            return True
        
        return False

    def move(self, board, movement, turn):
        # @brief own_board에 움직임을 반영
        # @date 23/11/03 
        # @return boolean : 가능한 움직임인지 여부, own_board : 변경된 보드
        # @param self, String raw_movement : 처음 좌표값 + 움직일 좌표값 or 바로 UCI 좌표값

        # print('move')

        '''if type(movement) == int: # raw_movement이 숫자로 입력되면
            raw_movement_list = list(str(movement))

            while len(raw_movement_list) < 4:
                raw_movement_list = ['0'] + raw_movement_list

            x = int(raw_movement_list[0])
            y = int(raw_movement_list[1])
            next_x = int(raw_movement_list[2])
            next_y = int(raw_movement_list[3])
            movement = "".join([self.transSanPosition(x=x, y=y), self.transSanPosition(x=next_x, y=next_y)])
        
        else:
            movement = raw_movement'''

        if self.legalMove(board, movement) == True:
            board.push_san(movement)
            # print(f'{movement}\tsuccess')
            turn += 1
            return True, board, turn
        else:
            # print(f'{movement}\tfailed')
            print(board.fen())
            return False, board, turn
        
    def returnRewardWhite(self, result_judgementEnd):
        # @brief 보상을 부여해줌
        # @date 23/11/04
        # @return Reward
        # @param result_judgementEnd : judgementEnd 결과

        # print('returnRewardWhite')

        color = result_judgementEnd[0]
        win_or_draw = result_judgementEnd[1]

        if color == True: # 백

            if win_or_draw == False: # stalemate
                return -0.2
            else: # checkmate
                return -1
            
        elif color == False: # 흑

            if win_or_draw == False: # stalemate
                return -0.2
            else:
                return 1
            
        else:

            return -0.01
    
    def returnRewardBlack(self, result_judgementEnd):
        # @brief 흑에게 보상을 부여해줌
        # @date 23/11/04
        # @return Reward
        # @param result_judgementEnd : judgement 결과, move 결과

        # print('returnRewardBlack')

        color = result_judgementEnd[0]
        win_or_draw = result_judgementEnd[1]

        if color == True: # 백

            if win_or_draw == False: # stalemate
                return -0.2
            else: # checkmate
                return 1
            
        elif color == False: # 흑

            if win_or_draw == False: # stalemate
                return -0.2
            else:
                return -1
            
        else:

            return -0.01
            
    def visualize(self, raw_movement):
        self.move(raw_movement)
        print(self.turn % 2)
        print(self.own_board)
        return self.own_board