import chess
import json
import numpy as np
import random
import chess.polyglot

class XadrezIA:

    def __init__(self, profundidade=2, cor=chess.BLACK, parametros_personalizados=None):
        self.profundidade = profundidade
        self.cor = cor
        self.tabela_transposicao = {}

        self.parametros = parametros_personalizados or self.gerar_parametros_aleatorios()
        self.valores = self.parametros["VALOR_PECA"]

        with open("posicoes_ideais_w.json", "r") as w:
            self.posicoes_ideais_w = {k: np.array(v) for k, v in json.load(w).items()}
        with open("posicoes_ideais_b.json", "r") as b:
            self.posicoes_ideais_b = {k: np.array(v) for k, v in json.load(b).items()}

        self.posicoes_ideais = self.posicoes_ideais_b if cor == chess.BLACK else self.posicoes_ideais_w

    def gerar_parametros_aleatorios(self):
        return {
            "VALOR_PECA": {
                "P": random.randint(80, 120),
                "N": random.randint(250, 350),
                "B": random.randint(250, 350),
                "R": random.randint(450, 550),
                "Q": random.randint(850, 950),
                "K": 10000
            },
            "BONUS_PECA_CENTRO": random.randint(10, 40),
            "BONUS_FORK": random.randint(20, 60),
            "PENALIDADE_PIN": random.randint(30, 70),
            "PENALIDADE_PENDURADA_FRACAO": round(random.uniform(0.2, 0.6), 2),
            "BONUS_DESENVOLVIDA": random.randint(5, 20),
            "PENALIDADE_NAO_DESENVOLVIDA": random.randint(10, 30),
            "BONUS_CONTROLE_CENTRO": random.randint(5, 20),
            "BONUS_CHECK": random.randint(30, 70),
            "BONUS_CASTLING": random.randint(15, 40),
            "PENALIDADE_EMPATE": random.randint(200, 400),
            "PENALIDADE_REPETICAO": random.randint(150, 250),
            "BONUS_MOBILIDADE": random.randint(1, 5),
            "BONUS_DEFESA": random.randint(1, 5),
            "PENALIDADE_REI_SOBATAQUE": random.randint(1, 10),
            "BONUS_CHECKMATE": 11000
        }

    def estagio_jogo(self, tabuleiro: chess.Board):
        rainhas = [p for p in tabuleiro.piece_map().values() if p.piece_type == chess.QUEEN]
        if len(rainhas) == 0:
            return True
        elif len(rainhas) == 1:
            cor = rainhas[0].color
            menores = [p for p in tabuleiro.piece_map().values() if p.piece_type in [chess.KNIGHT, chess.BISHOP] and p.color == cor]
            return len(menores) <= 1
        return False

    def avaliar_tabuleiro(self, tabuleiro: chess.Board):
        score = 0
        centro = [chess.D4, chess.E4, chess.D5, chess.E5]
        if self.cor == chess.WHITE:
            iniciais_knight = {chess.B1, chess.G1}
            iniciais_bishop = {chess.C1, chess.F1}
        else:
            iniciais_knight = {chess.B8, chess.G8}
            iniciais_bishop = {chess.C8, chess.F8}

        for quadrado, peca in tabuleiro.piece_map().items():
            linha, coluna = divmod(quadrado, 8)
            simbolo = peca.symbol().upper()
            valor_peca = self.valores[simbolo]

            if simbolo == "K":
                bonus = self.posicoes_ideais[simbolo + "_l"][linha][coluna] if self.estagio_jogo(tabuleiro) else self.posicoes_ideais[simbolo + "_e"][linha][coluna]
            else:
                bonus = self.posicoes_ideais[simbolo][linha][coluna]

            if simbolo == "P" and peca.color == self.cor and quadrado in centro:
                bonus += self.parametros["BONUS_PECA_CENTRO"]

            if peca.color == self.cor:
                score += valor_peca + bonus
            else:
                score -= valor_peca + bonus

            if peca.color == self.cor:
                if tabuleiro.is_attacked_by(not self.cor, quadrado) and not tabuleiro.is_attacked_by(self.cor, quadrado):
                    score -= int(valor_peca * self.parametros["PENALIDADE_PENDURADA_FRACAO"])
                if tabuleiro.is_pinned(self.cor, quadrado):
                    score -= self.parametros["PENALIDADE_PIN"]

                alvos = 0
                for alvo in tabuleiro.attacks(quadrado):
                    peca_alvo = tabuleiro.piece_at(alvo)
                    if peca_alvo and peca_alvo.color != self.cor and peca_alvo.symbol().upper() in ["B", "R", "Q", "N"]:
                        alvos += 1
                if alvos >= 2:
                    score += self.parametros["BONUS_FORK"]

                if peca.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    if quadrado in iniciais_knight or quadrado in iniciais_bishop:
                        score -= self.parametros["PENALIDADE_NAO_DESENVOLVIDA"]
                    else:
                        score += self.parametros["BONUS_DESENVOLVIDA"]

                for alvo in tabuleiro.attacks(quadrado):
                    if alvo in centro:
                        score += self.parametros["BONUS_CONTROLE_CENTRO"]

        if tabuleiro.is_check():
            score += self.parametros["BONUS_CHECK"] if tabuleiro.turn != self.cor else -self.parametros["BONUS_CHECK"]
        if tabuleiro.is_checkmate():
            score += self.parametros["BONUS_CHECKMATE"] if tabuleiro.turn != self.cor else -self.parametros["BONUS_CHECKMATE"]
        if tabuleiro.is_stalemate() or tabuleiro.is_insufficient_material():
            score -= self.parametros["PENALIDADE_EMPATE"]
        if tabuleiro.is_repetition(2):
            score -= self.parametros["PENALIDADE_REPETICAO"]

        movimento_aliados = sum(1 for mov in tabuleiro.legal_moves if tabuleiro.piece_at(mov.from_square) and tabuleiro.piece_at(mov.from_square).color == self.cor)
        movimento_inimigos = sum(1 for mov in tabuleiro.legal_moves if  tabuleiro.piece_at(mov.from_square) and tabuleiro.piece_at(mov.from_square).color != self.cor)

        score += self.parametros["BONUS_MOBILIDADE"] * (movimento_aliados - movimento_inimigos)

        # segurança do rei

        quadrado_rei = tabuleiro.king(self.cor)

        if quadrado_rei is not None:
            adjacentes = [quad for quad in chess.SQUARES if chess.square_distance(quadrado_rei, quad) == 1]
            bonus_defesa = 0

            for quadrado in adjacentes:
                peca_adj = tabuleiro.piece_at(quadrado)

                if peca_adj and peca_adj.color == self.cor and peca_adj.symbol().upper() == "P":
                    bonus_defesa += self.parametros["BONUS_DEFESA"]

            score += bonus_defesa

            penalidade_ataques = 0

            for quadrado in adjacentes:
                if tabuleiro.is_attacked_by(not self.cor, quadrado):
                    penalidade_ataques += 1

            score -= self.parametros["PENALIDADE_REI_SOBATAQUE"] * penalidade_ataques

        return score

    def ordenar_movimentos(self, tabuleiro, movimentos):
        def prioridade(m):
            score = 0
            if tabuleiro.is_capture(m):
                score += 15
            if tabuleiro.gives_check(m):
                score += 5
            if tabuleiro.is_castling(m):
                score += 7
            return score
        return sorted(movimentos, key=prioridade, reverse=True)

    def minimax(self, tabuleiro, profundidade, maximizando, alpha, beta):
        if tabuleiro.fen() in self.tabela_transposicao:
            valor, prof_salva = self.tabela_transposicao[tabuleiro.fen()]
            if prof_salva >= profundidade:
                return valor

        if profundidade == 0 or tabuleiro.is_game_over():
            valor = self.avaliar_tabuleiro(tabuleiro)
            self.tabela_transposicao[tabuleiro.fen()] = (valor, profundidade)
            return valor

        movimentos = self.ordenar_movimentos(tabuleiro, list(tabuleiro.legal_moves))

        if maximizando:
            melhor_valor = -float("inf")
            for movimento in movimentos:
                tabuleiro.push(movimento)
                valor = self.minimax(tabuleiro, profundidade - 1, False, alpha, beta)
                tabuleiro.pop()
                melhor_valor = max(melhor_valor, valor)
                alpha = max(alpha, melhor_valor)
                if beta <= alpha:
                    break
            self.tabela_transposicao[tabuleiro.fen()] = (melhor_valor, profundidade)
            return melhor_valor
        else:
            melhor_valor = float("inf")
            for movimento in movimentos:
                tabuleiro.push(movimento)
                valor = self.minimax(tabuleiro, profundidade - 1, True, alpha, beta)
                tabuleiro.pop()
                melhor_valor = min(melhor_valor, valor)
                beta = min(beta, melhor_valor)
                if beta <= alpha:
                    break
            self.tabela_transposicao[tabuleiro.fen()] = (melhor_valor, profundidade)
            return melhor_valor

    def obter_movimento_abertura(self, tabuleiro: chess.Board):
        try:
            with chess.polyglot.open_reader("Perfect2017.bin") as leitor:
                entradas = list(leitor.find_all(tabuleiro))
                
                if entradas:
                    return max(entradas, key=lambda e: e.weight).move
        except:
            pass
        return None

    def obter_melhor_movimento(self, tabuleiro):
        movimento_abertura = self.obter_movimento_abertura(tabuleiro)
        if movimento_abertura:
            return movimento_abertura

        melhor_valor = -float("inf")
        melhor_movimento = None
        for movimento in self.ordenar_movimentos(tabuleiro, list(tabuleiro.legal_moves)):
            tabuleiro.push(movimento)
            valor = self.minimax(tabuleiro, self.profundidade - 1, False, -float("inf"), float("inf"))
            tabuleiro.pop()
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_movimento = movimento
        return melhor_movimento

import os

def mutar_parametros(parametros):
    novos = json.loads(json.dumps(parametros))
    for k, v in novos.items():
        if isinstance(v, dict):
            for sub_k in v:
                if sub_k != "K":
                    v[sub_k] += random.randint(-20, 20)
                    v[sub_k] = max(1, v[sub_k])
        elif isinstance(v, int):
            novos[k] += random.randint(-10, 10)
            novos[k] = max(1, novos[k])
        elif isinstance(v, float):
            novos[k] += round(random.uniform(-0.1, 0.1), 2)
            novos[k] = max(0.01, novos[k])

    return novos


def mostrar_parametros_ia(ia: XadrezIA, titulo="Parâmetros da IA"):
    print("\n" + "="*60)
    print(f"{titulo}".center(60))
    print("="*60)
    for chave, valor in ia.parametros.items():
        if isinstance(valor, dict):
            print(f"\n{chave}:")
            for subk, subv in valor.items():
                print(f"  {subk}: {subv}")
        else:
            print(f"{chave}: {valor}")
    print("="*60 + "\n")


def jogar_partida(ia1, ia2):
    jogo = chess.Board()
    while not jogo.is_game_over():
        atual = ia1 if jogo.turn == ia1.cor else ia2
        movimento = atual.obter_melhor_movimento(jogo)
        if movimento:
            print(movimento)
            jogo.push(movimento)
    return jogo.result()


def train_selfplay(geracoes=5, profundidade=4):
    
    if os.path.exists("melhor_individuo.json"):
        with open("melhor_individuo.json", "r") as f:
            parametros = json.load(f)
        melhor_antigo = XadrezIA(profundidade=profundidade, parametros_personalizados=parametros)
    else:
        melhor_antigo = XadrezIA(profundidade=profundidade)

    melhor_ia = melhor_antigo

    for rodada in range(geracoes):
        ia_mutado = XadrezIA(profundidade=profundidade,
                             cor=chess.BLACK if melhor_ia.cor == chess.WHITE else chess.WHITE,
                             parametros_personalizados=mutar_parametros(melhor_ia.parametros))

        resultado = jogar_partida(melhor_ia, ia_mutado)
        print(f"Geração {rodada+1} - Resultado: {resultado}")

        if (resultado == "1-0" and melhor_ia.cor == chess.WHITE) or (resultado == "0-1" and melhor_ia.cor == chess.BLACK):
            melhor_ia = melhor_ia
        else:
            melhor_ia = ia_mutado

    
    vitorias_novo = 0
    for i in range(3):
        jogo = chess.Board()
        ia_novo = melhor_ia
        ia_velho = melhor_antigo
        resultado = jogar_partida(ia_novo, ia_velho)
        print(f"Jogo de verificação {i+1} - Resultado: {resultado}")

        if (resultado == "1-0" and ia_novo.cor == chess.WHITE) or (resultado == "0-1" and ia_novo.cor == chess.BLACK):
            vitorias_novo += 1

    if vitorias_novo >= 2:
        print("Novo melhor indivíduo identificado! Salvando...")
        with open("melhor_individuo.json", "w") as f:
            json.dump(melhor_ia.parametros, f, indent=2)
        mostrar_parametros_ia(melhor_ia, "Novo Melhor Indivíduo")
    else:
        print("O novo indivíduo não superou o antigo.")
        mostrar_parametros_ia(melhor_antigo, "Melhor Antigo Mantido")
