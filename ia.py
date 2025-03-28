import chess
import json
import numpy as np

class XadrezIA:

    def __init__(self, profundidade = 2, cor = chess.BLACK):

        self.profundidade = profundidade
        self.cor = cor

        with open("posicoes_ideais_w.json", "r") as w:
            self.posicoes_ideais_w = {k: np.array(v) for k, v in json.load(w).items()}

        with open("posicoes_ideais_b.json", "r") as b:
            self.posicoes_ideais_b = {k: np.array(v) for k, v in json.load(b).items()}

        if cor == chess.BLACK:
            self.posicoes_ideais = self.posicoes_ideais_b
        else:
            self.posicoes_ideais = self.posicoes_ideais_w

    def estagio_jogo(self, tabuleiro:chess.Board):

        # retorna True se for late game e False se for early game

        rainhas = [p for p in tabuleiro.piece_map().values() if p.piece_type == chess.QUEEN]

        if len(rainhas) == 0:
            return True
        elif len(rainhas) == 1:
            cor = rainhas[0].color
            menores = [p for p in tabuleiro.piece_map().values() if p.piece_type in [chess.KNIGHT, chess.BISHOP] and p.color == cor]

            if len(menores) <= 1:
                return True
            else:
                return False
        else:
            return False
            
    def avaliar_tabuleiro(self, tabuleiro:chess.Board, movimento: chess.Move = None):
        
        valores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}
        pontos = 0
        centro = [chess.D4, chess.E4, chess.D5, chess.E5]

        # Avaliando captura:

        if movimento != None:
            if tabuleiro.is_legal(movimento):

                if tabuleiro.is_capture(movimento):
                    peca_capturada = tabuleiro.piece_at(movimento.to_square)
                    peca_atacante = tabuleiro.piece_at(movimento.from_square)

                    if peca_atacante and peca_atacante.color == self.cor and peca_capturada:

                        simbolo_a = peca_atacante.symbol().upper()
                        simbolo_c = peca_capturada.symbol().upper()

                        pontos += valores[simbolo_c] - valores[simbolo_a]
                    
                if tabuleiro.gives_check(movimento):
                    pontos += 50

                if tabuleiro.is_castling(movimento):
                    pontos += 40

                # Simular o movimento
            
                tabuleiro.push(movimento)

        # Avaliando posição

        for quadrado, peca in tabuleiro.piece_map().items():

            if peca.color == self.cor:
                linha, coluna = divmod(quadrado, 8)
                simbolo = peca.symbol().upper()

                if simbolo == "K":
                    pontos = pontos + self.posicoes_ideais[simbolo + "_l"][linha][coluna] if self.estagio_jogo(tabuleiro) else pontos + self.posicoes_ideais[simbolo + "_e"][linha][coluna]
                else:
                    pontos += self.posicoes_ideais[simbolo][linha][coluna]
        

        # Avaliando cheque

        if tabuleiro.is_check():
            pontos += 100 if tabuleiro.turn != self.cor else - 100

        # Avaliando cheque-mate

        if tabuleiro.is_checkmate():
            pontos += 1000 if tabuleiro.turn != self.cor else - 1000

        # Avalinado empate  

        if tabuleiro.is_stalemate() or tabuleiro.is_insufficient_material():
            pontos -= 900

        # Terminando avaliação
        if movimento is not None and tabuleiro.is_legal(movimento):
            tabuleiro.pop()

        return pontos
    
    def minimax(self, tabuleiro:chess.Board, profundidade: int, maximizando: bool, alpha: float, beta: float, movimento_anterior: chess.Move = None):

        avaliacao_atual = self.avaliar_tabuleiro(tabuleiro, movimento_anterior)

        if profundidade == 0 or tabuleiro.is_game_over():
            return avaliacao_atual
        
        if maximizando:
            melhor_valor = -float("inf")

            for movimento in list(tabuleiro.legal_moves):
                tabuleiro.push(movimento)
                valor = self.minimax(tabuleiro, profundidade - 1, False, alpha, beta, movimento)
                tabuleiro.pop()
                melhor_valor = max(melhor_valor, valor)
                alpha = max(alpha, melhor_valor)
                if beta <= alpha:
                    break
            return melhor_valor
        else:
            melhor_valor = float("inf")

            for movimento in list(tabuleiro.legal_moves):
                tabuleiro.push(movimento)
                valor = self.minimax(tabuleiro, profundidade - 1, True, alpha, beta, movimento)
                tabuleiro.pop()
                melhor_valor = min(melhor_valor, valor)
                beta = min(beta, melhor_valor)
                if beta <= alpha:
                    break
            return melhor_valor

    def obter_melhor_movimento(self, tabuleiro:chess.Board):
        melhor = -float("inf")
        melhor_movimento = None

        for movimento in tabuleiro.legal_moves:
            
            tabuleiro.push(movimento)
            valor = self.minimax(tabuleiro, self.profundidade - 1, False, -float("inf"), float("inf"), movimento)
            tabuleiro.pop()

            if valor > melhor:
                melhor = valor
                melhor_movimento = movimento

        return melhor_movimento