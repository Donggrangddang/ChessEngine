import chess

def trans_position(x,y):
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

def judgement(board):
    if board.is_stalemate() == True:
        
        return "Stalemate"

    elif board.is_checkmate() == True:

        return "Checkmate"

def legal_move(board, position):

    if chess.Move.from_uci(position) in board.legal_moves:
        return True
    
    return False

def move(board, raw_position):

    raw_position = raw_position.split(",")

    x = int(raw_position[0])
    y = int(raw_position[1])
    next_x = int(raw_position[2])
    next_y = int(raw_position[3])
    position = "".join([trans_position(x, y), trans_position(next_x, next_y)])




def run():

    board = chess.Board()


    if legal_move(board, position) == True:
        board.push_san(position)
        print(f'{position} success')

    else:
        print(f'{position} failed')

    print(board)
        

if __name__ == '__main__':
    run() 