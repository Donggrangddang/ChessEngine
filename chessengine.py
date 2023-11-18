import chess
import chess.pgn

class ChessEngine():

    def __init__(self):
        self.board = chess.Board()


    def getLegalMoves(self, board : str) -> list:
        """get lagal moves in board"""

        legal_moves = board.legal_moves
        return legal_moves


    def evaluate(self, board : str) -> int:
        """evaluate curr state's value"""

        def count_pieces(board : chess.Board, color : bool) -> int:

            board_fen = list(board.fen().split(' '))[0]
            piece_type = ['p', 'n', 'b', 'r', 'q']
            if color == True:
                for i in range(5):
                    piece_type[i] = piece_type[i].upper()

            count_pawn = board_fen.count(piece_type[0])
            count_knight = board_fen.count(piece_type[1])
            count_bishop = board_fen.count(piece_type[2])
            count_rook = board_fen.count(piece_type[3])
            count_queen = board_fen.count(piece_type[4])

            count_list = [
                count_pawn,
                count_knight,
                count_bishop,
                count_rook,
                count_queen
            ]

            return count_list
        
        def countMaterial(count_list : list) -> int:

            pawnValue = 100
            knightValue = 300
            bishopValue = 350
            rookValue = 500
            queenValue = 900

            material = 0
            material += count_list[0] * pawnValue
            material += count_list[1] * knightValue
            material += count_list[2] * bishopValue
            material += count_list[3] * rookValue
            material += count_list[4] * queenValue

            return material
        
        white_eval = countMaterial(count_pieces(board=board, color=True))
        black_eval = countMaterial(count_pieces(board=board, color=False))

        evaluation = white_eval - black_eval
        if board.turn == True: # white turn
            return evaluation
        else:
            return -evaluation


    def legalMovement(self, board : str) -> list:
        """
        state에서 가능한 Action 반환한다.
        시간복잡도 : O(n)
        """

        legal_moves_raw = list(board.legal_moves)
        legal_movements = []

        for i in range(len(legal_moves_raw)):
            append_legal_movement = str(legal_moves_raw[i]).replace('Move.from_uci(', '')
            append_legal_movement = append_legal_movement.replace(')', '')
            legal_movements.append(append_legal_movement)

        return legal_movements


    def search(self, board : str, depth : int, alpha : int, beta : int) -> int:

        if depth == 0:
            return self.evaluate(board)

        legal_movements = self.legalMovement(board)

        if len(legal_movements) == 0:
            if board.is_check() == True:
                return float("-inf")
            else:
                return 0

        for move in legal_movements:
            board = self.move(board, move)
            evaluation = -self.search(board, depth - 1, alpha, beta)
            board = self.unMakeMove(board, move)
            if evaluation >= beta:
                return beta
            alpha = max(alpha, evaluation)
        
        return alpha


    def find_best_move(self, board, depth):

        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        legal_movements = self.legalMovement(board)

        for move in legal_movements:
            board = self.move(board, move)
            evaluation = -self.search(board, depth - 1, -beta, -alpha)
            board = self.unMakeMove(board, move)

            if evaluation > alpha:
                alpha = evaluation
                best_move = move

        print(best_move)

        return best_move


    def testLegalMovement(self, board, depth):
        if depth == 0:
            return 1
        
        moves = self.legalMovement(board)
        numposition = 0

        for move in moves:
            board.push_san(move)
            numposition += self.testLegalMovement(board, depth - 1)
            board.pop()

        return numposition


    def run(self):
        '''board = chess.Board()
        game = chess.pgn.Game()
        turn = 0
        while True:
            movement = self.find_best_move(board, depth=4)
            board = self.move(board, movement)
            if turn == 0:
                node = game.add_variation(chess.Move.from_uci(movement))
            else:
                node = node.add_variation(chess.Move.from_uci(movement))

            turn += 1

            print(str(game))'''

        board = chess.Board('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - ')
        print(self.testLegalMovement(board, depth=1))
        print(self.testLegalMovement(board, depth=2))
        print(self.testLegalMovement(board, depth=3))
        print(self.testLegalMovement(board, depth=4))
        print(self.testLegalMovement(board, depth=5))



if __name__ == '__main__':
    a = ChessEngine()
    a.run()