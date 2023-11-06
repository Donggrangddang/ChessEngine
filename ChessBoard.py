import chess

class ChessBoard:

    def __init__(self):
        self.board = chess.Board()
        self.turn = 0

    def transSanPosition(self, x, y):
        # @brief x, y로 입력되는 좌표를 체스 좌표로 변환해줌.
        # @date 23/11/03 
        # @return "".join([trans_x, trans_y]) : 변환된 체스 좌표 값.
        # @param x : 변환하려는 x 좌표값, y : 변환하려는 y 좌표값.

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
        # @brief stalemate인지 checkmate인지 판별해줌
        # @date 23/11/03 
        # @return White or Black, Stalemate or Checkmate
        # @param self

        if board.is_stalemate() == True:

            if self.turn % 2 == 0:
                return True, False
            else:
                return False, False

        elif board.is_checkmate() == True:

            if self.turn % 2 == 0:
                return True, True
            else:
                return False, True

        else:
            return None

    def legalMove(self, position):
        # @brief 가능한 움직임인지 아닌지 판별해줌
        # @date 23/11/03 
        # @return boolean : 가능한 움직임 여부
        # @param self, position : 포지션

        move = chess.Move.from_uci(position)

        if move in self.board.legal_moves:
            return True
        
        return False

    def move(self, raw_position):
        # @brief board에 움직임을 반영
        # @date 23/11/03 
        # @return boolean : 가능한 움직임인지 여부, board : 변경된 보드
        # @param self, String raw_position : 처음 좌표값 + 움직일 좌표값 or 바로 UCI 좌표값

        if raw_position.isdecimal(): # raw_position이 숫자로 입력되면
            x = int(raw_position[0])
            y = int(raw_position[1])
            next_x = int(raw_position[2])
            next_y = int(raw_position[3])
            position = "".join([self.transSanPosition(x=x, y=y), self.transSanPosition(x=next_x, y=next_y)])
        
        else:
            position = raw_position

        print(self.turn % 2)

        judgement_end = self.judgementEnd(self.board, self.turn)

        if judgement_end == None:

            if self.legalMove(position) == True:
                self.board.push_san(position)
                print(f'{position} success')
                self.turn += 1
                board = self.board
                return True, board
            else:
                print(f'{position} failed')
                board = self.board
                return False, board

        else:

            if judgement_end[0] == True:
                if judgement_end[1] == False:
                    print('stalemate')
                else:
                    print('흑 승')

            else:
                if judgement_end[1] == False:
                    print('stalemate')
                else:
                    print('백 승')

    def returnRewardWhite(tuple):
        # @brief 보상을 부여해줌
        # @date 23/11/04
        # @return Reward
        # @param tuple : judgementEnd 결과, move 결과

        if type(tuple[1]) == bool: # judgementEnd 결과
            if tuple[0] == True: # 백
                if tuple[1] == False: # stalemate
                    return -0.2
                else: # checkmate
                    return -1
            else:
                if tuple[1] == False: # stalemate
                    return -0.2
                else:
                    return 1
        else: # move 결과
            if tuple[0] == True:
                return -0.01
            else:
                return -0.05
    
    def returnRewardBlack(tuple):
        # @brief 흑에게 보상을 부여해줌
        # @date 23/11/04
        # @return Reward
        # @param tuple : judgement 결과, move 결과

        if type(tuple[1]) == bool: # judgement 결과
            if tuple[0] == True: # 백
                if tuple[1] == False: # stalemate
                    return -0.2
                else: # checkmate
                    return 1
            else:
                if tuple[1] == False: # stalemate
                    return -0.2
                else:
                    return -1
        else: # move 결과
            if tuple[0] == True:
                return -0.01
            else:
                return -0.05
            
    def visualize(self, raw_position):
        self.move(raw_position)
        print(self.board)
        return self.board

a = ChessBoard()

while True:
    a.visualize(input())
