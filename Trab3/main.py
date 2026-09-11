# main.py
import pygame
import random
import time
from util import EventManager
from player import Player
from bullet import Bullet
from enemy import Enemy
from powerup import PowerUp


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Survivor-like Shooter")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    event_manager = EventManager()

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player(event_manager)
    all_sprites.add(player)

    def on_enemy_spawn(data):
        x = random.choice([-50, 850])
        y = random.randint(0, 600)
        enemy = Enemy(x, y, player)
        all_sprites.add(enemy)
        enemies.add(enemy)

    def on_shoot(data):
        if player.state != "MORTO":
            bullet = Bullet(player.rect.centerx, player.rect.centery, data['x'], data['y'])
            all_sprites.add(bullet)
            bullets.add(bullet)

    def on_powerup_spawn(data):
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        tipo = random.choice(["INVENCIBILIDADE", "VIDA"])
        powerup = PowerUp(x, y, tipo)
        all_sprites.add(powerup)
        powerups.add(powerup)

    event_manager.subscribe("SPAWN_ENEMY", on_enemy_spawn)
    event_manager.subscribe("SHOOT", on_shoot)
    event_manager.subscribe("SPAWN_POWERUP", on_powerup_spawn)

    spawn_timer = 0
    powerup_timer = 0

    next_powerup_target = random.randint(180, 300)

    running = True
    start_time = time.time()
    survival_time = 0

    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    event_manager.emit("SHOOT", {'x': mx, 'y': my})

        if player.state != "MORTO":
            survival_time = time.time() - start_time

            # --- DIFICULDADE PROGRESSIVA ---
            # Começa em 90. A cada 1 segundo sobrevivendo, diminui 1.
            # O limite mínimo (max difficulty) é 20 frames de intervalo.
            current_spawn_delay = max(20, 90 - int(survival_time))

            spawn_timer += 1
            if spawn_timer > current_spawn_delay:
                event_manager.emit("SPAWN_ENEMY")
                spawn_timer = 0

            powerup_timer += 1
            if powerup_timer > next_powerup_target:
                event_manager.emit("SPAWN_POWERUP")
                powerup_timer = 0
                next_powerup_target = random.randint(300, 600)

            player.update(keys)
            enemies.update()
            bullets.update()
            powerups.update()

            for bullet in bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
                for enemy in hit_enemies:
                    enemy.hit()
                    bullet.kill()

            if pygame.sprite.spritecollide(player, enemies, False):
                player.take_damage()

            hit_powerups = pygame.sprite.spritecollide(player, powerups, True)
            for pu in hit_powerups:
                if pu.power_type == "INVENCIBILIDADE":
                    player.make_invincible(5)
                elif pu.power_type == "VIDA":
                    player.add_life()

        # --- Renderização Visual ---
        screen.fill((40, 40, 40))
        all_sprites.draw(screen)

        # --- Interface de Usuário (UI) ---
        if player.state != "MORTO":
            hp_text = font.render(f"Vidas: {player.hp}", True, (255, 255, 255))
            screen.blit(hp_text, (10, 10))

            minutos_vivos = int(survival_time // 60)
            segundos_vivos = int(survival_time % 60)
            tempo_texto = font.render(f"Tempo: {minutos_vivos:02}:{segundos_vivos:02}", True, (255, 255, 255))
            screen.blit(tempo_texto, (650, 10))
        else:
            minutos = int(survival_time // 60)
            segundos = int(survival_time % 60)

            if minutos > 0:
                texto = f"Você sobreviveu por {minutos} minutos e {segundos} segundos"
            else:
                texto = f"Você sobreviveu por {segundos} segundos"

            game_over_text = font.render(texto, True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(400, 300))
            screen.blit(game_over_text, text_rect)

            instrucao = font.render("Aperte ESPAÇO para sair", True, (200, 200, 200))
            instrucao_rect = instrucao.get_rect(center=(400, 350))
            screen.blit(instrucao, instrucao_rect)

            if keys[pygame.K_SPACE]:
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()