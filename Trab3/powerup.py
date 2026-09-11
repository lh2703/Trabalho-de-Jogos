# powerup.py
import pygame


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((20, 20))

        # Define a cor baseada no tipo
        if self.power_type == "INVENCIBILIDADE":
            self.image.fill((0, 0, 255))  # Quadrado Azul
        elif self.power_type == "VIDA":
            self.image.fill((0, 255, 0))  # Quadrado Verde

        self.rect = self.image.get_rect(center=(x, y))