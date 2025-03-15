from time import sleep
import pygame 
import chess
import chess.engine
import sys

from ias.randomIA import random_move

ALTURA, LARGURA = 720, 720
TAM_QUADRADOS = ALTURA / 8

ia_vs_ia = True

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
    valores_pos = {"P": [[0, 0, 0, 0, 0, 0, 0, 0], 
                         [50, 50, 50, 50, 50, 50, 50, 50], 
                         [10, 10, 20, 30, 30, 20, 10, 10], 
                         [5, 5, 10, 25, 25, 10, 5, 5], 
                         [0, 0, 0, 20, 20, 0, 0, 0], 
                         [5, -5, -10, 0, 0, -10, -5, 5], 
                         [5, 10, 10, -20, -20, 10, 10, 5], 
                         [0, 0, 0, 0, 0, 0, 0, 0]], 
                    "N": [[-50, -40, -30, -30, -30, -30, -40, -50],
                        [-40, -20, 0, 0, 0, 0, -20, -40], 
                        [-30, 0, 10, 15, 15, 10, 0, -30],
                        [-30, 5, 15, 20, 20, 15, 5, -30],
                        [-30, 0, 15, 20, 20, 15, 0, -30],
                        [-30, 5, 10, 15, 15, 10, 5, -30],
                        [-40, -20, 0, 5, 5, 0, -20, -40],
                        [-50, -40, -30, -30, -30, -30, -40, -50]], 
                    "B": [[-20, -10, -10, -10, -10, -10, -10, -20],
                        [-10, 0, 0, 0, 0, 0, 0, -10],
                        [-10, 0, 5, 10, 10, 5, 0, -10],
                        [-10, 5, 5, 10, 10, 5, 5, -10],
                        [-10, 0, 10, 10, 10, 10, 0, -10],
                        [-10, 10, 10, 10, 10, 10, 10, -10],
                        [-10, 5, 0, 0, 0, 0, 5, -10],
                        [-20, -10, -10, -10, -10, -10, -10, -20]],
                    "R": [[0, 0, 0, 0, 0, 0, 0, 0],
                        [5, 10, 10, 10, 10, 10, 10, 5],
                        [-5, 0, 0, 0, 0, 0, 0, -5],
                        [-5, 0, 0, 0, 0, 0, 0, -5],
                        [-5, 0, 0, 0, 0, 0, 0, -5],
                        [-5, 0, 0, 0, 0, 0, 0, -5],
                        [-5, 0, 0, 0, 0, 0, 0, -5],
                        [0, 0, 0, 5, 5, 0, 0, 0]],
                    "Q": [[-20, -10, -10, -5, -5, -10, -10, -20],
                        [-10, 0, 0, 0, 0, 0, 0, -10],
                        [-10, 0, 5, 5, 5, 5, 0, -10],
                        [-5, 0, 5, 5, 5, 5, 0, -5],
                        [0, 0, 5, 5, 5, 5, 0, -5],
                        [-10, 5, 5, 5, 5, 5, 0, -10],
                        [-10, 0, 5, 0, 0, 0, 0, -10],
                        [-20, -10, -10, -5, -5, -10, -10, -20]],
                    "K": [[0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0]]
                    }
    
    valores_pos_pretas = {piece: values[::-1] for piece, values in valores_pos.items()}

    valores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}
    score = 0

    if board.is_checkmate():  
        if board.turn == chess.WHITE:
            return 10000
        else:
            return -10000

    if board.is_stalemate() or board.is_insufficient_material():
        return -100

    for square in chess.SQUARES:
        peca = board.piece_at(square)

        if peca:
            valor_peca = valores.get(peca.symbol().upper(), 0)
            linha, coluna = divmod(square, 8)

            if peca.color == chess.WHITE:
                score -= valor_peca

            else:
                score += valor_peca

                if peca.symbol().upper() in valores_pos_pretas:
                    score += valores_pos_pretas[peca.symbol().upper()][linha][coluna]

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
            valor = minimax(board, 1, float('-inf'), float('inf'), False)
            board.pop()

            if valor > melhor_valor:
                melhor_valor = valor
                melhor_movimento = move

    return melhor_movimento
   

rodando = True
board = chess.Board()
relogio = pygame.time.Clock()
quadradoSelecionado = None
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

                if event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE and ia_vs_ia == False:
                    x, y = event.pos

                    coluna = int(x // TAM_QUADRADOS)
                    linha = 7 - int(y // TAM_QUADRADOS)

                    quadrado = chess.square(coluna, linha)
                    peca = board.piece_at(quadrado)

                    if quadradoSelecionado == None:
                        quadradoSelecionado = quadrado

                    else:

                        move = chess.Move(quadradoSelecionado, quadrado)

                        if move in board.legal_moves:
                            board.push(move)
                        else:
                            quadradoSelecionado = None

                        quadradoSelecionado = None
                            
                                                         

                    

        
        if not pausa:       
            if board.turn == chess.BLACK:
                move = move_ai("Min")
            
                if move:
                    board.push(move)
            
            else:
                move = move_ai("Random")

                if move:
                    board.push(move)


