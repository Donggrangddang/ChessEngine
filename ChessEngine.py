from ChessBoard import ChessBoard
import chess
import chess.pgn
import random

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

class ChessEngine(ChessBoard):
    
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

    def judgementState(self, state, color):
        # @brief 특정 color의 state가 self.state_color안에 있는 지 확인하고 있으면 True와 index를 반환하고 없다면 False를 반환하고 상태를 추가함
        # @date 23/11/07
        # @return boolean, self.state.index(state) : 현재 상태의 self.state에서의 index값
        # @param self, state : 상태 값, boolean color : True = 백, False = 흑

        # print('judgementState')

        if type(state) != str:
            state = state.fen()

        dummy_state = state.split(' ')

        state = " ".join(dummy_state[0:4])

        if color == True: # 백

            if state in self.state_white:
                return True, self.state_white.index(state)
            else:
                self.state_white.append(state)
                return False, self.state_white.index(state)
            
        else:

            if state in self.state_black:
                return True, self.state_black.index(state)
            else:
                self.state_black.append(state)
                return False, self.state_black.index(state)

    def judgementAction(self, state_index, action, color=True):
        # @brief 특정 color에서의 state에서 action의 index값을 알아냄
        # @date 23/11/09
        # @return 
        # @param self, state_index : state의 index값, color : 흑, 백

        # print('judgementAction')

        if color == True: # 백

            return self.action_white[state_index].index(action)

        else:
            
            return self.action_black[state_index].index(action)

    def addLegalAction(self, state, color=True):
        # @brief 특정한 color의 state에서 가능한 Action을 self.action_color에 추가함
        # @date 23/11/04
        # @return List legal_moves : 가능한 움직임 List
        # @param self, state : 상태 값, boolean color : True = 백, False = 흑

        # print('addLegalAction')

        legal_moves_raw = list(state.legal_moves)
        legal_moves = []
        for i in range(len(legal_moves_raw)):
            append_legal_move = str(legal_moves_raw[i]).replace('Move.from_uci(', '')
            append_legal_move = append_legal_move.replace(')', '')
            legal_moves.append(append_legal_move)

        # legal_moves = self.transRawPosition(legal_moves)

        if color == True:

            self.action_white.append(legal_moves)

            return legal_moves
        
        else:

            self.action_black.append(legal_moves)

            return legal_moves

    def transRawPosition(self, legal_moves):
        # @brief 체스 좌표를 숫자로 변환해줌
        # @date 23/11/07
        # @return legal_moves
        # @param self, legal_moves : 가능한 움직임

        # print('transRawPosition')

        for i in range(len(legal_moves)): # 가능한 움직임의 개수 만큼 반복

            position = list(legal_moves[i]) # 글자 쪼개기
            _ = []

            for j in range(len(position)): # 글자의 수 만큼 반복

                dummy = position[j]

                if j == 0 or j == 2: # 영어
                    _.append(str(ord(dummy) - 97))
                elif j == 1 or j == 3: # 숫자
                    _.append(str(8 - int(dummy)))
                
            raw_position= int("".join(_))
            legal_moves[i] = raw_position
        
        return legal_moves
        
    def findOptimalPolicy(self, state_index, color):
        # @brief 특정한 color의 최적 정책(pi)를 찾아줌
        # @date 23/11/09
        # @return None
        # @param self, boolean color

        # print('findOptimalPolicy')

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
        
    def generateRandomSoftPolicy(self, epsilon=0.1, param=True, color=True):
        # @brief 임의의 소프트 정책을 만들어줌
        # @date 23/11/04
        # @return None
        # @param self, epsilon : 입실론, param : True면 하고 False면 그냥 랜덤

        # print('generateRandomSoftPolicy')

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

    def generateProbability(self, state_index, color):
        # @brief b에 따른 확률을 정함(초기 b)
        # @date 23/11/06
        # @return 0
        # @param self, state_index : 현재 상태의 index값

        # print('generateProbablility')

        if color == True:

            self.b_white.append([0 for i in range(len(self.action_white[state_index]))])

            for i in range(len(self.action_white[state_index])):
                self.b_white[state_index][i] = 1 / len(self.action_white[state_index])

            return 0

        else:

            self.b_black.append([0 for i in range(len(self.action_black[state_index]))])

            for i in range(len(self.action_black[state_index])):
                self.b_black[state_index][i] = 1 / len(self.action_black[state_index])

            return 0

    def chooseAction(self, state_index, color):
        # @brief b에 따른 확률로 Action을 정함
        # @date 23/11/05
        # @return action : 취할 행동
        # @param self, state_index : 현재 상태의 index값

        # print('chooseAction')

        if color == True:

            action = random.choices(self.action_white[state_index], weights = self.b_white[state_index])

            return action[0]

        else:

            action = random.choices(self.action_black[state_index], weights = self.b_black[state_index])

            return action[0]
        
    def generateEpisode(self):
        # @brief 에피소드를 생성함
        # @date 23/11/08
        # @return episode : episode_white + episode_black
        # @param self

        # print('generateEpisode')

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

        pgn_list = chess.pgn.Game()

        while self.judgementEnd(board, turn) == (6, 6):

            judgement = self.judgementState(state=board, color=(turn % 2 == 0))
            state_index = judgement[1]

            if turn % 2 == 0: # 백이라면

                color = True

                if judgement[0] == True: # 한번 겪었던 상황 -> 이에 대한 확률이 있다.
                    action = self.chooseAction(state_index, color)
                    return_move = self.move(board, action, turn)
                    board = return_move[1]
                    turn = return_move[2]
                    action_list_white.append(action)
                    state_list_white.append(board.fen())
                    reward_list_white.append(0)
                    if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(action))
                    else:
                        node = node.add_variation(chess.Move.from_uci(action))

                else: # 겪지 않았던 상황 -> 이에 대한 확률이 없다.
                    self.addLegalAction(state=board, color=color)
                    self.generateProbability(state_index, color)
                    action = self.chooseAction(state_index, color)
                    return_move = self.move(board, action, turn)
                    board = return_move[1]
                    turn = return_move[2]
                    action_list_white.append(action)
                    state_list_white.append(board.fen())
                    reward_list_white.append(self.returnRewardWhite(self.judgementEnd(board, turn)))
                    if turn == 1:
                        node = pgn_list.add_variation(chess.Move.from_uci(action))
                    else:
                        node = node.add_variation(chess.Move.from_uci(action))

            else: # 흑이라면

                color = False
                
                if judgement[0] == True: # 한번 겪었던 상황 -> 이에 대한 확률이 있다.
                    action = self.chooseAction(state_index, color)
                    return_move = self.move(board, action, turn)
                    board = return_move[1]
                    turn = return_move[2]
                    action_list_black.append(action)
                    state_list_black.append(board.fen())
                    reward_list_black.append(0)
                    node = node.add_variation(chess.Move.from_uci(action))

                else: # 겪지 않았던 상황 -> 이에 대한 확률이 없다.
                    self.addLegalAction(state=board, color=color)
                    self.generateProbability(state_index, color)
                    action = self.chooseAction(state_index, color)
                    return_move = self.move(board, action, turn)
                    board = return_move[1]
                    turn = return_move[2]
                    action_list_black.append(action)
                    state_list_black.append(board.fen())
                    reward_list_black.append(self.returnRewardBlack(self.judgementEnd(board, turn)))
                    node = node.add_variation(chess.Move.from_uci(action))
                    
        print(pgn_list)

        episode_white.append(state_list_white)
        episode_white.append(action_list_white)
        episode_white.append(reward_list_white)
        episode_black.append(state_list_black)
        episode_black.append(action_list_black)
        episode_black.append(reward_list_black)
        episode = episode_white + episode_black

        return episode, turn

    def run(self, times=10 ** 7):
        return_generate_episode = self.generateEpisode()

        # print('run')

        episode = return_generate_episode[0]
        turn = return_generate_episode[1]

        state_list_white = episode[0]
        action_list_white = episode[1]
        reward_list_white = episode[2]
        state_list_black = episode[3]
        action_list_black = episode[4]
        reward_list_black = episode[5]
        
        G_white = 0
        G_black = 0
        W_white = 1
        W_black = 1
        discount_rate = 0.9

        for i in range(times):

            if times % 10000 == 0:
                print(i)

            if turn % 2 == 0: # 백 차례에서 끝남

                for t in range((turn // 2) - 1, -1, -1): # 흑

                    G_black = discount_rate * G_black + reward_list_black[t + 1]
                    state_index = self.judgementState(state=state_list_black[t], color=False)[1]
                    action_index = self.judgementAction(state_index=state_index, action=action_list_black[t], color=False)

                    self.cumulative_weight_black[state_index][action_index] += W_black
                    self.quality_value_black[state_index][action_index] += (W_black / self.cumulative_weight_black[state_index][action_index]) * (G_black - self.quality_value_black[state_index][action_index])
                    optimal_action = self.findOptimalPolicy(state_index, color=False)

                    if action_list_black[t] != optimal_action:
                        break
                    else:
                        W_black *= 1 / self.b_black[state_index][action_index]

                for t in range(((turn - 1) // 2) - 1, -1, -1): # 백

                    G_white = discount_rate * G_white + reward_list_white[t + 1]
                    state_index = self.judgementState(state=state_list_white[t], color=False)[1]
                    action_index = self.judgementAction(state_index=state_index, action=action_list_white[t], color=False)

                    self.cumulative_weight_white[state_index][action_index] += W_white
                    self.quality_value_white[state_index][action_index] += (W_white / self.cumulative_weight_white[state_index][action_index]) * (G_white - self.quality_value_white[state_index][action_index])
                    optimal_action = self.findOptimalPolicy(state_index, color=False)

                    if action_list_white[t] != optimal_action:
                        break
                    else:
                        W_white *= 1 / self.b_white[state_index][action_index]
    
            else: # 흑 차례에서 끝남
                
                for t in range(((turn - 1) // 2) - 1, -1, -1): # 흑

                    G_black = discount_rate * G_black + reward_list_black[t + 1]
                    state_index = self.judgementState(state=state_list_black[t], color=False)[1]
                    action_index = self.judgementAction(state_index=state_index, action=action_list_black[t], color=False)

                    self.cumulative_weight_black[state_index][action_index] += W_black
                    self.quality_value_black[state_index][action_index] += (W_black / self.cumulative_weight_black[state_index][action_index]) * (G_black - self.quality_value_black[state_index][action_index])
                    optimal_action = self.findOptimalPolicy(state_index, color=False)

                    if action_list_black[t] != optimal_action:
                        break
                    else:
                        W_black *= 1 / self.b_black[state_index][action_index]

                for t in range((turn // 2) - 1, -1, -1): # 백

                    G_white = discount_rate * G_white + reward_list_white[t + 1]
                    state_index = self.judgementState(state=state_list_white[t], color=False)[1]
                    action_index = self.judgementAction(state_index=state_index, action=action_list_white[t], color=False)

                    self.cumulative_weight_white[state_index][action_index] += W_white
                    self.quality_value_white[state_index][action_index] += (W_white / self.cumulative_weight_white[state_index][action_index]) * (G_white - self.quality_value_white[state_index][action_index])
                    optimal_action = self.findOptimalPolicy(state_index, color=False)

                    if action_list_white[t] != optimal_action:
                        break
                    else:
                        W_white *= 1 / self.b_white[state_index][action_index]

    def saveAsTxtFile(self):
        f = open(f'summerize_{self}', "w+")
        f.write('quality_value_white')
        f.write(self.quality_value_white)
        f.write('state_white')
        f.write(self.state_white)
        f.write('action_white')
        f.write(self.action_white)
        f.write('cumulative_weight_white')
        f.write(self.cumulative_weight_white)
        f.write('pi_white')
        f.write(self.pi_white)
        f.write('b_white')
        f.write(self.b_white)
        f.write('quality_value_black')
        f.write(self.quality_value_black)
        f.write('state_black')
        f.write(self.state_black)
        f.write('action_black')
        f.write(self.action_black)
        f.write('cumulative_weight_black')
        f.write(self.cumulative_weight_black)
        f.write('pi_black')
        f.write(self.pi_black)
        f.write('b_black')
        f.write(self.b_black)
        f.close()

    def visualize(self):
        self.run()
        self.saveAsTxtFile()

a = ChessEngine()

a.visualize()














