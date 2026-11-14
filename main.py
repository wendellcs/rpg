import random
import arcade

# Configurações do nosso jogo.
TAMANHO_TILE = 32 # Tamanho do tile em pixels ( 32px x 32px )
ESCALA = 0.25 # Controla o tamanho das sprites ( reduz para 25% do tamanho original )
INTERVALO_MOVIMENTO_INIMIGO = 0.5 
DURACAO_FRAME_ANDANDO = 0.12 
TEMPO_PARA_VOLTAR_AO_IDLE = 0.3 # Tempo para resetar as animações do player.

# Caminhos das imagens e sprites utilizadas
CAMINHO_PAREDE = "imagens_arcade/parede_tile.png"
CAMINHO_CHAO = "imagens_arcade/chao.png"
CAMINHO_JOGADOR_IDLE = "imagens_arcade/player/idle1.png"
CAMINHO_JOGADOR_UP = "imagens_arcade/player/up1.png"
CAMINHOS_JOGADOR_ANDANDO = [
    f"imagens_arcade/player/direita{i}.png"
    for i in range(1, 4)
]
CAMINHO_INIMIGO_PARADO = "imagens_arcade/inimigos/abobora/abobora1.png"
CAMINHO_INIMIGO_ANDANDO = "imagens_arcade/inimigos/abobora/abobora2.png"

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
        # Adiciona o sprite do jogador à lista
        self.sprites_jogador.append(self.sprite_jogador)

        # Percorre cada inimigo do mundo
        for inimigo in self.mundo.inimigos:
            # Cria a sprite do inimigo
            sprite = arcade.Sprite(CAMINHO_INIMIGO_PARADO, scale = ESCALA)
            # Posiciona nas coords do inimigo 
            self.atualizar_posicao_sprite(sprite, inimigo[0], inimigo[1])
            # Adiciona à lista de inimigos
            self.sprites_inimigos.append(sprite)

    def atualizar_posicao_sprite(self, sprite, grade_x, grade_y):
        sprite.center_x = self.para_tela_x(grade_x) # Converte e define X
        sprite.center_y = self.para_tela_y(grade_y) # Converte e define Y

    # Método chamado quando a tecla é pressionada
    def on_key_press(self, key, modifiers):
        # Flag que indica se o jogador se moveu
        moveu = False 
        # Se tecla W ou seta pra cima
        if key in (arcade.key.W, arcade.key.UP):
            moveu = self.mundo.mover_jogador(0, -1)
            if moveu:
                self.ultimo_tipo_movimento = 'cima'

        elif key in (arcade.key.S, arcade.key.DOWN):
            moveu = self.mundo.mover_jogador(0, 1)
            if moveu:
                self.ultimo_tipo_movimento = 'baixo'

        elif key in (arcade.key.A, arcade.key.LEFT):
            moveu = self.mundo.mover_jogador(-1, 0)
            if moveu:
                self.direcao_horizontal = -1
                self.ultimo_tipo_movimento = 'lateral'

        elif key in (arcade.key.D, arcade.key.RIGHT):
            moveu = self.mundo.mover_jogador(1, 0)
            if moveu:
                self.direcao_horizontal = 1
                self.ultimo_tipo_movimento = 'lateral'

        elif key == arcade.key.Q or key == arcade.key.ESCAPE:
            arcade.close_window()
            return

        if moveu:
            self.atualizar_posicao_sprite(self.sprite_jogador, self.mundo.jogador_x, self.mundo.jogador_y)
            self.tempo_desde_ultimo_movimento_jogador = 0.0
            self.atualizar_textura_jogador()

    # Método chamado a cada frame para atualizar a lógica
    def on_update(self, delta_time):
        # Animação do player
        self.tempo_desde_ultimo_movimento_jogador += delta_time

        # Se ainda está dentro do tempo da animação
        if self.tempo_desde_ultimo_movimento_jogador < TEMPO_PARA_VOLTAR_AO_IDLE:
            # Se o movimento foi lateral
            if self.ultimo_tipo_movimento == 'lateral':
                self.tempo_desde_ultimo_frame += delta_time

                # Se passou o tempo de trocar frame
                if self.tempo_desde_ultimo_frame >= DURACAO_FRAME_ANDANDO:
                    self.tempo_desde_ultimo_frame = 0.0
                    # Avança frame
                    self.indice_frame_andando = (self.indice_frame_andando + 1) % len(self.texturas_andando)
                    # Aplica nova textura
                    self.sprite_jogador.texture = self.texturas_andando[self.indice_frame_andando]
        
        # Se passou tempo suficiente parado
        else:
            # Volta para a textura parada
            self.sprite_jogador.texture = self.textura_idle
            # Reseta o tipo de movimento
            self.ultimo_tipo_movimento = None

        self.tempo_desde_ultimo_passo_inimigo += delta_time

        if self.tempo_desde_ultimo_passo_inimigo >= INTERVALO_MOVIMENTO_INIMIGO:
            self.mundo.vagar_inimigos()
            
            # Percorre cada inimigo
            for i, inimigo in enumerate(self.mundo.inimigos):
                sprite = self.sprites_inimigos[i]

                dx = inimigo[0] - posicoes_antigas[i][0]
                
                # Moveu para direita
                if dx > 0:
                    sprite.scale_x = abs(sprite.scale_x)
                elif dx < 0:
                    sprite.scale_x -abs(sprite.scale_x)

                self.atualizar_posicao_sprite(sprite, inimigo[0], inimigo[1])
                sprite.texture = self.textura_inimigo_andando

            self.tempo_desde_ultimo_passo_inimigo = 0.0
        
        # Se passou metade do intervalo
        elif self.tempo_desde_ultimo_passo_inimigo >= INTERVALO_MOVIMENTO_INIMIGO / 2:
            for sprite in self.sprites_inimigos:
                sprite.texture = self.textura_inimigo_parado
    
    def atualizar_textura_jogador(self):
        if self.ultimo_tipo_movimento == 'lateral':
            # Espelha a sprite 
            self.sprite_jogador.scale_x = self.direcao_horizontal * abs(self.sprite_jogador.scale_x)
            self.tempo_desde_ultimo_frame = 0.0
            # Avança frame
            self.indice_frame_andando = (self.indice_frame_andando + 1) % len(self.texturas_andando)
            # Aplica a textura
            self.sprite_jogador.texture = self.texturas_andando[self.indice_frame_andando]

        elif self.ultimo_tipo_movimento == 'cima':
            self.sprite_jogador.texture = self.textura_up
        elif self.ultimo_tipo_movimento == 'baixo':
            self.sprite_jogador.texture = self.textura_idle

janela = JanelaJogo()
arcade.run()

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