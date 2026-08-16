# Inicialização
import pygame
import random
pygame.init()
pygame.font.init()



font = font = pygame.font.Font(None, 40)
Nome = "Luís Henrique"

random.seed(Nome)
x, y =  random.randint(265, 280), random.randint(105, 110)

print(y)

# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH , HEIGHT))

texto = font.render(Nome, True, (0,0,0))
rect = texto.get_rect(center=(WIDTH/2, HEIGHT/2))


#loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # Desenha
        screen.fill((50, 50, 50))
        pygame.draw.rect(screen, (255,255,255), rect)
        screen.blit(texto, rect)
        pygame.display.flip()
