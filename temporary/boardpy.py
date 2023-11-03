import chess

board = chess.Board()
#보드 세팅

position = [x_position, y_position]

move = chess.Move.from_uci("".join(position))

board.legal_moves

chess.Move.from_uci("e2e3") in board.legal_moves
#legal move 판정

board.push_san("e2e4")
board.push_san("e7e5")
board.push_san("f1c4")
board.push_san("b8c6")
board.push_san("d1h5")
board.push_san("g8f6")
board.push_san("h5f7")
#체크메이트

def judgement():
    if board.is_stalemate() == "True":

        return 0
        
    if board.is_checkmate() == "True":
        
        return 0

board #보드 불러오기