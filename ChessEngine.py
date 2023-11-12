import random
import time

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
        self.quality_value_white = []
        self.quality_value_black = []
        self.state_white = []
        self.state_black = []
        self.action_white = []
        self.action_black = []
        self.cumulative_weight_white = []
        self.cumulative_weight_black = []
        self.pi_white = []
        self.pi_black = []
        self.b_white = []
        self.b_black = []


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


    def judgement_state(self, state : str, color : bool) -> tuple[bool, int]:
        """
        특정 color의 state가 self.state_color안에 있는 지 확인하고 있으면 True와 index를 반환하고 없다면 상태를 추가하고 False와 index를 반환한다.
        시간복잡도 : O(n)
        """


        if type(state) != str:
            state = state.fen()

        dummy_state = state.split(' ')

        state = " ".join(dummy_state[:5])

        if color == True: # 백

            if state in self.state_white:
                return True, self.state_white.index(state)
            else:
                self.quality_value_white.append([])
                self.cumulative_weight_white.append([])
                self.pi_white.append(0)
                self.state_white.append(state)
                return False, self.state_white.index(state)
            
        else:

            if state in self.state_black:
                return True, self.state_black.index(state)
            else:
                self.quality_value_black.append([])
                self.cumulative_weight_black.append([])
                self.pi_black.append(0)
                self.state_black.append(state)
                return False, self.state_black.index(state)


    def judgement_action(self, state_index : int, action : str, color : bool) -> int:
        """
        특정 color에서의 state에서 action의 index값을 알아낸다.
        시간복잡도 : O(n)
        """

        if color == True: # 백

            return self.action_white[state_index].index(action)

        else:
            
            return self.action_black[state_index].index(action)


    def add_legal_action(self, state : str, color : bool) -> list:
        """
        특정한 color의 state에서 가능한 Action을 self.action_color에 추가한다.
        특정한 color의 state에서 가능한 ACtion의 개수만큼 c와 q에도 추가한다.
        시간복잡도 : O(n)
        """

        legal_moves_raw = list(state.legal_moves)
        legal_moves = []

        state_index = self.judgement_state(state=state, color=color)[1]

        for i in range(len(legal_moves_raw)):
            append_legal_move = str(legal_moves_raw[i]).replace('Move.from_uci(', '')
            append_legal_move = append_legal_move.replace(')', '')
            legal_moves.append(append_legal_move)

        if color == True:

            for i in range(len(legal_moves)):
                self.quality_value_white[state_index].append(0)
                self.cumulative_weight_white[state_index].append(0)

            self.action_white.append(legal_moves)

            return legal_moves
        
        else:
            
            for i in range(len(legal_moves)):
                self.quality_value_black[state_index].append(0)
                self.cumulative_weight_black[state_index].append(0)

            self.action_black.append(legal_moves)

            return legal_moves


    def find_optimal_policy(self, state_index : int, color : bool) -> list:
        """
        특정한 color의 최적 정책(pi)을 찾아준다.
        시간복잡도 : O(n)
        """

        if color == True: # 백이라면

            action_list = lambda i: self.quality_value_white[state_index][i]
            argmax_action_index = max(range(len(self.quality_value_white[state_index])), key=action_list)

            self.pi_white[state_index] = argmax_action_index
            return self.pi_white[state_index]
        
        else:

            action_list = lambda i: self.quality_value_black[state_index][i]
            argmax_action_index = max(range(len(self.quality_value_black[state_index])), key=action_list)

            self.pi_black[state_index] = argmax_action_index
            return self.pi_black[state_index]


    def generate_random_softpolicy(self, epsilon : int, param : bool, color : bool) -> None:
        """
        임의의 소프트 정책을 만들어준다.
        시간복잡도 : O(n ** 2)
        """

        if color == True:

            if param:
                for i in range(len(self.action_white)):
                    for j in range(len(self.action_white[i])):
                        if self.pi_white[i] == self.action_white[i].index(self.action_white[i][j]):
                            self.b_white[i][j] = 1 - epsilon + epsilon * (1 / len(self.action_white[i]))
                        else:
                            self.b_white[i][j] = epsilon / len(self.action_white[i])

            else:
                for i in range(len(self.action_white)):
                    for j in range(len(self.action_white[i])):
                        self.b_white[i][j] = 1 / len(self.action_white[i])

            return None
        
        else:

            if param:
                for i in range(len(self.action_black)):
                    for j in range(len(self.action_black[i])):
                        if self.pi_black[i] == self.action_black[i].index(self.action_black[i][j]):
                            self.b_black[i][j] = 1 - epsilon + epsilon * (1 / len(self.action_black[i]))
                        else:
                            self.b_black[i][j] = epsilon / len(self.action_black[i])

            else:
                for i in range(len(self.action_black)):
                    for j in range(len(self.action_black[i])):
                        self.b_black[i][j] = 1 / len(self.action_black[i])

            return None


    def generate_probability(self, state_index : int, color : bool) -> None:
        """
        state_index의 state에서의 self.b에서의 action을 취할 확률을 계산해준다.
        시간복잡도 : O(n)
        """

        if color == True:

            self.b_white.append([0 for i in range(len(self.action_white[state_index]))])

            for i in range(len(self.action_white[state_index])):
                self.b_white[state_index][i] = 1 / len(self.action_white[state_index])

            return None

        else:

            self.b_black.append([0 for i in range(len(self.action_black[state_index]))])

            for i in range(len(self.action_black[state_index])):
                self.b_black[state_index][i] = 1 / len(self.action_black[state_index])

            return None


    def choose_action(self, state_index : int, color : bool) -> str:
        """
        b에 따른 확률로 state에서의 action을 골라준다.
        시간복잡도 : O(n)
        """

        if color == True:

            action = random.choices(self.action_white[state_index], weights = self.b_white[state_index])

            return action[0]

        else:

            action = random.choices(self.action_black[state_index], weights = self.b_black[state_index])

            return action[0]


    def generate_episode(self) -> tuple[list, int]:
        """
        b에 따른 에피소드를 생성한다
        시간복잡도 : O(n ** 2)
        """

        episode_white = []
        episode_black = []
        action_list_white = []
        action_list_black = []
        state_list_white = []
        state_list_black = []
        reward_list_white = [0]
        reward_list_black = [0]
        board = chess.Board()
        turn = 0

        # pgn_list = chess.pgn.Game() # PGN

        while self.judgement_end(board, turn) == (6, 6):

            judgement = self.judgement_state(state=board, color=(turn % 2 == 0))
            state_index = judgement[1]

            if turn % 2 == 0: # 백이라면

                color = True

                if judgement[0] == True: # 한번 겪었던 상황 -> 이에 대한 확률이 있다.
                    state_list_white.append(board.fen())
                    action = self.choose_action(state_index, color)
                    return_move_agent = self.move_agent(board, action, turn)
                    board = return_move_agent[0]
                    turn = return_move_agent[1]
                    action_list_white.append(action)

                    if board in state_list_white:
                        reward_list_white.append(0)
                    else:
                        reward_list_white.append(self.return_reward_white(self.judgement_end(board, turn)))
                    """if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(action))
                    else:
                        node = node.add_variation(chess.Move.from_uci(action))""" # PGN

                else: # 겪지 않았던 상황 -> 이에 대한 확률이 없다.
                    state_list_white.append(board.fen())
                    self.add_legal_action(board, color)
                    self.generate_probability(state_index, color)
                    action = self.choose_action(state_index, color)
                    return_move_agent = self.move_agent(board, action, turn)
                    board = return_move_agent[0]
                    turn = return_move_agent[1]
                    action_list_white.append(action)
                    reward_list_white.append(self.return_reward_white(self.judgement_end(board, turn)))
                    """if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(action))
                    else:
                        node = node.add_variation(chess.Move.from_uci(action))""" # PGN

            else: # 흑이라면

                color = False
                
                if judgement[0] == True: # 한번 겪었던 상황 -> 이에 대한 확률이 있다.
                    state_list_black.append(board.fen())
                    action = self.choose_action(state_index, color)
                    return_move_agent = self.move_agent(board, action, turn)
                    board = return_move_agent[0]
                    turn = return_move_agent[1]
                    action_list_black.append(action)

                    if board in state_list_black:
                        reward_list_black.append(0)
                    else:
                        reward_list_black.append(self.return_reward_black(self.judgement_end(board, turn)))
                    # node = node.add_variation(chess.Move.from_uci(action)) # PGN

                else: # 겪지 않았던 상황 -> 이에 대한 확률이 없다.
                    state_list_black.append(board.fen())
                    self.add_legal_action(board, color)
                    self.generate_probability(state_index, color)
                    action = self.choose_action(state_index, color)
                    return_move_agent = self.move_agent(board, action, turn)
                    board = return_move_agent[0]
                    turn = return_move_agent[1]
                    action_list_black.append(action)
                    reward_list_black.append(self.return_reward_black(self.judgement_end(board, turn)))
                    # node = node.add_variation(chess.Move.from_uci(action)) # PGN
                    
        # print(pgn_list) # PGN

        if reward_list_black[-1] == 1:
            reward_list_white[-1] = -1

        elif reward_list_black[-1] == -0.2:
            reward_list_white[-1] = -0.2
        
        elif reward_list_white[-1] == 1:
            reward_list_black[-1] = -1

        elif reward_list_white[-1] == -0.2:
            reward_list_black[-1] = -0.2


        episode_white.append(state_list_white)
        episode_white.append(action_list_white)
        episode_white.append(reward_list_white)
        episode_black.append(state_list_black)
        episode_black.append(action_list_black)
        episode_black.append(reward_list_black)
        episode = episode_white + episode_black

        return episode, turn


    def run(self, times=500):

        # print('run')

        start_real = time.time()

        episode_time = 0
        evaluate_time = 0

        G_white = 0
        G_black = 0
        W_white = 1
        W_black = 1
        discount_rate = 0.9

        for i in range(times):

            asdf_time = 0

            start = time.time()

            return_generate_episode = self.generate_episode()

            end_episode = time.time()

            episode = return_generate_episode[0]
            turn = return_generate_episode[1]

            state_list_white = episode[0]
            action_list_white = episode[1]
            reward_list_white = episode[2]
            state_list_black = episode[3]
            action_list_black = episode[4]
            reward_list_black = episode[5]

            if turn % 2 == 0: # 백 차례에서 끝남

                for t in range((turn // 2) - 1, -1, -1): # 흑

                    G_black = discount_rate * G_black + reward_list_black[t + 1]
                    result_judgement_state = self.judgement_state(state=state_list_black[t], color=False)
                    state_index = result_judgement_state[1]
                    action_index = self.judgement_action(state_index, action=action_list_black[t], color=False)

                    self.cumulative_weight_black[state_index][action_index] += W_black
                    self.quality_value_black[state_index][action_index] += (W_black / self.cumulative_weight_black[state_index][action_index]) * (G_black - self.quality_value_black[state_index][action_index])
                    optimal_action = self.find_optimal_policy(state_index, color=False)

                    if action_list_black[t] != optimal_action:
                        break
                    else:
                        asdf_time += 1
                        W_black *= 1 / self.b_black[state_index][action_index]

                for t in range(((turn) // 2) - 1, -1, -1): # 백

                    G_white = discount_rate * G_white + reward_list_white[t + 1]
                    result_judgement_state = self.judgement_state(state=state_list_white[t], color=True)
                    state_index = result_judgement_state[1]
                    action_index = self.judgement_action(state_index, action=action_list_white[t], color=True)

                    self.cumulative_weight_white[state_index][action_index] += W_white
                    self.quality_value_white[state_index][action_index] += (W_white / self.cumulative_weight_white[state_index][action_index]) * (G_white - self.quality_value_white[state_index][action_index])
                    optimal_action = self.find_optimal_policy(state_index, color=True)

                    if action_list_white[t] != optimal_action:
                        break
                    else:
                        asdf_time += 1
                        W_white *= 1 / self.b_white[state_index][action_index]
    
            else: # 흑 차례에서 끝남
                
                for t in range(((turn - 1) // 2) - 1, -1, -1): # 흑

                    G_black = discount_rate * G_black + reward_list_black[t + 1]
                    result_judgement_state = self.judgement_state(state=state_list_black[t], color=False)
                    state_index = result_judgement_state[1]
                    action_index = self.judgement_action(state_index, action=action_list_black[t], color=False)

                    self.cumulative_weight_black[state_index][action_index] += W_black
                    self.quality_value_black[state_index][action_index] += (W_black / self.cumulative_weight_black[state_index][action_index]) * (G_black - self.quality_value_black[state_index][action_index])
                    optimal_action = self.find_optimal_policy(state_index, color=False)

                    if action_list_black[t] != optimal_action:
                        break
                    else:
                        asdf_time += 1
                        W_black *= 1 / self.b_black[state_index][action_index]

                for t in range(((turn - 1) // 2) - 1, -1, -1): # 백

                    G_white = discount_rate * G_white + reward_list_white[t + 1]
                    result_judgement_state = self.judgement_state(state=state_list_white[t], color=True)
                    state_index = result_judgement_state[1]
                    action_index = self.judgement_action(state_index, action=action_list_white[t], color=True)

                    self.cumulative_weight_white[state_index][action_index] += W_white
                    self.quality_value_white[state_index][action_index] += (W_white / self.cumulative_weight_white[state_index][action_index]) * (G_white - self.quality_value_white[state_index][action_index])
                    optimal_action = self.find_optimal_policy(state_index, color=True)

                    if action_list_white[t] != optimal_action:
                        break
                    else:
                        asdf_time += 1
                        W_white *= 1 / self.b_white[state_index][action_index]

            print(f'{i}\t{time.time() - start}s\t{end_episode - start}s\t{time.time() - end_episode}s\t{asdf_time}')
            episode_time += end_episode - start
            evaluate_time += time.time() - end_episode
        print(f'{times}\t{time.time() - start_real}s')


    def saveAsTxtFile(self):
        f = open(f'C:/Codes/datebase/data2', "w+")
        f.write('quality_value_white\n')
        f.write(str(self.quality_value_white) + '\n')
        f.write('state_white\n')
        f.write(str(self.state_white) + '\n')
        f.write('action_white\n')
        f.write(str(self.action_white) + '\n')
        f.write('cumulative_weight_white\n')
        f.write(str(self.cumulative_weight_white) + '\n')
        f.write('pi_white\n')
        f.write(str(self.pi_white) + '\n')
        f.write('b_white\n')
        f.write(str(self.b_white) + '\n')
        f.write('quality_value_black\n')
        f.write(str(self.quality_value_black) + '\n')
        f.write('state_black\n')
        f.write(str(self.state_black) + '\n')
        f.write('action_black\n')
        f.write(str(self.action_black) + '\n')
        f.write('cumulative_weight_black\n')
        f.write(str(self.cumulative_weight_black) + '\n')
        f.write('pi_black\n')
        f.write(str(self.pi_black) + '\n')
        f.write('b_black\n')
        f.write(str(self.b_black) + '\n')
        f.close()

    def visualize(self):
        self.run()
        self.saveAsTxtFile()

    def debugging(self):
        start = time.time()
        board = chess.Board()

        for i in range(10 * 8):
            self.judgement_end(board, i)

        print(f'{time.time() - start}s')

a = ChessEngine()

a.visualize()














