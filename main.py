import pygame, sys, chess
from jogo import JogoXadrez
from ia import XadrezIA
from graficos import carregar_imagens, desenhar_tabuleiro, desenhar_pecas, desenhar_movimentos

ALTURA, LARGURA = 720, 720
TAM_QUADRADOS = ALTURA // 8

pecas_promocao = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
pecas_imagens = {chess.QUEEN: "q", chess.ROOK: "r", chess.BISHOP: "b", chess.KNIGHT: "n"}

def desenhar_menu_promocao(tela, cor, x):
    y = ALTURA // 2 - 2 * TAM_QUADRADOS
    for i, peca in enumerate(pecas_promocao):
        cor_str = 'w' if cor == chess.WHITE else 'b'
        peca_str = {chess.QUEEN: 'Q', chess.ROOK: 'R', chess.BISHOP: 'B', chess.KNIGHT: 'N'}[peca]
        imagem = pygame.image.load(f"img/{cor_str}{peca_str}.png")

        rect_x = x
        rect_y = y + i * TAM_QUADRADOS
        rect = pygame.Rect(rect_x, rect_y, TAM_QUADRADOS, TAM_QUADRADOS)

        pygame.draw.rect(tela, (255, 255, 255), rect, border_radius=10)

        pygame.draw.rect(tela, (0, 0, 0), rect, width=3, border_radius=10)

        imagem = pygame.transform.scale(imagem, (TAM_QUADRADOS - 10, TAM_QUADRADOS - 10))
        img_rect = imagem.get_rect(center=rect.center)
        tela.blit(imagem, img_rect.topleft)

    pygame.display.flip()

def escolher_promocao(tela, cor, x):
    desenhar_menu_promocao(tela, cor, x)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                _, y = event.pos
                index = (y - (ALTURA // 2 - 2 * TAM_QUADRADOS)) // TAM_QUADRADOS
                if 0 <= index < 4:
                    return pecas_promocao[index]

def main():
    pygame.init()
    tela = pygame.display.set_mode((ALTURA, LARGURA))
    pygame.display.set_caption("Xadrez contra algoritmo Minimax")

    carregar_imagens()
    jogo = JogoXadrez()
    ia = XadrezIA(profundidade=3)

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
                coluna = int(x // TAM_QUADRADOS)
                linha = 7 - int(y // TAM_QUADRADOS)
                quadrado = chess.square(coluna, linha)

                if quadrado_selecionado is None:

                    peca = jogo.board.piece_at(quadrado)

                    if peca and peca.color == chess.WHITE:
                        quadrado_selecionado = quadrado
                else:
                    movimento = chess.Move(quadrado_selecionado, quadrado)

                    # Detecta promoção
                    if (
                        jogo.board.piece_at(quadrado_selecionado).piece_type == chess.PAWN and
                        chess.square_rank(quadrado) == 7
                    ):
                        promocao = escolher_promocao(tela, chess.WHITE, x)
                        movimento = chess.Move(quadrado_selecionado, quadrado, promotion=promocao)

                    jogo.movimento(movimento)
                    quadrado_selecionado = None

        # Movimento da IA
        if not jogo.fim_de_jogo() and jogo.board.turn == chess.BLACK:
            movimento = ia.obter_melhor_movimento(jogo.board)
            if movimento:
                jogo.movimento(movimento)

if __name__ == "__main__":
    main()