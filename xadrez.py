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


def ordenar_movimentos(board: chess.Board):
    return sorted(board.legal_moves, key= lambda move: evaluate_move(board, move), reverse= True)

def evaluate_move(board: chess.Board, move):
    board.push(move)
    valor = evaluate_board(board)
    board.pop()

    return valor


def draw_board():
    for linha in range(8):
        for coluna in range(8):
            cor = BRANCO if (linha + coluna) % 2 == 0 else VERDE
            pygame.draw.rect(tela, cor, (coluna * TAM_QUADRADOS, linha * TAM_QUADRADOS, TAM_QUADRADOS, TAM_QUADRADOS))


def evaluate_board(board):

    valores = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000}
    score = 0

    if board.is_checkmate():  
        if board.turn == chess.WHITE:
            return 1000
        else:
            return -1000

    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
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
                score += 5 if peca.color == chess.BLACK else -5 

    if board.is_repetition(1): 
        score -= 20

    print(score)
    return score

transposition_table = {}

def minimax(board, depth, alpha, beta, maximize):

    hash_key = board.fen()

    if hash_key in transposition_table and transposition_table[hash_key][1] >= depth:
        return transposition_table[hash_key][0]

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    melhor_valor = float('-inf') if maximize else float('inf')

    for move in ordenar_movimentos(board):
        board.push(move)
        eval = minimax(board, depth - 1, alpha, beta, not maximize)
        board.pop()

        if maximize:
            melhor_valor = max(melhor_valor, eval)
            alpha = max(alpha, eval)

        else:
            melhor_valor = min(melhor_valor, eval)
            beta = min(beta, eval)
            

        if beta <= alpha:
            break

        transposition_table[hash_key] = (melhor_valor, depth)
    
    return melhor_valor


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
            valor = minimax(board, 1, float('-inf'), float('inf'), True)
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
            
            elif ia_vs_ia:
                move = move_ai("Random")

                if move:
                    board.push(move)


