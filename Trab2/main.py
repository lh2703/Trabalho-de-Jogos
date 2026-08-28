import pygame
import sys
import os
from grid import Grid

pygame.init()
pygame.font.init()

LARGURA = 800
ALTURA = 600
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Trabalho 2 - Sokoban")
clock = pygame.time.Clock()

fonte = pygame.font.SysFont("Arial", 20, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 32, bold=True)
fonte_titulo = pygame.font.SysFont("Arial", 42, bold=True)

PASTA_PATO = os.path.join("images", "duck")


def carregar_img(nome, tamanho=(40, 40)):
    caminho = os.path.join(PASTA_PATO, nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(img, tamanho)
    except Exception:
        s = pygame.Surface(tamanho, pygame.SRCALPHA)
        pygame.draw.circle(s, (240, 200, 0), (tamanho[0] // 2, tamanho[1] // 2), 15)
        return s


sprites = {
    'base': carregar_img("base.png"),
    'step': carregar_img("step.png"),
    'crouch': carregar_img("crouch.png"),
    'blink': carregar_img("blink.png"),
    'quack': carregar_img("quack.png"),
    'wing': carregar_img("wing.png"),
}

MAPAS = [
    [
        "#######",
        "#     #",
        "# @   #",
        "# $ . #",
        "# $ . #",
        "#     #",
        "#######"
    ],
    [
        "#######",
        "#     #",
        "#  .  #",
        "# $ $ #",
        "#  @  #",
        "#  .  #",
        "#######"
    ],
    [
        "########",
        "#      #",
        "#  . . #",
        "# $ $  #",
        "#  @ $ #",
        "#   .  #",
        "#      #",
        "########"
    ]
]

nivel_atual = 0
jogo_finalizado = False


def criar_fase(idx):
    layout = MAPAS[idx]
    w = len(layout[0]) * 50
    h = len(layout) * 50
    start_x = (LARGURA - w) // 2
    start_y = (ALTURA - h) // 2 + 20
    return Grid(start_x, start_y, layout, sprites)


grid = criar_fase(nivel_atual)

btn_reset = pygame.Rect(LARGURA - 160, 20, 130, 35)
btn_prox = pygame.Rect(LARGURA - 160, 65, 130, 35)
btn_recomecar = pygame.Rect(LARGURA // 2 - 100, ALTURA // 2 + 50, 200, 45)

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_pos = pygame.mouse.get_pos()

                if jogo_finalizado:
                    if btn_recomecar.collidepoint(m_pos):
                        nivel_atual = 0
                        jogo_finalizado = False
                        grid = criar_fase(nivel_atual)
                else:
                    if btn_reset.collidepoint(m_pos):
                        grid = criar_fase(nivel_atual)
                    elif btn_prox.collidepoint(m_pos) and grid.venceu:
                        if nivel_atual + 1 < len(MAPAS):
                            nivel_atual += 1
                            grid = criar_fase(nivel_atual)
                        else:
                            jogo_finalizado = True
                    else:
                        grid.clique_mouse(m_pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if jogo_finalizado:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_r]:
                    nivel_atual = 0
                    jogo_finalizado = False
                    grid = criar_fase(nivel_atual)
            else:
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    grid.tentar_mover(-1, 0)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    grid.tentar_mover(1, 0)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    grid.tentar_mover(0, -1)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    grid.tentar_mover(0, 1)
                elif event.key == pygame.K_r:
                    grid = criar_fase(nivel_atual)
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN] and grid.venceu:
                    if nivel_atual + 1 < len(MAPAS):
                        nivel_atual += 1
                        grid = criar_fase(nivel_atual)
                    else:
                        jogo_finalizado = True

    if not jogo_finalizado:
        grid.update(dt)

    screen.fill((25, 25, 30))

    if jogo_finalizado:
        t1 = fonte_titulo.render("Jogo Finalizado!", True, (240, 200, 50))
        t2 = fonte_grande.render("Você completou todas as fases.", True, (200, 200, 200))

        screen.blit(t1, (LARGURA // 2 - t1.get_width() // 2, ALTURA // 2 - 100))
        screen.blit(t2, (LARGURA // 2 - t2.get_width() // 2, ALTURA // 2 - 30))

        pygame.draw.rect(screen, (50, 130, 70), btn_recomecar, border_radius=6)
        pygame.draw.rect(screen, (90, 200, 110), btn_recomecar, 2, border_radius=6)

        txt_b = fonte.render("Jogar De Novo", True, (255, 255, 255))
        screen.blit(txt_b,
                    (btn_recomecar.centerx - txt_b.get_width() // 2, btn_recomecar.centery - txt_b.get_height() // 2))

    else:
        grid.draw(screen)

        txt_n = fonte.render(f"Fase: {nivel_atual + 1}/{len(MAPAS)}", True, (200, 200, 200))
        txt_m = fonte.render(f"Movimentos: {grid.movimentos}", True, (200, 200, 200))
        screen.blit(txt_n, (25, 20))
        screen.blit(txt_m, (25, 45))

        pygame.draw.rect(screen, (60, 65, 75), btn_reset, border_radius=5)
        pygame.draw.rect(screen, (100, 105, 120), btn_reset, 1, border_radius=5)
        txt_r = fonte.render("Reiniciar (R)", True, (255, 255, 255))
        screen.blit(txt_r, (btn_reset.x + 12, btn_reset.y + 6))

        if grid.venceu:
            bg_vitoria = pygame.Rect(LARGURA // 2 - 160, ALTURA - 85, 320, 50)
            pygame.draw.rect(screen, (40, 120, 60), bg_vitoria, border_radius=6)
            pygame.draw.rect(screen, (80, 200, 110), bg_vitoria, 2, border_radius=6)

            txt_v = fonte_grande.render("Fase Concluída!", True, (255, 255, 255))
            screen.blit(txt_v, (bg_vitoria.centerx - txt_v.get_width() // 2, bg_vitoria.y + 8))

            pygame.draw.rect(screen, (40, 110, 70), btn_prox, border_radius=5)
            pygame.draw.rect(screen, (80, 180, 110), btn_prox, 1, border_radius=5)

            lbl = "Finalizar" if nivel_atual + 1 == len(MAPAS) else "Próximo >"
            txt_p = fonte.render(lbl, True, (255, 255, 255))
            screen.blit(txt_p, (btn_prox.centerx - txt_p.get_width() // 2, btn_prox.y + 6))

    pygame.display.flip()