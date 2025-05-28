import random
import threading
import pygame
from pygame import gfxdraw

# Inicializa o Pygame
pygame.init()
FPS = 10  # Frame rate controlado
screen = pygame.display.set_mode((500, 500))  # Janela 500x500 para 50x50 células
pygame.display.set_caption("Tabuleiro Zumbis vs Azuis")
clock = pygame.time.Clock()

# Tabuleiro 50x50
tabuleiro = [[0 for _ in range(50)] for _ in range(50)]
lock = threading.Lock()  # Lock para sincronização

# Posições iniciais espaçadas (2 zumbis na metade direita e 10 azuis na metade esquerda)
# Zumbis (colunas 25 a 49)
tabuleiro[10][40] = 2  # Zumbi 1
tabuleiro[40][45] = 2  # Zumbi 2

# Azuis (colunas 0 a 24)
tabuleiro[5][5] = 1    # Azul 1
tabuleiro[5][20] = 1   # Azul 2
tabuleiro[15][10] = 1  # Azul 3
tabuleiro[15][24] = 1  # Azul 4
tabuleiro[25][15] = 1  # Azul 5
tabuleiro[25][5] = 1   # Azul 6
tabuleiro[35][10] = 1  # Azul 7
tabuleiro[35][20] = 1  # Azul 8
tabuleiro[45][15] = 1  # Azul 9
tabuleiro[45][5] = 1   # Azul 10

# Lista de elementos ativos (x, y, valor)
elementos_ativos = [
    (10, 40, 2), (40, 45, 2),  # Zumbis
    (5, 5, 1), (5, 20, 1), (15, 10, 1), (15, 24, 1), (25, 15, 1),
    (25, 5, 1), (35, 10, 1), (35, 20, 1), (45, 15, 1), (45, 5, 1)  # Azuis
]

# Direções possíveis (cima, baixo, esquerda, direita)
direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Função para mover um elemento
def mover_elemento(x, y, valor, elementos_ativos):
    with lock:
        dx, dy = random.choice(direcoes)
        novo_x, novo_y = x + dx, y + dy
        if 0 <= novo_x < 50 and 0 <= novo_y < 50 and tabuleiro[novo_x][novo_y] == 0:
            tabuleiro[novo_x][novo_y] = valor
            tabuleiro[x][y] = 0
            # Atualiza a posição do elemento na lista
            idx = elementos_ativos.index((x, y, valor))
            elementos_ativos[idx] = (novo_x, novo_y, valor)
            return novo_x, novo_y
    return x, y

# Função para verificar interação (zumbi x azul)
def verificar_interacao(x, y, elementos_ativos):
    with lock:
        if tabuleiro[x][y] != 2:  # Só zumbis interagem
            return
        for dx, dy in direcoes:
            adj_x, adj_y = x + dx, y + dy
            if 0 <= adj_x < 50 and 0 <= adj_y < 50 and tabuleiro[adj_x][adj_y] == 1:
                tabuleiro[adj_x][adj_y] = 2  # Transforma azul em zumbi
                # Atualiza a lista de elementos
                idx = next(i for i, e in enumerate(elementos_ativos) if e[0] == adj_x and e[1] == adj_y)
                elementos_ativos[idx] = (adj_x, adj_y, 2)

# Função de atualização do jogo
def update_loop():
    global elementos_ativos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    # Executa um turno: move e interage
    threads = []
    for i, (x, y, valor) in enumerate(elementos_ativos):
        t = threading.Thread(target=lambda: (mover_elemento(x, y, valor, elementos_ativos), verificar_interacao(x, y, elementos_ativos)))
        threads.append(t)
        t.start()

    # Espera todas as threads terminarem o turno
    for t in threads:
        t.join()

    # Desenha o tabuleiro
    screen.fill((200, 200, 200))  # Fundo cinza claro
    cell_size = 10
    for i in range(50):
        for j in range(50):
            color = (200, 200, 200) if tabuleiro[i][j] == 0 else \
                    (0, 255, 255) if tabuleiro[i][j] == 1 else (0, 100, 0)  # Ciano claro ou Verde escuro (para zumbis)
            gfxdraw.box(screen, (j * cell_size, i * cell_size, cell_size, cell_size), color)

    # Verifica condições de término
    tem_azul = False
    azul_na_direita = False
    for i in range(50):
        for j in range(50):
            if tabuleiro[i][j] == 1:
                tem_azul = True
                if j == 49:
                    azul_na_direita = True

    # Se um azul chegou à direita, pausa o jogo sem fechar
    if azul_na_direita:
        print("Um azul chegou à direita! Jogo pausado, pressione 'q' para sair.")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    return False
            pygame.display.flip()
            clock.tick(FPS)

    # Se não houver mais azuis, pausa o jogo sem fechar
    if not tem_azul:
        print("Todos são zumbis! Jogo pausado, pressione 'q' para sair.")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    return False
            pygame.display.flip()
            clock.tick(FPS)

    pygame.display.flip()
    clock.tick(FPS)
    return True

# Loop principal
def main():
    while True:
        if not update_loop():
            break

if __name__ == "__main__":
    main()

# Fecha o Pygame ao terminar
pygame.quit()