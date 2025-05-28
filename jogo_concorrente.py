import random
import threading
import pygame
from pygame import gfxdraw
import asyncio
import platform

# Inicializa o Pygame
pygame.init()
FPS = 10  # Frame rate controlado
screen = pygame.display.set_mode((500, 500))  # Janela 500x500 para 50x50 células
pygame.display.set_caption("Tabuleiro Zumbis vs Azuis")
clock = pygame.time.Clock()

# Tabuleiro 50x50
tabuleiro = [[0 for _ in range(50)] for _ in range(50)]
lock = threading.Lock()  # Lock para sincronização

# Quantidades de azuis e zumbis
NUM_AZUIS = 10
NUM_ZUMBIS = 5

# Função para gerar posições aleatórias sem sobreposição
def gerar_posicoes_aleatorias(linhas, colunas_inicio, colunas_fim, quantidade):
    todas_posicoes = [(i, j) for i in range(linhas[0], linhas[1] + 1) for j in range(colunas_inicio, colunas_fim + 1)]
    if len(todas_posicoes) < quantidade:
        raise ValueError("Não há posições suficientes na área para alocar todos os elementos.")
    return random.sample(todas_posicoes, quantidade)

# Definir áreas e alocar elementos
def setup():
    global elementos_ativos
    # Lista de elementos ativos (x, y, valor)
    elementos_ativos = []

    # Áreas do tabuleiro
    area_azuis = (0, 49)    # linhas de 0 a 49
    area_zumbis = (0, 49)   # linhas de 0 a 49

    # Gerar posições: azuis na metade esquerda (colunas 0 a 24), zumbis na metade direita (colunas 25 a 49)
    posicoes_azuis = gerar_posicoes_aleatorias(area_azuis, 0, 24, NUM_AZUIS)
    posicoes_zumbis = gerar_posicoes_aleatorias(area_zumbis, 25, 49, NUM_ZUMBIS)

    # Alocar azuis
    for pos in posicoes_azuis:
        tabuleiro[pos[0]][pos[1]] = 1
        elementos_ativos.append((pos[0], pos[1], 1))

    # Alocar zumbis
    for pos in posicoes_zumbis:
        tabuleiro[pos[0]][pos[1]] = 2
        elementos_ativos.append((pos[0], pos[1], 2))

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
                    (0, 255, 255) if tabuleiro[i][j] == 1 else (0, 100, 0)  # Ciano claro ou Verde escuro
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

    # Se um azul chegou à direita, pausa o jogo
    if azul_na_direita:
        print("Um azul chegou à direita! Jogo pausado, pressione 'q' para sair.")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    return False
            pygame.display.flip()
            clock.tick(FPS)

    # Se não houver mais azuis, pausa o jogo
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

# Loop principal compatível com Pyodide
async def main():
    setup()  # Inicializa o tabuleiro
    while True:
        if not update_loop():  # Atualiza o jogo
            break
        await asyncio.sleep(1.0 / FPS)  # Controla o frame rate

# Verifica se está rodando no Pyodide (Emscripten) ou localmente
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())

# Fecha o Pygame ao terminar
pygame.quit()