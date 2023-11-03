import chess

class ChessBoard:

    def __init__(self):
        self.board = chess.Board
        self.turn = 0

    def transPosition(x, y):
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

    def judgement(self):
        # @brief stalemate인지 checkmate인지 판별해줌
        # @date 23/11/03 
        # @return White or Black, Stalemate or Checkmate
        # @param self

        if self.board.is_stalemate() == True:

            if self.turn % 2 == 0:
                return True, False
            else:
                return False, False

        elif self.board.is_checkmate() == True:

            if self.turn % 2 == 0:
                return True, True
            else:
                return False, True

    def legalMove(self, position):
        # @brief 가능한 움직임인지 아닌지 판별해줌
        # @date 23/11/03 
        # @return boolean : 가능한 움직임 여부
        # @param self, position : 포지션

        if chess.Move.from_uci(position) in self.board.legalMoves:
            return True
        
        return False

    def move(self, raw_position):
        # @brief board에 움직임을 반영
        # @date 23/11/03 
        # @return boolean : 가능한 움직임인지 여부, board : 변경된 보드
        # @param self, String raw_position : 처음 좌표값 + 움직일 좌표값

        raw_position = raw_position.split(",")

        x = int(raw_position[0])
        y = int(raw_position[1])
        next_x = int(raw_position[2])
        next_y = int(raw_position[3])
        position = "".join([self.transPosition(self, x=x, y=y), self.transPosition(self, x=next_x, y=next_y)])
        if self.legalMove(position=position) == True:
            self.board.push_san(position)
            print(f'{position} success')
            return True, self.board
        else:
            print(f'{position} failed')
            return False, self.board

    def returnReward(list):
        # @brief 보상을 줌
        # @date 23/11/03 
        # @return float Reward 
        # @param list : move함수의 반환값

        if list[0] == True:
            return 0
        else:
            return -0.1
            
        
            