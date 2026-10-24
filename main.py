import random

mapa_tiles = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B..................B',
    'B.....E............B',
    'B............B.....B',
    'B..BBBBB.....B.....B',
    'B...B........B.....B',
    'B...B..............B',
    'B...B.......BBB....B',
    'B..................B',
    'B.....BBBB.........B',
    'B.......E..........B',
    'B.............P....B',
    'B..................B',
    'B.....E............B',
    'BBBBBBBBBBBBBBBBBBBB',
]

ICONE_JOGADOR = '@'

class Mundo:
    def __init__(self):
        self.grade = [list(linha) for linha in mapa_tiles]
        self.jogador_x = 0
        self.jogador_y = 0
        self.inimigos = []
        for y, linha in enumerate(self.grade):
            for x, celula in enumerate(linha):
                if celula == 'P':
                    self.jogador_x, self.jogador_y = x, y
                    self.grade[y][x] = '.'
                elif celula == 'E':
                    self.inimigos.append([x, y])
                    self.grade[y][x] = '.'

    def mover_jogador(self, dx, dy):
        novo_x = self.jogador_x + dx
        novo_y = self.jogador_y + dy
        if self.esta_bloqueado(novo_x, novo_y):
            print("Você esbarra em uma parede.")
            return
        inimigo = self.inimigo_em(novo_x, novo_y)
        if inimigo:
            print("Um inimigo bloqueia o caminho.")
            return
        self.jogador_x, self.jogador_y = novo_x, novo_y

    def esta_bloqueado(self, x, y):
        if y < 0 or y >= len(self.grade) or x < 0 or x >= len(self.grade[0]):
            return True
        return self.grade[y][x] == 'B'

    def inimigo_em(self, x, y):
        for inimigo in self.inimigos:
            if inimigo[0] == x and inimigo[1] == y:
                return inimigo
        return None

    def renderizar(self):
        for y, linha in enumerate(self.grade):
            texto_linha = ""
            for x, celula in enumerate(linha):
                if (x, y) == (self.jogador_x, self.jogador_y):
                    texto_linha += ICONE_JOGADOR
                elif self.inimigo_em(x, y):
                    texto_linha += 'E'
                else:
                    texto_linha += celula
            print("|" + texto_linha + "|")
        print("Movimento: W (cima) / S (baixo) / A (esquerda) / D (direita) / Q (sair)")

    def vagar_inimigos(self):
        for inimigo in self.inimigos:
            dx, dy = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = inimigo[0] + dx, inimigo[1] + dy
            if not self.esta_bloqueado(nx, ny) and (nx, ny) != (self.jogador_x, self.jogador_y):
                if not self.inimigo_em(nx, ny):
                    inimigo[0], inimigo[1] = nx, ny

def executar():
    mundo = Mundo()
    rodando = True
    while rodando:
        mundo.renderizar()
        comando = input("\n> ").strip().lower()
        if comando == 'w':
            mundo.mover_jogador(0, -1)
        elif comando == 's':
            mundo.mover_jogador(0, 1)
        elif comando == 'a':
            mundo.mover_jogador(-1, 0)
        elif comando == 'd':
            mundo.mover_jogador(1, 0)
        elif comando == 'q':
            rodando = False
            continue
        else:
            print("Comando inválido.")
            continue
        mundo.vagar_inimigos()
    print("Obrigado por jogar!")

# Chamada para iniciar o jogo
executar()

# git add .
# git commit -m 'mensagem'
# git push

# git clone https://github.com/wendellcs/rpg.git

# cd ./rpg
# git pull