import pygame
import chess

BRANCO, VERDE = (238, 238, 210), (118, 150, 86)
ALTURA, LARGURA = 720, 720
TAM_QUADRADOS = ALTURA // 8
pecas = {}

def carregar_imagens():
    
    tipos = ["B", "K", "N", "P", "Q", "R"]
    cores = ['w', 'b']

    for cor in cores:
        for peca in tipos:
            image = pygame.image.load(f"img/{cor}{peca}.png")
            image = pygame.transform.scale(image, (TAM_QUADRADOS, TAM_QUADRADOS))
            
            pecas[cor + peca] = image

def desenhar_tabuleiro(tela):
    for linha in range(8):
        for coluna in range(8):
            cor = BRANCO if (linha + coluna) % 2 == 0 else VERDE
            pygame.draw.rect(tela, cor, (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS, TAM_QUADRADOS, TAM_QUADRADOS))

def desenhar_pecas(tela, tabuleiro:chess.Board):
    for quadrado in chess.SQUARES:

        peca = tabuleiro.piece_at(quadrado)

        if peca:
            coluna = quadrado % 8
            linha = 7 - (quadrado // 8)
            
            peca_str = peca.symbol().upper()
            cor = "w" if peca.color == chess.WHITE else "b"
            tela.blit(pecas[cor + peca_str], (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS))

def desenhar_movimentos(tela, quadrado: chess.Square, tabuleiro:chess.Board):
    peca = tabuleiro.piece_at(quadrado)

    if peca:
        movimentos_permitidos = [movimento for movimento in tabuleiro.legal_moves if movimento.from_square == quadrado]

        for movimento in movimentos_permitidos:
            para_linha, para_coluna = divmod(movimento.to_square, 8)

            pygame.draw.circle(tela, (10, 10, 10), (para_coluna * TAM_QUADRADOS + TAM_QUADRADOS // 2, (7 - para_linha) * TAM_QUADRADOS + TAM_QUADRADOS // 2), 15)