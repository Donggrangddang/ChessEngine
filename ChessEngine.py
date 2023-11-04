import ChessBoard
import numpy as np

'''
- 사용할 변수
    List state : 상태 List
    List action : 각각에 상태에 대한 Action List
    quality_value : 상태 행동 가치 쌍
- 구현할 함수
    상태가 List State안에 있는 지 확인하고 있으면 True를 반환하고 없다면 False를 반환하고 상태를 추가하는 함수

'''

class ChessEngine(ChessBoard):
    
    def __init__(self):
        self.quality_value = np.array((0, 162))
    
