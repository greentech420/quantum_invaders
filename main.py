import pygame
import sys
import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np

# Pygameの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Quantum Invaders')

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# 敵クラス
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.rect.y += 40

# 弾クラス
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# 量子回路を使用して敵の動きを決定する関数
def quantum_movement():
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # アダマールゲート
    qc.measure(0, 0)
    
    # AerSimulatorを使用して直接シミュレーション
    backend = AerSimulator()
    result = backend.run(qc, shots=1).result()
    counts = result.get_counts()
    
    # '1'の状態が測定されたかどうかを確認
    return '1' in counts

# ゲームクラス
class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.create_enemies()

    def create_enemies(self):
        for row in range(5):
            for column in range(8):
                enemy = Enemy(column * 80 + 100, row * 60 + 50)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
        return True

    def update(self):
        self.all_sprites.update()

        # 量子回路による敵の特殊移動
        if quantum_movement():
            for enemy in self.enemies:
                enemy.speed = random.randint(1, 4)

        # 衝突判定
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 10

        # ゲームオーバー判定
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            return False
        
        return True

    def draw(self):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

# メインゲームループ
def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        running = game.handle_events()
        if not running:
            break

        if not game.update():
            break

        game.draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 