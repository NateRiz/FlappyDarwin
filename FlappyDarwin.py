import pygame
from random import randint
from time import sleep
from enum import Enum


class State(Enum):
    SETUP = 0
    PLAYING = 1
    GAMEOVER = 2


class Pipe:
    spawned = 0

    def __init__(self, height, width):
        self.passed = False
        Pipe.spawned += 1
        gap_size = max(0, 250 - 10 * Pipe.spawned)
        ht = randint(00, height - gap_size)
        self.top = pygame.rect.Rect(width, 0, 100, ht)

        hb = ht + gap_size
        self.bot = pygame.rect.Rect(width, hb, 100, height - hb)


class Bird:
    def __init__(self):
        self.VELOCITY_INITIAL = -10
        self.rect = pygame.rect.Rect(16, 300 + randint(-3, 3), 32, 32)
        self.fitness = 0
        self.velocity = self.VELOCITY_INITIAL
        self.dead = False
        self.ready_to_start = False
        self.ready_for_update = False



class FlappyDarwin:
    def __init__(self, population=1):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.evo_mode = False
        self.GRAVITY = .981
        self.QUIT_SIGNAL = False

        self.pipe_speed = 3
        self.score = 0
        self.generation = -1
        self.font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self.frames = 1

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pipes = []
        self.birds = [Bird() for _ in range(population)]
        self.population = population

        self.game_state = State.SETUP

    def start(self):

        while not self.QUIT_SIGNAL:

            while sum([bird.ready_to_start for bird in self.birds]) != self.population:
                sleep(.1)

            self.game_state = State.PLAYING
            self.generation += 1

            while self.game_state == State.PLAYING:
                while sum([bird.ready_for_update for bird in self.birds]) != self.population:
                    sleep(.1)
                self.update()
                if not self.evo_mode:
                    self.draw()
                self.poll()

            while self.game_state == State.GAMEOVER:
                sleep(.1)


    def poll(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.QUIT_SIGNAL = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump()

                if event.key == pygame.K_RETURN:
                    self.evo_mode = not self.evo_mode

    def update(self):
        self.frames += 1
        self.spawn_pipe()
        for i in reversed(range(len(self.pipes))):
            self.pipes[i].top.x -= self.pipe_speed
            self.pipes[i].bot.x -= self.pipe_speed
            if self.birds[0].rect.x > self.pipes[i].top.x and not self.pipes[i].passed:
                self.pipes[i].passed = True
                self.score += 1
            if self.pipes[i].top.right < 0:
                del self.pipes[i]

        for bird in self.birds:
            bird.velocity += self.GRAVITY
            bird.rect.y += bird.velocity

        self.check_dead()
        if sum([bird.dead for bird in self.birds]) == self.population:
            self.game_state = State.GAMEOVER

    def draw(self):
        self.screen.fill((0, 0, 0))

        gen = self.font.render(F"Gen: {self.generation}", True, (255, 255, 255))
        score = self.font.render(F"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(gen, (8, 8))
        self.screen.blit(score, (8, 16 + gen.get_size()[1]))

        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.top, 3)
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.bot, 3)

        for bird in self.birds:
            if not bird.dead:
                pygame.draw.rect(self.screen, (0, 255, 0), bird.rect, 3)

        pygame.display.flip()

    def spawn_pipe(self):
        pipe_horizontal_buffer = 400
        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > pipe_horizontal_buffer:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))

    def jump(self, id_=0):
        self.birds[id_].velocity = self.birds[id_].VELOCITY_INITIAL

    def restart(self):
        self.pipes.clear()
        self.birds = [Bird() for _ in range(self.population)]
        Pipe.spawned = 0
        self.score = 0
        self.frames = 1
        self.game_state = State.SETUP

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
        assert bird.dead == Falses
        bird.fitness = self.frames
        bird.dead = True

