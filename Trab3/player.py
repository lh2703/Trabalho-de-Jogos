# player.py
import pygame
import time


class Player(pygame.sprite.Sprite):
    def __init__(self, event_manager):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 255, 0))  # Pato Amarelo
        self.rect = self.image.get_rect(center=(400, 300))
        self.speed = 5
        self.state = "NORMAL"

        self.hp = 3  # 3 Vidas
        self.invincible_time = 0
        self.invincible_duration = 2

        self.event_manager = event_manager

    def update(self, keys):
        if self.state == "MORTO":
            self.image.set_alpha(0)  # Fica invisível quando morre
            return

        # Controle da invencibilidade
        if self.state == "INVENCIVEL" and time.time() - self.invincible_time > self.invincible_duration:
            self.state = "NORMAL"
            self.image.set_alpha(255)

        # Pisca na tela enquanto está invencível
        if self.state == "INVENCIVEL":
            alpha = 128 if int(time.time() * 10) % 2 == 0 else 255
            self.image.set_alpha(alpha)

        # Movimentação
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed

        self.rect.x += dx
        self.rect.y += dy

    def take_damage(self):
        if self.state == "NORMAL":
            self.hp -= 1
            if self.hp <= 0:
                self.state = "MORTO"
            else:
                self.state = "INVENCIVEL"
                self.invincible_duration = 2  # Invencibilidade de 2s após dano
                self.invincible_time = time.time()

    def add_life(self):
        self.hp += 1

    def make_invincible(self, duration):
        self.state = "INVENCIVEL"
        self.invincible_duration = duration  # Aqui entram os 5s do power-up
        self.invincible_time = time.time()