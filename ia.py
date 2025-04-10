import chess
import json
import numpy as np
import chess.polyglot

class Avaliacao:
    VALOR_PECA = {
        "P": 100,
        "N": 300,
        "B": 300,
        "R": 500,
        "Q": 900,
        "K": 10000
    }

    BONUS_PECA_CENTRO = 20
    BONUS_FORK = 30
    PENALIDADE_PIN = 50
    PENALIDADE_PENDURADA_FRACAO = 1/3
    BONUS_DESENVOLVIDA = 10
    PENALIDADE_NAO_DESENVOLVIDA = 15
    BONUS_CONTROLE_CENTRO = 10
    BONUS_CHECK = 50
    BONUS_CASTLING = 25
    PENALIDADE_EMPATE = 300
    PENALIDADE_REPETICAO = 200
    BONUS_MOBILIDADE = 2
    BONUS_CHECKMATE = 11000


class XadrezIA:

    def __init__(self, profundidade = 2, cor = chess.BLACK):

        self.profundidade = profundidade
        self.cor = cor
        self.valores = Avaliacao.VALOR_PECA
        self.tabela_transposicao = {}

        with open("posicoes_ideais_w.json", "r") as w:
            self.posicoes_ideais_w = {k: np.array(v) for k, v in json.load(w).items()}

        with open("posicoes_ideais_b.json", "r") as b:
            self.posicoes_ideais_b = {k: np.array(v) for k, v in json.load(b).items()}

        if cor == chess.BLACK:
            self.posicoes_ideais = self.posicoes_ideais_b
        else:
            self.posicoes_ideais = self.posicoes_ideais_w

    def estagio_jogo(self, tabuleiro: chess.Board):

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

    def avaliar_movimento(self, tabuleiro: chess.Board, movimento: chess.Move):
        pontos = 0

        if tabuleiro.is_capture(movimento):
            peca_capturada = tabuleiro.piece_at(movimento.to_square)
            peca_atacante = tabuleiro.piece_at(movimento.from_square)

            if peca_atacante and peca_atacante.color == self.cor and peca_capturada:
                simbolo_a = peca_atacante.symbol().upper()
                simbolo_c = peca_capturada.symbol().upper()
                pontos += self.valores[simbolo_c] - self.valores[simbolo_a]

        if tabuleiro.gives_check(movimento):
            pontos += Avaliacao.BONUS_CHECK

        if tabuleiro.is_castling(movimento):
            pontos += Avaliacao.BONUS_CASTLING

        return pontos


    def ordenar_movimentos(self, tabuleiro: chess.Board, movimentos: list):
        movimentos_avaliados = []

        for movimento in movimentos:
            pontos = self.avaliar_movimento(tabuleiro, movimento)
            movimentos_avaliados.append((movimento, pontos))

        movimentos_avaliados.sort(key=lambda x: x[1], reverse=True)

        return [move for move, _ in movimentos_avaliados]

    def avaliar_tabuleiro(self, tabuleiro: chess.Board, movimento: chess.Move = None):
        score = 0
        centro = [chess.D4, chess.E4, chess.D5, chess.E5]
        simulou = False

        if movimento is not None and tabuleiro.is_legal(movimento):
            score += self.avaliar_movimento(tabuleiro, movimento)
            tabuleiro.push(movimento)
            simulou = True

        if self.cor == chess.WHITE:
            pos_iniciais_knight = {chess.B1, chess.G1}
            pos_iniciais_bishop = {chess.C1, chess.F1}
        else:
            pos_iniciais_knight = {chess.B8, chess.G8}
            pos_iniciais_bishop = {chess.C8, chess.F8}

        for quadrado, peca in tabuleiro.piece_map().items():
            linha, coluna = divmod(quadrado, 8)
            simbolo = peca.symbol().upper()
            valor_peca = self.valores[simbolo]

            if simbolo == "K":
                bonus = self.posicoes_ideais[simbolo + "_l"][linha][coluna] if self.estagio_jogo(tabuleiro) else self.posicoes_ideais[simbolo + "_e"][linha][coluna]
            else:
                bonus = self.posicoes_ideais[simbolo][linha][coluna]

            if simbolo == "P" and peca.color == self.cor and quadrado in centro:
                bonus += Avaliacao.BONUS_PECA_CENTRO

            if peca.color == self.cor:
                score += valor_peca + bonus
            else:
                score -= valor_peca + bonus

            if peca.color == self.cor:
                if tabuleiro.is_attacked_by(not self.cor, quadrado) and not tabuleiro.is_attacked_by(self.cor, quadrado):
                    score -= int(valor_peca * Avaliacao.PENALIDADE_PENDURADA_FRACAO)

                if tabuleiro.is_pinned(self.cor, quadrado):
                    score -= Avaliacao.PENALIDADE_PIN

                alvos = 0
                for alvo in tabuleiro.attacks(quadrado):
                    peca_alvo = tabuleiro.piece_at(alvo)
                    if peca_alvo and peca_alvo.color != self.cor and peca_alvo.symbol().upper() in ["B", "R", "Q", "N"]:
                        alvos += 1
                if alvos >= 2:
                    score += Avaliacao.BONUS_FORK

                if peca.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    if quadrado in pos_iniciais_knight or quadrado in pos_iniciais_bishop:
                        score -= Avaliacao.PENALIDADE_NAO_DESENVOLVIDA
                    else:
                        score += Avaliacao.BONUS_DESENVOLVIDA

                for alvo in tabuleiro.attacks(quadrado):
                    if alvo in centro:
                        score += Avaliacao.BONUS_CONTROLE_CENTRO
                        break

        if simulou:
            tabuleiro.pop()

        if tabuleiro.is_check():
            score += Avaliacao.BONUS_CHECK if tabuleiro.turn != self.cor else -Avaliacao.BONUS_CHECK
        if tabuleiro.is_checkmate():
            score += Avaliacao.BONUS_CHECKMATE if tabuleiro.turn != self.cor else -Avaliacao.BONUS_CHECKMATE
        if tabuleiro.is_stalemate() or tabuleiro.is_insufficient_material():
            score -= Avaliacao.PENALIDADE_EMPATE
        if tabuleiro.is_repetition(2):
            score -= Avaliacao.PENALIDADE_REPETICAO

        mobilidade = sum(len(list(tabuleiro.legal_moves)) for peca in tabuleiro.piece_map().values() if peca.color == self.cor)
        score += mobilidade * Avaliacao.BONUS_MOBILIDADE

        return score


    def minimax(self, tabuleiro: chess.Board, profundidade: int, maximizando: bool, alpha: float, beta: float, movimento_anterior: chess.Move = None):

        tabuleiro_hash = hash(tabuleiro.fen())

        if tabuleiro_hash in self.tabela_transposicao: 
            entrada = self.tabela_transposicao[tabuleiro_hash]
            if entrada["profundidade"] >= profundidade:
                return entrada["valor"]

        avaliacao_atual = self.avaliar_tabuleiro(tabuleiro, movimento_anterior)

        if profundidade == 0 or tabuleiro.is_game_over():
            self.tabela_transposicao[tabuleiro_hash] = {"valor": avaliacao_atual, "profundidade": profundidade}
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

            self.tabela_transposicao[tabuleiro_hash] = {"valor": melhor_valor, "profundidade": profundidade}
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
            
            self.tabela_transposicao[tabuleiro_hash] = {"valor": melhor_valor, "profundidade": profundidade}
            return melhor_valor

    def obter_movimento_abertura(self, tabuleiro: chess.Board):
        try:
            with chess.polyglot.open_reader("Perfect2017.bin") as leitor:
                entradas = list(leitor.find_all(tabuleiro))

                if entradas:
                    melhor_entrada = max(entradas, key= lambda entrada: entrada.weight)
                    return melhor_entrada.move
            
        except Exception as e:
            print("Erro ao acessar o livro de aberturas:", e)

        return None

    def obter_melhor_movimento(self, tabuleiro: chess.Board):

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

            pontos_movimentos.sort(key=lambda x: x[1], reverse=True)
            movimentos = [mov for mov, _ in pontos_movimentos]

            melhor_movimento = movimentos[0]

        return melhor_movimento
