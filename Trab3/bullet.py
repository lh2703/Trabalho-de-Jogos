# bullet.py
import pygame
import math


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))

        # Calcula a direção do tiro
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * 10
        self.dy = math.sin(angle) * 10

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # Destrói o projétil se sair da tela
        if self.rect.x < 0 or self.rect.x > 800 or self.rect.y < 0 or self.rect.y > 600:
            self.kill()