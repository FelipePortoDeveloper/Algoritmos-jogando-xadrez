import random, chess


def random_move(board):
    movimentos = list(board.legal_moves)

    if movimentos:
        random_move = random.choice(movimentos)
    
        return random_move