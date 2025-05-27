import random

def criar_mundo_wumpus(n=4, num_buracos=3):
    mundo = [[[] for _ in range(n)] for _ in range(n)]

    def posicao_aleatoria(excluidas):
        while True:
            x, y = random.randint(0, n-1), random.randint(0, n-1)
            if (x, y) not in excluidas:
                return (x, y)

    def vizinhos(x, y):
        return [(nx, ny) for (nx, ny) in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)] if 0 <= nx < n and 0 <= ny < n]

    usados = set()

    # Coloca o Wumpus
    xw, yw = posicao_aleatoria(usados)
    mundo[xw][yw].append('W')
    usados.add((xw, yw))
    for vx, vy in vizinhos(xw, yw):
        if 'F' not in mundo[vx][vy]:
            mundo[vx][vy].append('F')

    # Coloca o ouro
    xg, yg = posicao_aleatoria(usados)
    mundo[xg][yg].append('G')
    usados.add((xg, yg))

    # Coloca os buracos
    for _ in range(num_buracos):
        xb, yb = posicao_aleatoria(usados)
        mundo[xb][yb].append('P')
        usados.add((xb, yb))
        for vx, vy in vizinhos(xb, yb):
            if 'B' not in mundo[vx][vy]:
                mundo[vx][vy].append('B')

    # Coloca posição inicial (opcional)
    mundo[0][0].append('S')

    return mundo

def imprimir_mundo(mundo):
    n = len(mundo)
    for i in range(n):
        for j in range(n):
            cell = ','.join(mundo[i][j]) if mundo[i][j] else '.'
            print(f"[{cell:^7}]", end=' ')
        print()

# Exemplo de uso
mundo = criar_mundo_wumpus(n=4, num_buracos=3)
imprimir_mundo(mundo)
