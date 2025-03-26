import chess
import random
import json

class XadrezIA:

    def __init__(self, profundidade = 2, cor = chess.BLACK):

        self.profundidade = profundidade
        self.cor = cor

        with open("posicoes_ideais_w.json", "r") as w:
            self.posicoes_ideais_w = json.load(w)

        with open("posicoes_ideais_b.json", "r") as b:
            self.posicoes_ideais_b = json.load(b)

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
            
    def avaliar_tabuleiro(self, tabuleiro:chess.Board, movimento: chess.Move):
        
        valores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}
        pontos = 0

        # Avaliando captura:

        if tabuleiro.is_capture(movimento):
            peca_capturada = tabuleiro.piece_at(movimento.to_square).symbol().upper()
            pontos = pontos + valores[peca_capturada] if tabuleiro.turn == self.cor else pontos - valores[peca_capturada] 
            print(pontos)

        # Simular o movimento

        tabuleiro.push(movimento)

        # Avaliando posição

        for quadrado in chess.SQUARES:

            peca = tabuleiro.piece_at(quadrado)

            linha, coluna = divmod(quadrado, 8)

            if peca:

                simbolo = peca.symbol().upper()
                cor = peca.color

                
                if cor == self.cor:

                    # Verificar momento do jogo

                    if simbolo == "K":
                        pontos = pontos + self.posicoes_ideais[simbolo + "_l"][linha][coluna] if self.estagio_jogo(tabuleiro) else pontos + self.posicoes_ideais[simbolo + "_e"][linha][coluna]
                    else:
                        pontos += self.posicoes_ideais[simbolo][linha][coluna]

        # Avaliando cheque

        if tabuleiro.is_check():
            pontos += 100 if tabuleiro.turn != self.cor else - 100
            print(pontos)

        # Avaliando cheque-mate

        if tabuleiro.is_checkmate():
            pontos += 1000 if tabuleiro.turn != self.cor else - 1000

        # Avalinado empate  

        if tabuleiro.is_stalemate() or tabuleiro.is_insufficient_material():
            pontos -= 900


        # Terminando avaliação

        tabuleiro.pop()
        return pontos
        
board = chess.Board()

ia = XadrezIA(2, chess.BLACK)

board.push(chess.Move(chess.E2, chess.E4))

pontos = ia.avaliar_tabuleiro(board, chess.Move(chess.E7, chess.E5))

board.push(chess.Move(chess.E7, chess.E5))

print(board.piece_at(chess.E8))

