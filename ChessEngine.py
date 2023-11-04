import ChessBoard
import numpy as np

'''
- 사용할 변수
    List state : 상태 List, State는 
    List action : 각각에 상태에 대한 Action List, Action은 str 4자리로 표현됨
    quality_value : 상태 행동 가치 쌍
- 구현할 함수
    현재 State를 구해주는 함수 -> ChessBoard.move 함수로 해결 가능
    상태가 List State안에 있는 지 확인하고 있으면 True를 반환하고 없다면 False를 반환하고 상태를 추가하는 함수
    quality_value에 만난 State와 거기서 가능한 Action을 

'''

class ChessEngine(ChessBoard):
    
    def __init__(self):
        self.quality_value = np.array((0, 162))
        self.state = []
        self.action = []

    def addLegalAction(self):
        # @brief 새로 추가된 state에서 가능한 Action을 self.action에 추가함
        # @date 23/11/04
        # @return List legal_moves : 가능한 움직임 List
        # @param self
        
        state = self.state[-1]
        legal_moves_raw = list(state.legal_moves)
        legal_moves = []
        for i in range(len(legal_moves_raw)):
            append_legal_move = legal_moves_raw[i].replace('Move.from_uci(', '')
            append_legal_move = append_legal_move.replace(')', '')
            legal_moves.append(append_legal_move)

        legal_moves = self.transSanPosition(self, list=legal_moves)

        return legal_moves

    def transSanPosition(self, legal_moves):
        # @brief 체스 좌표를 숫자로 변환해줌
        # @date 23/11/04
        # @return List legal_moves : 체스 좌표를 숫자로 변환한 List
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
        
        return legal_moves

    def judgementState(self, state):
        # @brief state가 self.state안에 있는 지 확인하고 있으면 True와 index를 반환하고 없다면 False를 반환하고 상태를 추가함
        # @date 23/11/04
        # @return boolean, self.state.index(state) : 현재 상태의 self.state에서의 index값
        # @param self, state : 현재 상태 값

        if state in self.state:
            return True, self.state.index(state)
        else: 
            self.state.append()
            return False
        
    def selectActionB(self, state):
        # @brief 정책 b를 따르는 현재 상태에서 취할 행동을 구함 
        # @date 23/11/04
        # @return boolean, self.state.index(state) : 현재 상태의 self.state에서의 index값
        # @param self

        if type(self.judgementState(self, state)) == tuple: # 한번 만난 State일 경우
            action_list = self.action[self.judgementState[1]]
            quality_value_list = self.quality_value[self.judgementState[1]]


