import chess
import time

class ChessEngine2:

    def __init__(self):
        self.board = chess.Board()
        self.cutoff_count = 0
        self.eval_called = 0


    def eval(self):
        self.eval_called += 1
        if self.board.is_checkmate():
            if self.board.turn:
                return float('-inf')
            else:
                return float('inf')

        piece_value = [0, 100, 300, 320, 500, 900, 10000]
        pure_piece_score = 0

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                if piece.color == chess.WHITE:
                    pure_piece_score += piece_value[piece.piece_type]
                else:
                    pure_piece_score -= piece_value[piece.piece_type]
            
        return pure_piece_score


    def alphabeta_max(self, alpha, beta, depth, returnBestMove=False):
        if depth == 0:
            return self.eval()
        
        best_move = None

        for move in self.board.legal_moves:
            self.board.push(move)
            score = self.alphabeta_min(alpha, beta, depth - 1)
            self.board.pop()
            if score > alpha:
                alpha = score
                best_move = move
            if alpha >= beta:
                break

        if returnBestMove:
            return best_move
        return alpha

    def alphabeta_min(self, alpha, beta, depth, returnBestMove=False):
        if depth == 0:
            return self.eval()
        
        best_move = None

        for move in self.board.legal_moves:
            self.board.push(move)
            score = self.alphabeta_max(alpha, beta, depth - 1)
            self.board.pop()
            if score < beta:
                beta = score
                best_move = move
            if alpha >= beta:
                self.cutoff_count += 1
                break

        if returnBestMove:
            return best_move
        return beta
        
    def find_best_move(self, depth):

        best_move = None
        if self.board.turn:
            best_move = self.alphabeta_max(float('-inf'), float('inf'), depth, True)
        else:
            best_move = self.alphabeta_min(float('-inf'), float('inf'), depth, True)
        
        return best_move

    def run(self):
        self.board.set_fen('8/7p/3k4/2pn1pPP/1pB1pP2/1P6/3K4/8 w - - 2 42')
        start = time.time()
        print(f'Current Position moves: {self.board.legal_moves.count()}')
        print(f'Best move: {self.find_best_move(5)}')
        print(f'Time: {time.time() - start}')
        print(f'Eval called: {self.eval_called}')
        print(f'Cutoff count: {self.cutoff_count}')

if __name__ == "__main__":
    a = ChessEngine2()
    a.run()