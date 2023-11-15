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


    def move_agent(self, board : str, movement : str, turn : int) -> tuple[str, int]:
        """
        board에 movement를 반영한다.
        agent가 학습을 할 때에만 사용하는 함수이다.(movement가 이미 검증된 함수)
        시간복잡도 : O(1)
        """

        board.push_san(movement)
        turn += 1

        return board, turn


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


    def return_reward_white(self, result_judgement_end : tuple[bool, bool]) -> float:
        """
        백에게 보상을 부여해준다.
        시간복잡도 : O(1)
        """
        color = result_judgement_end[0]
        win_or_draw = result_judgement_end[1]

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


    def return_reward_black(self, result_judgement_end : tuple[bool, bool]) -> float:
        """
        흑에게 보상을 부여해준다.
        시간복잡도 : O(1)
        """

        color = result_judgement_end[0]
        win_or_draw = result_judgement_end[1]

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


    def judgement_state(self, state : str, color : bool) -> bool:
        """
        특정 color의 state가 self.color안에 있는 지 확인하고 있으면 True를 반환하고 
        없으면 state_color에 state를 추가하고 False를 반환한다.
        시간복잡도 : O(n)
        """

        board = state

        if type(state) != str:
            state = state.fen()

        state = self.state_converter(state)

        if color == True: # 백

            if state in self.white:
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

        epslion = 0.5

        if param:
            return [1 / len for i in range(len)]
        else:
            probabilty = [epslion / len for i in range(len)]
            probabilty[index_pi] += 1 - epslion
            return probabilty


    def state_converter(self, state : str) -> str:
        """
        state를 맨 마지막 값을 뺀 상태로 반환시킴
        시간복잡도 :O(1)
        """

        dummy_state = state.split(' ')

        state = " ".join(dummy_state[:5])

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


    def generate_episode(self) -> tuple[dict, dict, list, list, int]:
        """
        b에 따른 에피소드를 생성한다
        시간복잡도 : O(n ** 2)
        """

        episode_white = {}
        episode_black = {}
        state_list_white = []
        state_list_black = []
        board = chess.Board()
        turn = 0

        # pgn_list = chess.pgn.Game() # PGN

        while self.judgement_end(board, turn) == (6, 6):

            judgement = self.judgement_state(state=board, color=(turn % 2 == 0))

            if turn % 2 == 0: # 백이라면

                color = True
                state = self.state_converter(board.fen())

                state_list_white.append(state)
                action = self.choose_action(state, color)
                return_move_agent = self.move_agent(board, action, turn)
                board = return_move_agent[0]
                turn = return_move_agent[1]

                if state in episode_white:
                    pass
                else:
                    episode_white[state] = [action, self.return_reward_white(self.judgement_end(board, turn))]

            else: # 흑이라면

                color = False
                state = self.state_converter(board.fen())

                state_list_black.append(state)
                action = self.choose_action(state, color)
                return_move_agent = self.move_agent(board, action, turn)
                board = return_move_agent[0]
                turn = return_move_agent[1]

                if state in episode_black:
                    pass
                else:
                    episode_black[state] = [action, self.return_reward_black(self.judgement_end(board, turn))]
                # node = node.add_variation(chess.Move.from_uci(action)) # PGN
                    
        # print(pgn_list) # PGN

        if episode_black[state_list_black[-1]][1] == 1:
            episode_white[state_list_white[-1]][1] = -1
            
        elif episode_black[state_list_black[-1]][1] == -0.2:
            episode_white[state_list_white[-1]][1] = -0.2
        
        elif episode_white[state_list_white[-1]][1] == 1:
            episode_black[state_list_black[-1]][1] = -1

        elif episode_white[state_list_white[-1]][1] == -0.2:
            episode_black[state_list_black[-1]][1] = -0.2

        return episode_white, episode_black, state_list_white, state_list_black, turn


    def learning(self, times=10 ** 8 + 1):

        if self.black == {} or self.white == {}:
            self.load_text_data(file_path_white='D:/database/data1_white.txt', file_path_black='D:/database/data1_black.txt')

        discount_rate = 0.9
        
        start = time.time()

        for i in range(times):

            if i % 100 == 0:
                print(f'{i}\t{time.time() - start}')
                self.save_as_txt_file('data1')
                start = time.time()

            return_generate_episode = self.generate_episode()

            G_white = 0
            G_black = 0
            W_white = 1
            W_black = 1

            episode_white = return_generate_episode[0]
            episode_black = return_generate_episode[1]
            state_list_white = return_generate_episode[2]
            state_list_black = return_generate_episode[3]
            turn = return_generate_episode[4]

            for t in range((turn // 2) - 1, -1, -1): # 흑

                state = state_list_black[t]
                action = episode_black[state][0]

                G_black = discount_rate * G_black + episode_black[state][1]
                action_index = self.judgement_action(state, action, color=False)

                self.black[state][1][action_index] += W_black
                self.black[state][2][action_index] += (W_black / self.black[state][1][action_index]) * (G_black - self.black[state][2][action_index])
                optimal_action = self.find_optimal_policy(state, color=False)

                if episode_black[state][0] != optimal_action:
                    break
                else:
                    W_black *= 1 / self.black[state][3][action_index]

            for t in range((turn // 2) - 1, -1, -1): # 백

                state = state_list_white[t]
                action = episode_white[state][0]

                G_white = discount_rate * G_white + episode_white[state][1]
                action_index = self.judgement_action(state, action, color=True)

                self.white[state][1][action_index] += W_white
                self.white[state][2][action_index] += (W_white / self.white[state][1][action_index]) * (G_white - self.white[state][2][action_index])
                optimal_action = self.find_optimal_policy(state, color=True)

                if episode_white[state][0] != optimal_action:
                    break
                else:
                    W_white *= 1 / self.white[state][3][action_index]


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


    def load_text_data(self, file_path_white: str, file_path_black: str, chunk_size=100*1024*1024):
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

        player_color = bool(input('white = True, black = False\t'))
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

        if player_color: # 플레이어가 백을 잡았을 때

            while self.judgement_end(board, turn) == (6, 6):

                if turn % 2 == 0: # 백 차례라면

                    movement = input('enter UCI\t')

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
                
                else: # 흑 차례라면
                    
                    state = self.state_converter(board.fen())
                    try:
                        movement = self.black[state][4][0]
                        if movement[0] == None: 
                            movement = self.choose_action(state, color=False)
                    except:
                        self.judgement_state(state, color=False)
                        movement = self.choose_action(state, color=False)
                    
                    result_move_agent = self.move_agent(board, movement, turn)
                    board = result_move_agent[0]
                    turn = result_move_agent[1]

                    node = node.add_variation(chess.Move.from_uci(movement))

                    print(movement)
                    print(board)

        else: # 플레이어가 흑을 잡았을 때

            while self.judgement_end(board, turn) == (6, 6):
    
                if turn % 2 == 1: # 흑 차례라면

                    movement = input('enter UCI\t')

                    result_move_player = self.move_player(board, movement, turn)

                    if result_move_player[0] == True:
                        board = result_move_player[1]
                        turn = result_move_player[2]
                        node = node.add_variation(chess.Move.from_uci(movement))

                        print(board)
                    else:
                        print('illegal_move')
                
                else: # 백 차례라면
                    
                    state = self.state_converter(board.fen())
                    try:
                        movement = self.white[state][4][0]
                        if movement == None:
                            movement = self.choose_action(state, color=True)
                    except:
                        self.judgement_state(state, color=True)
                        movement = self.choose_action(state, color=True)
                    
                    result_move_player = self.move_player(board, movement, turn)
                    board = result_move_player[0]
                    turn = result_move_player[1]

                    if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(movement))
                    else:
                        node = node.add_variation(chess.Move.from_uci(movement))

                    print(movement)
                    print(board)

        print(pgn_list)


    def visualize(self):
        self.load_text_data(file_path_white='D:/database/data1_white.txt', file_path_black='D:/database/data1_black.txt')
        self.save_as_txt_file('data1')

a = ChessEngine()

a.visualize()
