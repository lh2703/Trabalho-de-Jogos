import pygame
from abc import ABC, abstractmethod

CELL_SIZE = 50


class obj(ABC):
    def __init__(self, x, y, sprites=None):
        self.x = x
        self.y = y
        self.sprites = sprites if sprites is not None else []

    def draw(self, screen):
        if self.sprites:
            screen.blit(self.sprites[0], (self.x, self.y))

    @abstractmethod
    def update(self, dt):
        pass


class Cell(obj):
    def __init__(self, x, y, cell_type=' '):
        super().__init__(x, y, [])
        self.cell_type = cell_type
        self.rect = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, (45, 45, 55), self.rect)
        pygame.draw.rect(screen, (35, 35, 45), self.rect, 1)

        if self.cell_type == '#':
            pygame.draw.rect(screen, (65, 75, 90), self.rect)
            pygame.draw.rect(screen, (90, 100, 120), self.rect, 2)

        elif self.cell_type == '.':
            pygame.draw.circle(screen, (70, 190, 110), self.rect.center, 8)

        elif self.cell_type in ['$', '*']:
            m = 6
            box_rect = pygame.Rect(self.x + m, self.y + m, CELL_SIZE - 2 * m, CELL_SIZE - 2 * m)
            cor = (220, 170, 40) if self.cell_type == '*' else (150, 90, 40)
            borda = (240, 220, 100) if self.cell_type == '*' else (90, 50, 20)

            pygame.draw.rect(screen, cor, box_rect, border_radius=4)
            pygame.draw.rect(screen, borda, box_rect, 2, border_radius=4)
            pygame.draw.line(screen, borda, box_rect.topleft, box_rect.bottomright, 2)
            pygame.draw.line(screen, borda, box_rect.bottomleft, box_rect.topright, 2)

    def update(self, dt):
        pass


class Player(obj):
    def __init__(self, grid_col, grid_row, sprites_dict, offset_x, offset_y):
        self.col = grid_col
        self.row = grid_row
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.sprites_dict = sprites_dict

        super().__init__(
            offset_x + grid_col * CELL_SIZE,
            offset_y + grid_row * CELL_SIZE,
            list(sprites_dict.values())
        )

        self.virado_esquerda = False
        self.tempo_anim = 0.0
        self.frame_atual = 'base'
        self.tocando_som = False
        self.tempo_som = 0.0

    def mover(self, col, row, dx):
        self.col = col
        self.row = row
        self.x = self.offset_x + col * CELL_SIZE
        self.y = self.offset_y + row * CELL_SIZE
        if dx < 0:
            self.virado_esquerda = True
        elif dx > 0:
            self.virado_esquerda = False

    def update(self, dt):
        self.tempo_anim += dt

        if self.tocando_som:
            self.frame_atual = 'quack'
            self.tempo_som -= dt
            if self.tempo_som <= 0:
                self.tocando_som = False
        else:
            ciclo = int(self.tempo_anim * 4) % 10
            if ciclo in [0, 1]:
                self.frame_atual = 'step'
            elif ciclo == 5:
                self.frame_atual = 'blink'
            elif ciclo == 8:
                self.frame_atual = 'wing'
            else:
                self.frame_atual = 'base'

    def draw(self, screen):
        sprite = self.sprites_dict.get(self.frame_atual, self.sprites_dict['base'])
        if self.virado_esquerda:
            sprite = pygame.transform.flip(sprite, True, False)

        ox = (CELL_SIZE - sprite.get_width()) // 2
        oy = (CELL_SIZE - sprite.get_height()) // 2
        screen.blit(sprite, (self.x + ox, self.y + oy))


class Grid(obj):
    def __init__(self, x, y, layout, sprites_dict):
        super().__init__(x, y, [])
        self.linhas = len(layout)
        self.colunas = len(layout[0])
        self.matriz = []
        self.sprites_dict = sprites_dict
        self.movimentos = 0
        self.venceu = False

        pos_pato = (0, 0)

        for r in range(self.linhas):
            linha = []
            for c in range(self.colunas):
                char = layout[r][c]
                cx = x + c * CELL_SIZE
                cy = y + r * CELL_SIZE

                if char == '@':
                    tipo = ' '
                    pos_pato = (c, r)
                elif char == '+':
                    tipo = '.'
                    pos_pato = (c, r)
                else:
                    tipo = char

                linha.append(Cell(cx, cy, tipo))
            self.matriz.append(linha)

        self.player = Player(pos_pato[0], pos_pato[1], sprites_dict, x, y)

    def pos_valida(self, c, r):
        return 0 <= r < self.linhas and 0 <= c < self.colunas

    def tentar_mover(self, dx, dy):
        if self.venceu:
            return False

        nc = self.player.col + dx
        nr = self.player.row + dy

        if not self.pos_valida(nc, nr):
            return False

        celula_alvo = self.matriz[nr][nc]

        if celula_alvo.cell_type == '#':
            return False

        if celula_alvo.cell_type in ['$', '*']:
            proxc = nc + dx
            proxr = nr + dy

            if not self.pos_valida(proxc, proxr):
                return False

            destino_caixa = self.matriz[proxr][proxc]
            if destino_caixa.cell_type in [' ', '.']:
                destino_caixa.cell_type = '*' if destino_caixa.cell_type == '.' else '$'
                celula_alvo.cell_type = '.' if celula_alvo.cell_type == '*' else ' '

                self.player.mover(nc, nr, dx)
                self.player.tocando_som = True
                self.player.tempo_som = 0.2
                self.movimentos += 1
                self.checar_vitoria()
                return True
            return False

        if celula_alvo.cell_type in [' ', '.']:
            self.player.mover(nc, nr, dx)
            self.movimentos += 1
            return True

        return False

    def clique_mouse(self, pos):
        mx, my = pos
        c = (mx - self.x) // CELL_SIZE
        r = (my - self.y) // CELL_SIZE

        if self.pos_valida(c, r):
            dx = c - self.player.col
            dy = r - self.player.row
            if abs(dx) + abs(dy) == 1:
                self.tentar_mover(dx, dy)

    def checar_vitoria(self):
        for r in range(self.linhas):
            for c in range(self.colunas):
                if self.matriz[r][c].cell_type == '$':
                    return False
        self.venceu = True
        return True

    def update(self, dt):
        for linha in self.matriz:
            for c in linha:
                c.update(dt)
        self.player.update(dt)

    def draw(self, screen):
        for linha in self.matriz:
            for c in linha:
                c.draw(screen)
        self.player.draw(screen)