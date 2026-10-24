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
                if celula == 'P': # Possível erro
                    self.jogador_x , self.jogador_y = x, y
                    self.grade[y][x] = '.'
                elif celula == 'E':
                    self.inimigos.append([x, y])
                    self.grade[y][x] = '.'

    def mover_jogador(self, dx, dy):
        novo_x = self.jogador_x + dx
        novo_y = self.jogador_y + dy
        self.jogador_x, self.jogador_y = novo_x, novo_y

    def inimigo_em(self, x, y):
        for inimigo in self.inimigos:
            if inimigo[0] == x and inimigo[1] == y:
                return inimigo
        return None

    def renderizar(self):
        for y, linha in enumerate(self.grade):
            texto_linha = ''

            for x, celula in enumerate(linha):
                if ( x , y) == ( self.jogador_x, self.jogador_y ):
                    texto_linha += ICONE_JOGADOR

                # Código novo
                elif self.inimigo_em(x, y):
                    texto_linha += 'E'
                else:
                    texto_linha += celula 
                    print('|' + texto_linha +  '|')
# git add .
# git commit -m 'mensagem'
# git push

# git clone https://github.com/wendellcs/rpg.git