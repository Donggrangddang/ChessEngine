import numpy as np
board = np.zeros((8, 8))
board[1] = board[6] = 1
for i in range(2, 5):
    board [0][9-i] = board[0][i-2] = board[7][9-i] = board[7][i-2] = 6-i
board[0][3] = board[7][3] = 5
board[0][4] = board[7][4] = 6
board[0] *= -1
board[1] *= -1

def king_move(board, turn):
    king_curr_positon = np.where(board == 6 * turn) # [x, y]로 저장됨
    king_curr_positon_x = king_curr_positon[0]
    king_curr_positon_y = king_curr_positon[1]
    king_next_position = np.empty((0, 2))

    for i in range(-1, 2): # king이 갈 수 있는 칸 지정
        for j in range(-1, 2):
            king_next_position = np.append(king_next_position, np.array([king_curr_positon_x + i, king_curr_positon_y + j]), axis=0)

    print(king_next_position)

    for next_position in king_next_position: # -인 칸 제거
        king_next_position = np.delete(king_next_position, np.where(next_position))

    return king_next_position

print(king_move(board=board, turn=-1))

def knight_move(board, turn):
    knight_curr_position = np.where(board == 2 * turn)
    knight_curr_position_x = knight_curr_position[0]
    knight_curr_position_y = knight_curr_position[1]
    knight_next_position = np.empty((0,2))



'''
보드에서 기물 숫자 * turn의 좌표를 찾기
킹이 갈 수 있는 칸을 np를 이용해 표현
ex) 킹 위치 = [3, 4] -> 갈 수 있는 위치 = [[3, 5], [3, 3], ...]
    만약 좌표가 음수값이라면 -> 없앤다
    return 갈 수 있는 위치
'''
        