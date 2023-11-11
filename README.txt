White : True
Black : False

Stalemate : False
Checkmate : True

turn :  짝수 = 백차례
        홀수 = 흑차례

MainLogic
        상태가 많음 -> 최초접촉을 했을 때 상태 리스트에 상태와 이 상태에서 가능한 Action을 추가
        다음번에 이 상태를 만났을 때, 그때부터 추정 시작

        상태 행동 쌍을 표현해야함 -> 어떻게?
        상태는 String으로 나오게 된다. 그래서 위에 언급한 바와 같이 

- ver1.0 -> 하나의 AI (백과 흑을 나누지 않음.)

- ver2.0 -> 두개의 AI (백과 흑을 나눈다.)
        - ver2.1 -> 말을 잡는 것에 대해 따로 reward를 주지 않는다.
                - ver2.11 -> state를 fen의 6번째를 뺀걸로 나타냄
                - ver2.12 -> state를 fen의 5번째와 6번째를 뺀걸로 나타냄
        - ver2.2 -> 말을 잡는 것에 대해 reward를 준다. (구현 아직 x)
                - ver2.21 -> state를 fen의 6번째를 뺀걸로 나타냄
                - ver2.22 -> state를 fen의 5번째와 6번째를 뺀걸로 나타냄
                