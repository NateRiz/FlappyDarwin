import pygame
from random import randint
from time import time, sleep
from enum import Enum


class State(Enum):
    READY = 0
    PLAYING = 1
    GAMEOVER = 2


class Pipe:
    def __init__(self, height, width):
        gap_size = 150
        ht = randint(00, height - gap_size)
        self.top = pygame.rect.Rect(width, 0, 100, ht)

        hb = ht + gap_size
        self.bot = pygame.rect.Rect(width, hb, 100, height - hb)


class FlappyDarwin:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 30
        self.GRAVITY = .981
        self.VELOCITY_INITIAL = -10
        self.QUIT_SIGNAL = False
        self.game_state = State.READY

        self.pipe_speed = 3
        self.game_start_time = time()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pipes = []
        self.bird = pygame.rect.Rect(16, self.HEIGHT // 2, 32, 32)
        self.velocity = 0
        self.last_jump_time = 0

    def start(self):
        clock = pygame.time.Clock()
        self.last_jump_time = time()
        self.game_start_time = time()
        self.game_state = State.READY

        while not self.QUIT_SIGNAL:
            while self.game_state != State.READY:
                sleep(1)

            self.game_state = State.PLAYING
            while self.game_state == State.PLAYING:
                clock.tick(self.FPS)
                self.update()
                self.draw()
                self.poll()

    def poll(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.QUIT_SIGNAL = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump()

    def update(self):
        self.spawn_pipe()
        for i in reversed(range(len(self.pipes))):
            self.pipes[i].top.x -= self.pipe_speed
            if self.pipes[i].top.right < 0:
                del self.pipes[i]

        self.velocity += self.GRAVITY
        self.bird.y += self.velocity

        self.check_dead()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.top, 3)
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.bot, 3)

        pygame.draw.rect(self.screen, (0, 255, 0), self.bird, 3)

        pygame.display.flip()

    def spawn_pipe(self):
        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > 200:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))

    def jump(self):
        self.velocity = self.VELOCITY_INITIAL

    def restart(self):
        self.pipes.clear()
        self.bird = pygame.rect.Rect(16, self.HEIGHT // 2, 32, 32)
        self.last_jump_time = time()
        self.game_start_time = time()
        self.game_state = State.READY

    def check_dead(self):
        if self.bird.bottom >= self.HEIGHT or self.bird.top <= 0:
            self.game_state = State.GAMEOVER
        for pipe in self.pipes:
            if pipe.top.colliderect(self.bird) or pipe.bot.colliderect(self.bird):
                self.game_state = State.GAMEOVER
                break
