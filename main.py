import pygame, sys, chess
from jogo import JogoXadrez
from ia import XadrezIA
from graficos import carregar_imagens, desenhar_tabuleiro, desenhar_pecas, desenhar_movimentos

ALTURA, LARGURA = 720, 720
TAM_QUADRADOS = ALTURA // 8

def main():

    pygame.init()

    tela = pygame.display.set_mode((ALTURA, LARGURA))
    pygame.display.set_caption("Xadrez contra algoritmo Minimax")

    carregar_imagens()
    jogo = JogoXadrez()
    ia = XadrezIA(profundidade = 4)

    rodando = True
    quadrado_selecionado = None

    while rodando:

        tela.fill((0, 0, 0))
        desenhar_tabuleiro(tela)
        desenhar_pecas(tela, jogo.board)

        if quadrado_selecionado != None:
            desenhar_movimentos(tela, quadrado_selecionado, jogo.board)

        pygame.display.flip()

        if jogo.fim_de_jogo():
            print("Fim de jogo")
            rodando = False
            break
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
                sys.exit()

            if pygame.key.get_pressed()[pygame.K_r]:
                jogo.reinicia_jogo()

            if event.type == pygame.MOUSEBUTTONDOWN and jogo.board.turn == chess.WHITE:
                x, y = event.pos

                coluna = int(x // (TAM_QUADRADOS))  
                linha = 7 - int(y // TAM_QUADRADOS)

                quadrado = chess.square(coluna, linha)
                peca = jogo.board.piece_at(quadrado)

                if quadrado_selecionado == None:
                    quadrado_selecionado = quadrado

                else:
                    move = chess.Move(quadrado_selecionado, quadrado)

                    jogo.movimento(move)

                    quadrado_selecionado = None
        
        if not jogo.fim_de_jogo() and jogo.board.turn == chess.BLACK:
            movimento = ia.obter_melhor_movimento(jogo.board)

            if movimento:
                jogo.movimento(movimento)

if __name__ == "__main__":
    main()