import random
import arcade

# Configurações do nosso jogo.
TAMANHO_TILE = 32 # Tamanho do tile em pixels ( 32px x 32px )
ESCALA = 0.25 # Controla o tamanho das sprites ( reduz para 25% do tamanho original )
INTERVALO_MOVIMENTO_INIMIGO = 0.5 
DURACAO_FRAME_ANDANDO = 0.12 
TEMPO_PARA_VOLTAR_AO_IDLE = 0.3 # Tempo para resetar as animações do player.

# Caminhos das imagens e sprites utilizadas
CAMINHO_PAREDE = None 
CAMINHO_CHAO = None 
CAMINHO_JOGADOR_IDLE = None 
CAMINHO_JOGADOR_UP = None 
CAMINHOS_JOGADOR_ANDANDO = [] 
CAMINHO_INIMIGO_PARADO = None 
CAMINHO_INIMIGO_ANDANDO = None

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

class JanelaJogo(arcade.Window):
    def __init__(self):
        super().__init__(640, 480, 'RPG em Python') # Inicializa a janela em 640x480 e um título
        self.mundo = Mundo()
        self.sprites_cenario = arcade.SpriteList() # Lista de sprites do cenário
        self.sprites_jogador = arcade.SpriteList()
        self.sprites_inimigos = arcade.SpriteList()

        self.tempo_desde_ultimo_passo_inimigo = 0.0 
        self.montar_cenario() # Chama o método montar cenário
        self.montar_personagem()

        # Carrega os frames da caminhada do jogador
        self.texturas_andando = [arcade.load_texture(caminho) for caminho in CAMINHOS_JOGADOR_ANDANDO]
        self.textura_idle = arcade.load_texture(CAMINHO_JOGADOR_IDLE)
        self.textura_up = arcade.load_texture(CAMINHO_JOGADOR_UP)
        self.textura_inimigo_parado = arcade.load_texture(CAMINHO_INIMIGO_PARADO)
        self.textura_inimigo_andando = arcade.load_texture(CAMINHO_INIMIGO_ANDANDO)

        # Controle da animação 
        self.indice_frame_andando = 0 # Qual frame da caminhada ta sendo exibido
        self.tempo_desde_ultimo_frame = 0.0
        self.tempo_desde_ultimo_movimento_jogador = 999.0 # Há quanto tempo o jogador está parado
        self.direcao_horizontal = 1 # 1 = direita, -1 = esquerda
        self.ultimo_tipo_movimento = None # 'lateral', 'cima' ou 'baixo'

    def on_draw(self): # Método chamado a cada frame para renderizar na tela
        self.clear() # Limpa a tela
        self.sprites_cenario.draw() # Desenha o cenário
        self.sprites_jogador.draw() # Desenha o jogador
        self.sprites_inimigos.draw() # Desenha os inimigos

    def para_tela_x(self, x): # Converte a coordenada X da grade para coordenada X da tela
        return x * TAMANHO_TILE + TAMANHO_TILE / 2

    def para_tela_y(self, y):
        num_linhas = len(self.mundo.grade) # Número total de linhas na grade
        # Inverte o eixo Y ( grade cresce para baixo, tela para cima )
        return (num_linhas - 1 - y) * TAMANHO_TILE + TAMANHO_TILE / 2 

    def montar_cenario(self): # Método que cria os sprites do cenário
        for y, linha in enumerate(self.mundo.grade): # Percorre as linhas da grade
            for x, celula in enumerate(linha): # Percorre as células das linhas
                caminho = CAMINHO_PAREDE if celula == 'B' else CAMINHO_CHAO # Escolhe imagem de parede ou chão
                sprite = arcade.Sprite(caminho, scale=ESCALA) # Cria o sprite com a escala definida
                # Define as posições X e Y na tela
                sprite.center_x = self.para_tela_x(x) 
                sprite.center_y = self.para_tela_y(y)
                self.sprites_cenario.append(sprite) # Adiciona o sprite à lista do cenário

    def montar_personagem(self):
        self.sprite_jogador = arcade.Sprite(CAMINHO_JOGADOR_IDLE, scale=ESCALA) # Cria o sprite do jogador
        # Posiciona o jogador
        self.atualizar_posicao_sprite(self.sprite_jogador, self.mundo.jogador_x, self.mundo_jogador_y) 


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
# pip install arcade
# python -m pip install arcade <- Só o Eduardo

# git pull