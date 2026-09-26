import pygame
import math

from shape import Polygon
from collision import Collide


pygame.init()


WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "Mini-Golf Vetorial - Polygon Collision"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)
font_grande = pygame.font.SysFont(None, 60)


# =========================================================
# BOLINHA
# =========================================================

class Bolinha:

    def __init__(self, x, y):

        r = 12

        pontos = []

        for i in range(6):

            angle = math.radians(60 * i)

            pontos.append((
                x + r * math.cos(angle),
                y + r * math.sin(angle)
            ))

        self.poly = Polygon(pontos)

        self.vel_x = 0
        self.vel_y = 0

        self.atracao = 0.05

        self.em_movimento = False

    # -----------------------------------------------------
    # Move
    # -----------------------------------------------------

    def move(self, dx, dy):

        for i in range(len(self.poly.points)):

            self.poly.points[i] = (
                self.poly.points[i][0] + dx,
                self.poly.points[i][1] + dy
            )

        self.poly.update_geometry()

    # -----------------------------------------------------
    # Update da física
    # -----------------------------------------------------

    def update(self, obstaculos):

        if not self.em_movimento:
            return

        # -------------------------------------------------
        # Calcula quantos subpassos serão necessários
        #
        # Se a bola estiver andando 20 pixels por frame,
        # por exemplo, serão feitos aproximadamente 10
        # movimentos de 2 pixels.
        # -------------------------------------------------

        velocidade = math.hypot(
            self.vel_x,
            self.vel_y
        )

        subpassos = max(
            1,
            math.ceil(velocidade / 2.0)
        )

        dx = self.vel_x / subpassos
        dy = self.vel_y / subpassos

        for _ in range(subpassos):

            # ---------------------------------------------
            # Movimento pequeno
            # ---------------------------------------------

            self.move(dx, dy)

            colisao_detectada = False

            # ---------------------------------------------
            # Colisão com obstáculos
            # ---------------------------------------------

            for obs in obstaculos:

                colisao = Collide.polygon_mtv(
                    self.poly,
                    obs
                )

                if colisao is None:
                    continue

                shape_bola, shape_obs, normal, depth = colisao

                colisao_detectada = True

                # -----------------------------------------
                # Volta o último movimento
                # -----------------------------------------

                self.move(-dx, -dy)

                # -----------------------------------------
                # Recalcula a colisão depois de voltar
                #
                # Isso evita empurrar a bola para dentro
                # da parede.
                # -----------------------------------------

                colisao = Collide.polygon_mtv(
                    self.poly,
                    obs
                )

                if colisao is not None:

                    _, _, normal, depth = colisao

                # -----------------------------------------
                # Rebate a velocidade
                #
                # Fórmula:
                #
                # v' = v - 2(v.n)n
                # -----------------------------------------

                dot = (
                    self.vel_x * normal[0]
                    +
                    self.vel_y * normal[1]
                )

                # Só rebate se estiver indo em direção
                # à parede.
                if dot < 0:

                    self.vel_x = (
                        self.vel_x
                        - 2 * dot * normal[0]
                    ) * 0.80

                    self.vel_y = (
                        self.vel_y
                        - 2 * dot * normal[1]
                    ) * 0.80

                # -----------------------------------------
                # Pequeno empurrão para fora da parede
                # -----------------------------------------

                self.move(
                    normal[0] * (depth + 0.5),
                    normal[1] * (depth + 0.5)
                )

                # -----------------------------------------
                # Atualiza dx/dy porque a velocidade
                # mudou depois da colisão
                # -----------------------------------------

                velocidade = math.hypot(
                    self.vel_x,
                    self.vel_y
                )

                if velocidade > 0:

                    # O restante do frame continuará
                    # usando a nova velocidade.
                    restante = max(
                        1,
                        subpassos
                    )

                    dx = self.vel_x / restante
                    dy = self.vel_y / restante

                break

            # ---------------------------------------------
            # Colisão com bordas da tela
            # ---------------------------------------------

            box = self.poly.bounding_box

            if box.left < 0:

                self.move(-box.left, 0)

                if self.vel_x < 0:
                    self.vel_x *= -0.80

            elif box.right > WIDTH:

                self.move(
                    WIDTH - box.right,
                    0
                )

                if self.vel_x > 0:
                    self.vel_x *= -0.80

            box = self.poly.bounding_box

            if box.top < 0:

                self.move(0, -box.top)

                if self.vel_y < 0:
                    self.vel_y *= -0.80

            elif box.bottom > HEIGHT:

                self.move(
                    0,
                    HEIGHT - box.bottom
                )

                if self.vel_y > 0:
                    self.vel_y *= -0.80

        # -------------------------------------------------
        # Atrito
        # -------------------------------------------------

        self.vel_x *= 0.98
        self.vel_y *= 0.98

        # -------------------------------------------------
        # Para a bola quando estiver muito devagar
        # -------------------------------------------------

        if math.hypot(
            self.vel_x,
            self.vel_y
        ) < 0.2:

            self.vel_x = 0
            self.vel_y = 0

            self.em_movimento = False


# =========================================================
# BURACO
# =========================================================

class AlvoBuraco:

    def __init__(self, pontos):

        self.poly = Polygon(pontos)


# =========================================================
# NÍVEIS
# =========================================================

niveis = [

    {
        "inicio": (100, 500),

        "buraco": [
            (650, 80),
            (720, 80),
            (720, 130),
            (650, 130)
        ],

        "obstaculos": [

            Polygon([
                (200, 150),
                (400, 100),
                (350, 250),
                (250, 200)
            ]),

            Polygon([
                (500, 300),
                (650, 250),
                (700, 400),
                (550, 450)
            ]),

            Polygon([
                (100, 400),
                (300, 450),
                (200, 550)
            ])

        ]
    },

    {
        "inicio": (400, 520),

        "buraco": [
            (360, 50),
            (440, 50),
            (440, 90),
            (360, 90)
        ],

        "obstaculos": [

            Polygon([
                (250, 200),
                (550, 200),
                (400, 150)
            ]),

            Polygon([
                (150, 350),
                (300, 300),
                (250, 450)
            ]),

            Polygon([
                (500, 300),
                (650, 450),
                (550, 450)
            ]),

            Polygon([
                (350, 350),
                (450, 350),
                (400, 400)
            ])

        ]
    },

    {
        "inicio": (100, 100),

        "buraco": [
            (650, 480),
            (730, 480),
            (730, 540),
            (650, 540)
        ],

        "obstaculos": [

            Polygon([
                (300, 0),
                (350, 400),
                (250, 400)
            ]),

            Polygon([
                (500, 200),
                (550, 600),
                (450, 600)
            ]),

            Polygon([
                (100, 250),
                (200, 280),
                (150, 320)
            ])

        ]
    }

]


# =========================================================
# ESTADO DO JOGO
# =========================================================

nivel_atual = 0

pontos_total = 0

tacadas = 5

estado = "APONTAR"

mouse_inicial = (0, 0)


# =========================================================
# CARREGAR NÍVEL
# =========================================================

def carregar_nivel(idx):

    global bolinha
    global buraco
    global obstaculos
    global tacadas
    global estado

    dados = niveis[idx]

    bolinha = Bolinha(
        dados["inicio"][0],
        dados["inicio"][1]
    )

    buraco = AlvoBuraco(
        dados["buraco"]
    )

    obstaculos = dados["obstaculos"]

    tacadas = 5

    estado = "APONTAR"


carregar_nivel(nivel_atual)


# =========================================================
# LOOP PRINCIPAL
# =========================================================

running = True


while running:

    screen.fill((40, 120, 60))

    # =====================================================
    # EVENTOS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # APONTANDO
        # -------------------------------------------------

        if estado == "APONTAR" and not bolinha.em_movimento:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    box = bolinha.poly.bounding_box

                    if box.collidepoint(event.pos):

                        mouse_inicial = event.pos

                        estado = "ARRASTANDO"

        # -------------------------------------------------
        # ARRASTANDO
        # -------------------------------------------------

        elif estado == "ARRASTANDO":

            if event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1:

                    mouse_final = event.pos

                    dx = (
                        mouse_inicial[0]
                        - mouse_final[0]
                    )

                    dy = (
                        mouse_inicial[1]
                        - mouse_final[1]
                    )

                    # -------------------------------------
                    # Limita a força máxima
                    #
                    # Evita valores absurdamente grandes,
                    # mas ainda permite tacadas fortes.
                    # -------------------------------------

                    forca = 0.25

                    bolinha.vel_x = dx * forca
                    bolinha.vel_y = dy * forca

                    bolinha.em_movimento = True

                    tacadas -= 1

                    estado = "A VOAR"

        # -------------------------------------------------
        # VITÓRIA DO NÍVEL
        # -------------------------------------------------

        elif estado == "VITORIA_NIVEL":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    nivel_atual += 1

                    if nivel_atual < len(niveis):

                        carregar_nivel(
                            nivel_atual
                        )

                    else:

                        estado = "JOGO_COMPLETO"

                elif event.key == pygame.K_q:

                    running = False

        # -------------------------------------------------
        # GAME OVER / JOGO COMPLETO
        # -------------------------------------------------

        elif estado in [
            "GAME_OVER",
            "JOGO_COMPLETO"
        ]:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    nivel_atual = 0

                    pontos_total = 0

                    carregar_nivel(
                        nivel_atual
                    )

                elif event.key == pygame.K_q:

                    running = False

    # =====================================================
    # FÍSICA
    # =====================================================

    if bolinha.em_movimento:

        bolinha.update(obstaculos)

        # ---------------------------------------------
        # Verifica buraco
        # ---------------------------------------------

        if Collide.polygon(
            bolinha.poly,
            buraco.poly
        ):

            if math.hypot(
                bolinha.vel_x,
                bolinha.vel_y
            ) < 4:

                pontos_total += (
                    500
                    + tacadas * 100
                )

                bolinha.vel_x = 0
                bolinha.vel_y = 0
                bolinha.em_movimento = False

                estado = "VITORIA_NIVEL"

    # =====================================================
    # FIM DAS TACADAS
    # =====================================================

    if (
        not bolinha.em_movimento
        and estado == "A VOAR"
    ):

        if tacadas <= 0:

            estado = "GAME_OVER"

        else:

            estado = "APONTAR"

    # =====================================================
    # DESENHO DO BURACO
    # =====================================================

    pygame.draw.polygon(
        screen,
        (20, 60, 30),
        buraco.poly.points
    )

    pygame.draw.polygon(
        screen,
        (255, 215, 0),
        buraco.poly.points,
        3
    )

    # =====================================================
    # DESENHO DOS OBSTÁCULOS
    # =====================================================

    for obs in obstaculos:

        obs.draw(screen)

    # =====================================================
    # DESENHO DA BOLA
    # =====================================================

    pygame.draw.polygon(
        screen,
        (255, 255, 255),
        bolinha.poly.points
    )

    pygame.draw.polygon(
        screen,
        (0, 0, 0),
        bolinha.poly.points,
        2
    )

    # =====================================================
    # LINHA DE DIREÇÃO
    # =====================================================

    if estado == "ARRASTANDO":

        mouse_atual = pygame.mouse.get_pos()

        bola_centro = (
            bolinha.poly.bounding_box.centerx,
            bolinha.poly.bounding_box.centery
        )

        pygame.draw.line(
            screen,
            (255, 255, 0),
            bola_centro,
            mouse_atual,
            3
        )

    # =====================================================
    # INFORMAÇÕES
    # =====================================================

    txt_info = font.render(
        f"Nível: {nivel_atual + 1}/{len(niveis)} | "
        f"Tacadas: {tacadas} | "
        f"Pontos: {pontos_total}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        txt_info,
        (20, 20)
    )

    # =====================================================
    # VITÓRIA DO NÍVEL
    # =====================================================

    if estado == "VITORIA_NIVEL":

        txt_v = font_grande.render(
            "Nível Concluído!",
            True,
            (255, 255, 0)
        )

        txt_r = font.render(
            "Prima [R] para avançar de nível ou [Q] para sair",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt_v,
            (
                WIDTH // 2
                - txt_v.get_width() // 2,
                HEIGHT // 3
            )
        )

        screen.blit(
            txt_r,
            (
                WIDTH // 2
                - txt_r.get_width() // 2,
                HEIGHT // 2
            )
        )

    # =====================================================
    # JOGO COMPLETO
    # =====================================================

    elif estado == "JOGO_COMPLETO":

        txt_c = font_grande.render(
            "PARABÉNS! FINALIZOU O JOGO!",
            True,
            (255, 215, 0)
        )

        txt_p = font.render(
            f"Pontuação Final: {pontos_total}",
            True,
            (255, 255, 255)
        )

        txt_r = font.render(
            "Aperte [R] para reiniciar ou [Q] para sair",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt_c,
            (
                WIDTH // 2
                - txt_c.get_width() // 2,
                HEIGHT // 3
            )
        )

        screen.blit(
            txt_p,
            (
                WIDTH // 2
                - txt_p.get_width() // 2,
                HEIGHT // 2 - 20
            )
        )

        screen.blit(
            txt_r,
            (
                WIDTH // 2
                - txt_r.get_width() // 2,
                HEIGHT // 2 + 40
            )
        )

    # =====================================================
    # GAME OVER
    # =====================================================

    elif estado == "GAME_OVER":

        txt_g = font_grande.render(
            "FIM DAS TACADAS",
            True,
            (255, 50, 50)
        )

        txt_r = font.render(
            "Aperte [R] para tentar novamente ou [Q] para sair",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt_g,
            (
                WIDTH // 2
                - txt_g.get_width() // 2,
                HEIGHT // 3
            )
        )

        screen.blit(
            txt_r,
            (
                WIDTH // 2
                - txt_r.get_width() // 2,
                HEIGHT // 2
            )
        )

    # =====================================================
    # ATUALIZA TELA
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()