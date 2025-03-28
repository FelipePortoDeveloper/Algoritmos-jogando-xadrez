import chess

class JogoXadrez:

    def __init__(self):
        self.board = chess.Board()
        self.rodando = True
        self.pausado = False

    def movimento(self, movimento: chess.Move):
        if movimento in self.board.legal_moves:
            self.board.push(movimento)

    def fim_de_jogo(self):
        return self.board.is_game_over()
    
    def movimentos_permitidos(self):
        return list(self.board.legal_moves)
    
    def reinicia_jogo(self):
        self.board.reset()
        self.pausado = False