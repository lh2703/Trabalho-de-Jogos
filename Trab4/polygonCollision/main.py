import pygame
import math
from shape import Polygon
from collision import Collide

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini-Golf Vetorial - Polygon Collision")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
font_grande = pygame.font.SysFont(None, 60)


class Bolinha:
    def __init__(self, x, y):
        r = 12
        pontos = []
        for i in range(6):
            angle = math.radians(60 * i)
            pontos.append((x + r * math.cos(angle), y + r * math.sin(angle)))

        self.poly = Polygon(pontos)
        self.vel_x = 0
        self.vel_y = 0
        self.atracao = 0.05  # Fricção / desaceleração do relvado
        self.em_movimento = False

    def move(self, dx, dy):
        for i in range(len(self.poly.points)):
            self.poly.points[i] = (self.poly.points[i][0] + dx, self.poly.points[i][1] + dy)
        self.poly.update_geometry()

    def update(self):
        if not self.em_movimento:
            return

        # Aplica velocidade
        self.move(self.vel_x, self.vel_y)

        # Desaceleração por fricção
        self.vel_x *= 0.98
        self.vel_y *= 0.98

        # Parar se a velocidade for muito baixa
        if math.hypot(self.vel_x, self.vel_y) < 0.2:
            self.vel_x = 0
            self.vel_y = 0
            self.em_movimento = False

        # Ressalto nas paredes do ecrã
        box = self.poly.bounding_box
        if box.left < 0:
            self.vel_x *= -0.8
            self.move(-box.left, 0)
        elif box.right > WIDTH:
            self.vel_x *= -0.8
            self.move(WIDTH - box.right, 0)
        if box.top < 0:
            self.vel_y *= -0.8
            self.move(0, -box.top)
        elif box.bottom > HEIGHT:
            self.vel_y *= -0.8
            self.move(0, HEIGHT - box.bottom)


class AlvoBuraco:
    def __init__(self, pontos):
        self.poly = Polygon(pontos)


# --- INICIALIZAÇÃO DO NÍVEL ---
obstaculos = [
    Polygon([(200, 150), (400, 100), (350, 250), (250, 200)]),  # Obstáculo central
    Polygon([(500, 300), (650, 250), (700, 400), (550, 450)]),  # Obstáculo direito
    Polygon([(100, 400), (300, 450), (200, 550)])  # Obstáculo inferior esquerdo
]

# O Buraco do Golfe (Zona Alvo)
buraco = AlvoBuraco([(650, 80), (720, 80), (720, 130), (650, 130)])

bolinha = Bolinha(100, 500)
pontos_total = 0
tacadas = 5
estado = "APONTAR"  # "APONTAR", "A VOAR", "VITORIA", "GAME_OVER"
mouse_inicial = (0, 0)

running = True
while running:
    screen.fill((40, 120, 60))  # Cor verde relvado

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if estado == "APONTAR" and not bolinha.em_movimento:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Verifica se clicou perto da bolinha
                    box = bolinha.poly.bounding_box
                    if box.collidepoint(event.pos):
                        mouse_inicial = event.pos
                        estado = "ARRASTANDO"

        elif estado == "ARRASTANDO":
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_final = event.pos
                    # Calcula o vetor de impulso baseado na distância do arrastamento (estilingue)
                    dx = mouse_inicial[0] - mouse_final[0]
                    dy = mouse_inicial[1] - mouse_final[1]

                    bolinha.vel_x = dx * 0.15
                    bolinha.vel_y = dy * 0.15
                    bolinha.em_movimento = True
                    tacadas -= 1
                    estado = "A VOAR"

        elif estado in ["VITORIA", "GAME_OVER"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    bolinha = Bolinha(100, 500)
                    tacadas = 5
                    pontos_total = 0
                    estado = "APONTAR"
                elif event.key == pygame.K_q:
                    running = False

    # --- LÓGICA E FÍSICA ---
    if bolinha.em_movimento:
        bolinha.update()

        # 1. Colisão com Obstáculos Sólidos (Reflete o movimento)
        for obs in obstaculos:
            colisao = Collide.polygon(bolinha.poly, obs)
            if colisao:
                shape_bola, shape_obs = colisao

                cx_bola = sum(p[0] for p in shape_bola.points) / len(shape_bola.points)
                cy_bola = sum(p[1] for p in shape_bola.points) / len(shape_bola.points)
                cx_obs = sum(p[0] for p in shape_obs.points) / len(shape_obs.points)
                cy_obs = sum(p[1] for p in shape_obs.points) / len(shape_obs.points)

                dx, dy = cx_bola - cx_obs, cy_bola - cy_obs
                dist = math.hypot(dx, dy)
                if dist > 0:
                    nx, ny = dx / dist, dy / dist
                    dot = bolinha.vel_x * nx + bolinha.vel_y * ny
                    bolinha.vel_x = (bolinha.vel_x - 2 * dot * nx) * 0.8
                    bolinha.vel_y = (bolinha.vel_y - 2 * dot * ny) * 0.8
                    bolinha.move(nx * 4, ny * 4)

        # 2. Verifica se entrou no Buraco (Zona Alvo)
        if Collide.polygon(bolinha.poly, buraco.poly):
            if math.hypot(bolinha.vel_x, bolinha.vel_y) < 4:  # Precisa de entrar com calma
                pontos_total += 500 + (tacadas * 100)
                estado = "VITORIA"

        # Se parou e não marcou, volta a permitir apontar
        if not bolinha.em_movimento and estado == "A VOAR":
            if tacadas <= 0:
                estado = "GAME_OVER"
            else:
                estado = "APONTAR"

    # --- DESENHO ---
    # Desenhar o Buraco (Alvo)
    pygame.draw.polygon(screen, (20, 60, 30), buraco.poly.points)
    pygame.draw.polygon(screen, (255, 215, 0), buraco.poly.points, 3)

    # Desenhar Obstáculos
    for obs in obstaculos:
        obs.draw(screen)

    # Desenhar a Bolinha
    pygame.draw.polygon(screen, (255, 255, 255), bolinha.poly.points)
    pygame.draw.polygon(screen, (0, 0, 0), bolinha.poly.points, 2)

    # Linha do Estilingue se o jogador estiver a arrastar
    if estado == "ARRASTANDO":
        mouse_atual = pygame.mouse.get_pos()
        bola_centro = (bolinha.poly.bounding_box.centerx, bolinha.poly.bounding_box.centery)
        pygame.draw.line(screen, (255, 255, 0), bola_centro, mouse_atual, 3)

    # Interface (UI)
    txt_info = font.render(f"Tacadas restantes: {tacadas} | Pontos: {pontos_total}", True, (255, 255, 255))
    screen.blit(txt_info, (20, 20))

    if estado == "VITORIA":
        txt_v = font_grande.render("BOLA NO BURACO! 🎉", True, (255, 255, 0))
        txt_r = font.render("Prima [R] para o próximo nível ou [Q] para sair", True, (255, 255, 255))
        screen.blit(txt_v, (WIDTH // 2 - txt_v.get_width() // 2, HEIGHT // 3))
        screen.blit(txt_r, (WIDTH // 2 - txt_r.get_width() // 2, HEIGHT // 2))

    elif estado == "GAME_OVER":
        txt_g = font_grande.render("FIM DE TACADAS", True, (255, 50, 50))
        txt_r = font.render("Prima [R] para tentar novamente ou [Q] para sair", True, (255, 255, 255))
        screen.blit(txt_g, (WIDTH // 2 - txt_g.get_width() // 2, HEIGHT // 3))
        screen.blit(txt_r, (WIDTH // 2 - txt_r.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()