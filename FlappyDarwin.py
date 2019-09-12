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
        self.passed = False
        gap_size = 150
        ht = randint(00, height - gap_size)
        self.top = pygame.rect.Rect(width, 0, 100, ht)

        hb = ht + gap_size
        self.bot = pygame.rect.Rect(width, hb, 100, height - hb)


class Bird:
    def __init__(self):
        self.VELOCITY_INITIAL = -10

        self.rect = pygame.rect.Rect(16, 300+randint(-3,3), 32, 32)
        self.fitness = 0
        self.velocity = self.VELOCITY_INITIAL
        self.dead = False


class FlappyDarwin:
    def __init__(self, population=1):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 30
        if population>1: self.FPS = 120
        self.GRAVITY = .981
        self.QUIT_SIGNAL = False
        self.game_state = State.READY

        self.pipe_speed = 3
        self.game_start_time = time()
        self.score = 0

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pipes = []
        self.birds = [Bird() for _ in range(population)]
        self.population = population

    def start(self):
        clock = pygame.time.Clock()
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
            self.pipes[i].bot.x -= self.pipe_speed
            if self.pipes[i].top.right < 0:
                del self.pipes[i]

        for bird in self.birds:
            bird.velocity += self.GRAVITY
            bird.rect.y += bird.velocity

        self.check_dead()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.top, 3)
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.bot, 3)

        for bird in self.birds:
            if not bird.dead:
                pygame.draw.rect(self.screen, (0, 255, 0), bird.rect, 3)

        pygame.display.flip()

    def spawn_pipe(self):
        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > 200:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))

    def jump(self, id_=0):
        self.birds[id_].velocity = self.birds[id_].VELOCITY_INITIAL

    def restart(self):
        self.pipes.clear()
        self.birds = [Bird() for _ in range(self.population)]
        self.game_start_time = time()
        self.game_state = State.READY

    def check_dead(self):
        for bird in self.birds:
            if bird.dead:
                continue
            if bird.rect.bottom >= self.HEIGHT or bird.rect.top <= 0:
                self.kill_bird(bird)

        for bird in self.birds:
            if bird.dead:
                continue
            for pipe in self.pipes:
                if pipe.top.colliderect(bird.rect) or pipe.bot.colliderect(bird.rect):
                    self.kill_bird(bird)

    def kill_bird(self, bird):
        bird.fitness = time() - self.game_start_time
        bird.dead = True
        if sum([b.dead for b in self.birds]) == self.population:
            self.game_state = State.GAMEOVER
