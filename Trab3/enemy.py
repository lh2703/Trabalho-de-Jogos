# enemy.py
import pygame
import math
import time


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))  # Inimigo Vermelho
        self.rect = self.image.get_rect(center=(x, y))
        self.player = player
        self.speed = 2
        self.state = "PERSEGUINDO"
        self.stun_time = 0
        self.hp = 2  # O inimigo agora precisa tomar 2 tiros para morrer

    def update(self):
        # Se estiver atordoado, conta o tempo para voltar ao normal
        if self.state == "ATORDOADO":
            if time.time() - self.stun_time > 0.5:
                self.state = "PERSEGUINDO"
                self.image.fill((255, 0, 0))  # Volta a ficar vermelho
            return  # Impede que ande enquanto está atordoado

        # Se estiver perseguindo, vai na direção do jogador
        if self.state == "PERSEGUINDO":
            angle = math.atan2(self.player.rect.y - self.rect.y, self.player.rect.x - self.rect.x)
            self.rect.x += math.cos(angle) * self.speed
            self.rect.y += math.sin(angle) * self.speed

    def hit(self):
        self.hp -= 1  # Tira 1 de vida

        if self.hp <= 0:
            self.kill()  # Destrói o objeto permanentemente
        else:
            # Entra no estado atordoado
            self.state = "ATORDOADO"
            self.stun_time = time.time()
            self.image.fill((100, 100, 100))  # Fica cinza indicando dano