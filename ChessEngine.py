import ChessBoard
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
        self.quality_value = np.array((0, 162))
        self.state = []
        self.action = []
        self.cumulaive_weight = []
        self.pi = np.empty()
        self.b = np.empty()

    def judgementState(self, state):
        # @brief state가 self.state안에 있는 지 확인하고 있으면 True와 index를 반환하고 없다면 False를 반환하고 상태를 추가함
        # @date 23/11/04
        # @return boolean, self.state.index(state) : 현재 상태의 self.state에서의 index값
        # @param self, state : 상태 값

        if state in self.state:
            return True, self.state.index(state)
        else: 
            self.state.append()
            return False

    def addLegalAction(self, state):
        # @brief state에서 가능한 Action을 self.action에 추가함
        # @date 23/11/04
        # @return List legal_moves : 가능한 움직임 List
        # @param self, state : 상태 값
        
        legal_moves_raw = list(state.legal_moves)
        legal_moves = []
        for i in range(len(legal_moves_raw)):
            append_legal_move = legal_moves_raw[i].replace('Move.from_uci(', '')
            append_legal_move = append_legal_move.replace(')', '')
            legal_moves.append(append_legal_move)

        legal_moves = self.transRawPosition(self, list=legal_moves)
        self.action.append(legal_moves)

        return legal_moves

    def transRawPosition(self, legal_moves):
        # @brief 체스 좌표를 숫자로 변환해줌
        # @date 23/11/04
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
        
    def findOptimalPolicy(self):
        # @brief 최적 정책(pi)를 찾아줌
        # @date 23/11/04
        # @return None
        # @param self

        self.pi = np.argmax(self.quality_value, axis = 1)

        return None
    
    def generateRandomSoftPolicy(self, epsilon=0.1):
        # @brief 임의의 소프트 정책을 만들어줌
        # @date 23/11/04
        # @return None
        # @param self

        for i in range(len(self.action)):
            for j in range(len(self.action[i])):
                if self.pi[i] == self.action[i].index(self.action[i][j]):
                    self.b[i][j] = 1 - epsilon + (1 / len(self.action[i]))
                else:
                    self.b[i][j] = 1 / len(self.action[i])

        return None

    def generateEpisode(self):
        


