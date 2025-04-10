import chess
import json
import numpy as np
import chess.polyglot

class XadrezIA:

    def __init__(self, profundidade = 2, cor = chess.BLACK):

        self.profundidade = profundidade
        self.cor = cor
        self.valores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}

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

    def avaliar_movimento(self, tabuleiro:chess.Board, movimento: chess.Move):
        pontos = 0

        if tabuleiro.is_capture(movimento):
            peca_capturada = tabuleiro.piece_at(movimento.to_square)
            peca_atacante = tabuleiro.piece_at(movimento.from_square)

            if peca_atacante and peca_atacante.color == self.cor and peca_capturada:

                simbolo_a = peca_atacante.symbol().upper()
                simbolo_c = peca_capturada.symbol().upper()

                pontos += self.valores[simbolo_c] - self.valores[simbolo_a]
                    
        if tabuleiro.gives_check(movimento):
            pontos += 50

        if tabuleiro.is_castling(movimento):
            pontos += 40

        return pontos

    def ordenar_movimentos(self, tabuleiro:chess.Board, movimentos: list):
        movimentos_avaliados = []

        for movimento in movimentos:
            pontos = self.avaliar_movimento(tabuleiro, movimento)
            movimentos_avaliados.append((movimento, pontos))

        movimentos_avaliados.sort(key=lambda x: x[1], reverse=True)

        return [move for move, _ in movimentos_avaliados]

    def avaliar_tabuleiro(self, tabuleiro:chess.Board, movimento: chess.Move = None):
        
        pontos = 0
        centro = [chess.D4, chess.E4, chess.D5, chess.E5]

        # Avaliando captura:

        if movimento != None:
            if tabuleiro.is_legal(movimento):

                pontos += self.avaliar_movimento(tabuleiro, movimento)

                # Simular o movimento
            
                tabuleiro.push(movimento)

        # Avaliando posição

        for quadrado, peca in tabuleiro.piece_map().items():
                                
            linha, coluna = divmod(quadrado, 8)
            simbolo = peca.symbol().upper()
            valor_peca = self.valores[simbolo]

            if simbolo == "K":
                bonus = self.posicoes_ideais[simbolo + "_l"][linha][coluna] if self.estagio_jogo(tabuleiro) else self.posicoes_ideais[simbolo + "_e"][linha][coluna]
            else:
                bonus = self.posicoes_ideais[simbolo][linha][coluna]

            if peca.color == self.cor:
                if not tabuleiro.is_attacked_by(self.cor, quadrado):
                    bonus -= 10
                if tabuleiro.is_attacked_by(not self.cor, quadrado):
                    bonus -= 10

            if simbolo == "P":

                if peca.color == self.cor:
                    if quadrado in centro:
                        bonus += 50

            if peca.color == self.cor:
                pontos += valor_peca + bonus
            else:
                pontos -= valor_peca + bonus

        # Terminando avaliação de movimento
        if movimento is not None and tabuleiro.is_legal(movimento):
            tabuleiro.pop()
                
        # Avaliando cheque

        if tabuleiro.is_check():
            pontos += 100 if tabuleiro.turn != self.cor else - 100

        # Avaliando cheque-mate

        if tabuleiro.is_checkmate():
            pontos += 1000 if tabuleiro.turn != self.cor else - 1000

        # Avalinado empate  

        if tabuleiro.is_stalemate() or tabuleiro.is_insufficient_material():
            pontos -= 900

        # Avaliando repetição

        if tabuleiro.is_repetition(2):
            pontos -= 200

        # Avaliando Mobilidade

        mobilidade = sum(len(list(tabuleiro.legal_moves)) for p in tabuleiro.piece_map().values() if p.color == self.cor)
        pontos += mobilidade

        # Avaliando pins

        for quadrado, peca in tabuleiro.piece_map().items():
            if peca.color == self.cor and tabuleiro.is_pinned(self.cor, quadrado):
                pontos -= 20

        # Avaliando Forks

        for quadrado, peca in tabuleiro.piece_map().items():
            if peca.color != self.cor:
                continue

            ataques = tabuleiro.attacks(quadrado)
            alvos = 0

            for alvo in ataques:
                peca_alvo = tabuleiro.piece_at(alvo)
                if peca_alvo.color != self.cor:
                    if peca_alvo.symbol().upper() in ["B", "R", "Q", "N"]:
                        alvos += 1
                
            if alvos >= 2:
                pontos += 30

        return pontos
    
    def minimax(self, tabuleiro:chess.Board, profundidade: int, maximizando: bool, alpha: float, beta: float, movimento_anterior: chess.Move = None):

        avaliacao_atual = self.avaliar_tabuleiro(tabuleiro, movimento_anterior)

        if profundidade == 0 or tabuleiro.is_game_over():
            return avaliacao_atual
        
        if maximizando:
            melhor_valor = -float("inf")

            for movimento in self.ordenar_movimentos(tabuleiro, list(tabuleiro.legal_moves)):
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

            for movimento in self.ordenar_movimentos(tabuleiro, list(tabuleiro.legal_moves)):
                tabuleiro.push(movimento)
                valor = self.minimax(tabuleiro, profundidade - 1, True, alpha, beta, movimento)
                tabuleiro.pop()
                melhor_valor = min(melhor_valor, valor)
                beta = min(beta, melhor_valor)
                if beta <= alpha:
                    break
            return melhor_valor

    def obter_movimento_abertura(self, tabuleiro:chess.Board):
        try:
            with chess.polyglot.open_reader("Perfect2017.bin") as leitor:
                entradas = list(leitor.find_all(tabuleiro))

                if entradas:
                    melhor_entrada = max(entradas, key= lambda entrada: entrada.weight)
                    return melhor_entrada.move
            
        except Exception as e:
            print("Erro ao acessar o livro de aberturas:", e)

        return None

    def obter_melhor_movimento(self, tabuleiro:chess.Board):

        movimento_livro = self.obter_movimento_abertura(tabuleiro)

        if movimento_livro is not None:
            return movimento_livro

        movimentos = list(tabuleiro.legal_moves)
        melhor_movimento = None

        for profundidade_atual in range(1, self.profundidade + 1):
            pontos_movimentos = []

            for movimento in movimentos:
                tabuleiro.push(movimento)
                pontos = self.minimax(tabuleiro, profundidade_atual - 1, False, -float("inf"), float("inf"), movimento)
                tabuleiro.pop()
                pontos_movimentos.append((movimento, pontos))

            pontos_movimentos.sort(key=lambda x: x[1], reverse= True)
            movimentos = [mov for mov, _ in pontos_movimentos]

            melhor_movimento = movimentos[0]

        return melhor_movimento