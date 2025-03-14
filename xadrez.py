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
score = 0

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


def evaluate_board(board):
    valores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}
    score = 0

    if board.is_checkmate():  
        if board.turn == chess.WHITE:
            return 10000
        else:
            return -10000

    if board.is_stalemate() or board.is_insufficient_material():
        return -100

    central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

    for square in chess.SQUARES:
        peca = board.piece_at(square)
        if peca:
            valor_peca = valores.get(peca.symbol().upper(), 0)
            if peca.color == chess.WHITE:
                score -= valor_peca
            else:
                score += valor_peca

            if square in central_squares:
                score -= 5 if peca.color == chess.WHITE else +5

    score += len(list(board.legal_moves)) * 0.1

    return score



def minimax(board, depth, alpha, beta, maximize):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    movimentos_legais = list(board.legal_moves)

    if maximize:
        max_eval = float('-inf')
        for move in movimentos_legais:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return max_eval
    else:
        min_eval = float('inf')
        for move in movimentos_legais:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break

        return min_eval



def draw_pieces():
    for quadrado in chess.SQUARES:
        peca = board.piece_at(quadrado)

        if peca:
            coluna = quadrado % 8
            linha = 7 - (quadrado // 8)

            peca_str = peca.symbol().upper()

            cor = "w" if peca.color == chess.WHITE else "b"
            tela.blit(pecas[cor + peca_str], (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS))

def move_ai(selecionada: str):
    melhor_movimento = None
    melhor_valor = float('-inf')

    if selecionada == "Random":
        return random_move(board)
    elif selecionada == "Min":
        for move in board.legal_moves:
            board.push(move)
            valor = minimax(board, 2, float('-inf'), float('inf'), False)
            board.pop()

            if valor > melhor_valor:
                melhor_valor = valor
                melhor_movimento = move

    return melhor_movimento
   

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
                if pygame.key.get_pressed()[pygame.K_DOWN]:
                    print(board)

        
        if not pausa:

            if board.turn == chess.WHITE:
                move = move_ai("Random")
            else:
                move = move_ai("Random")
               
                
            

            if move:
                board.push(move)


