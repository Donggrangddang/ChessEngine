import ChessBoard
import chess
import numpy as np

'''
- 필요한 변수
	- self.state
	- self.action
	- self.quality_value : Q(s, a)
	- self.cumulative_weight : C(s, a)
	- pi
	- b
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
        self.quality_value_white = np.array((0, 162))
        self.quality_value_black = np.array((0, 162))
        self.state_white = []
        self.state_black = []
        self.action_white = []
        self.action_black = []
        self.cumulaive_weight_white = []
        self.cumulaive_weight_black = []
        self.pi_white = np.empty()
        self.pi_black = np.empty()
        self.b_white = np.empty()
        self.b_black = np.empty()

    def judgementState(self, state, color):
        # @brief 특정 color의 state가 self.state_color안에 있는 지 확인하고 있으면 True와 index를 반환하고 없다면 False를 반환하고 상태를 추가함
        # @date 23/11/07
        # @return boolean, self.state.index(state) : 현재 상태의 self.state에서의 index값
        # @param self, state : 상태 값, boolean color : True = 백, False = 흑

        if color == True: # 백

            if state in self.state_white:
                return True, self.state_white.index(state)
            else:
                if state not in self.state_white:
                    self.state_white.append()
                return False, False
            
        else:

            if state in self.state_black:
                return True, self.state_black.index(state)
            else:
                if state not in self.state_black:
                    self.state_black.append()
                return False, False

    def addLegalAction(self, state, color):
        # @brief 특정한 color의 state에서 가능한 Action을 self.action_color에 추가함
        # @date 23/11/04
        # @return List legal_moves : 가능한 움직임 List
        # @param self, state : 상태 값, boolean color : True = 백, False = 흑

        if color == True:
        
            legal_moves_raw = list(state.legal_moves)
            legal_moves = []
            for i in range(len(legal_moves_raw)):
                append_legal_move = legal_moves_raw[i].replace('Move.from_uci(', '')
                append_legal_move = append_legal_move.replace(')', '')
                legal_moves.append(append_legal_move)

            legal_moves = self.transRawPosition(self, list=legal_moves)
            self.action_white.append(legal_moves)

            return legal_moves
        
        else:

            legal_moves_raw = list(state.legal_moves)
            legal_moves = []
            for i in range(len(legal_moves_raw)):
                append_legal_move = legal_moves_raw[i].replace('Move.from_uci(', '')
                append_legal_move = append_legal_move.replace(')', '')
                legal_moves.append(append_legal_move)

            legal_moves = self.transRawPosition(self, list=legal_moves)
            self.action_black.append(legal_moves)

            return legal_moves

    def transRawPosition(self, legal_moves):
        # @brief 체스 좌표를 숫자로 변환해줌
        # @date 23/11/07
        # @return None
        # @param self, legal_moves : 가능한 움직임

        for i in range(len(legal_moves)):

            position = list(legal_moves[i])

            for j in range(len(position)):

                _ = None
                dummy = position[j]

                if j % 2 == 0: # 영어
                    _.append(ord(dummy[j]) - 97)
                else: # 숫자
                    _.append(8 - dummy[j])
                
                position[i] = "".join(_)
            
            legal_moves[i] = position
        
        return None
        
    def findOptimalPolicy(self, color):
        # @brief 특정한 color의 최적 정책(pi)를 찾아줌
        # @date 23/11/07
        # @return None
        # @param self, boolean color

        if color == True: # 백이라면

            self.pi_white = np.argmax(self.quality_value_white, axis=1)
            return None
        
        else:

            self.pi_black = np.argmax(self.quality_value_black, axis=1)
            return None
        
    def generateRandomSoftPolicy(self, epsilon=0.1, param=True, color=True):
        # @brief 임의의 소프트 정책을 만들어줌
        # @date 23/11/04
        # @return None
        # @param self, epsilon : 입실론, param : True면 하고 False면 그냥 랜덤

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

        if color == True:

            for i in range(len(self.action_white[state_index])):
                self.b_white[state_index][i] = 1 / len(self.action_white[state_index])

            return 0

        else:

            for i in range(len(self.action_white[state_index])):
                self.b_white[state_index][i] = 1 / len(self.action_white[state_index])

            return 0

    def chooseAction(self, state_index, color):
        # @brief b에 따른 확률로 Action을 정함
        # @date 23/11/05
        # @return action : 취할 행동
        # @param self, state_index : 현재 상태의 index값

        if color == True:

            action = np.random.choice(self.action_white[state_index], 1, p=self.b_white[state_index])

            return action

        else:

            action = np.random.choice(self.action_white[state_index], 1, p=self.b_white[state_index])

            return action
        
    def generateEpisode(self):
        # @brief 에피소드를 생성함
        # @date 23/11/04
        # @return episode
        # @param self

        episode = []
        action_list = []
        state_list = []
        reward_list = []
        board = chess.Board()
        turn = 0

        while self.judgementEnd(board, turn) == None:

            judgement = self.judgementState(self, state=board)
            state_index = judgement[1]

            if judgement[0] == True: # 한번 겪었던 상황 -> 이에 대한 확률이 있다.
                action = self.chooseAction(judgement[1])
                board = self.move(action)[1]
                action_list.append(action)
                state_list.append(board)

            else: # 겪지 않았던 상황 -> 이에 대한 확률이 없다.
                self.addLegalAction(state=board)
                self.generateProbability(judgement[1])
                action = self.chooseAction(judgement[1])
                board = self.move(action)[1]
                action_list.append(action)
                state_list.append(board)












