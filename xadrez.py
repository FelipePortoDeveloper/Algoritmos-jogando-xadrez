from time import sleep
import pygame 
import chess
import chess.engine
import sys

from ias.randomIA import random_move

ALTURA, LARGURA = 720, 720
TAM_QUADRADOS = ALTURA / 8
IASELECIONADA = "Random"

BRANCO, VERDE = (238, 238, 210), (118, 150, 86)

pygame.init()
tela = pygame.display.set_mode((ALTURA, LARGURA))
pygame.display.set_caption("IAs jogando xadrez")

pecas = {}
def load_images():
    tipos = ["B", "K", "N", "P", "Q", "R"]
    cores = ['w', 'b']

    for cor in cores:
        for peca in tipos:
            image = pygame.image.load(f"img/{cor}{peca}.png")
            image = pygame.transform.scale(image, (TAM_QUADRADOS, TAM_QUADRADOS))

            pecas[cor + peca] = image


def draw_board():
    for linha in range(8):
        for coluna in range(8):
            cor = BRANCO if (linha + coluna) % 2 == 0 else VERDE
            pygame.draw.rect(tela, cor, (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS, TAM_QUADRADOS, TAM_QUADRADOS))

def draw_pieces():
    for quadrado in chess.SQUARES:
        peca = board.piece_at(quadrado)

        if peca:
            coluna = quadrado % 8
            linha = 7 - (quadrado // 8)

            peca_str = peca.symbol().upper()

            cor = "w" if peca.color == chess.WHITE else "b"
            tela.blit(pecas[cor + peca_str], (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS))

def move_ai():
    if IASELECIONADA == "Random":
        board.push(random_move(board))
    elif IASELECIONADA == "Monte":
        pass
    elif IASELECIONADA == "Min":
        pass



rodando = True
board = chess.Board()
relogio = pygame.time.Clock()
pecaSelecionada = None
pausa = False

load_images()
while rodando:

    draw_board()
    draw_pieces()
    pygame.display.flip()
    relogio.tick(2)

    if board.is_game_over():
        if board.is_stalemate() and not pausa:
            print("Afogamento!")
        elif board.is_checkmate() and not pausa:
            print("Xeque-mate!")
        elif board.is_insufficient_material() and not pausa:
            print("Material insuficiente para checkmate!")
        
        pausa = True

   
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

    if not pausa:
        move_ai()