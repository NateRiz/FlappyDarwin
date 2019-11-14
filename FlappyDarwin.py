import pygame
from random import randint, seed
import os
from time import time


class Pipe:
    def __init__(self, height, width, moving_pipes=False):
        self.passed = False
        self.pipe_speed = 3
        gap_size = 256
        ht = randint(0, height - gap_size)
        self.top = pygame.rect.Rect(width, 0, 100, ht)
        self.moving_pipes = moving_pipes
        self.move_height = randint(0, height - gap_size)

        hb = ht + gap_size
        self.bot = pygame.rect.Rect(width, hb, 100, height - hb)

    def update(self):
        self.top.x -= self.pipe_speed
        self.bot.x -= self.pipe_speed
        if self.moving_pipes and self.top.x <= 300:
            self.move_to_next_height()

    def move_to_next_height(self):
        move_speed = 3
        if self.top.height < self.move_height:
            self.top.height += move_speed
            self.bot.top += move_speed

        elif self.top.height > self.move_height:
            self.top.height -= move_speed
            self.bot.top -= move_speed
            self.bot.height += move_speed

        if abs(self.top.height - self.move_height) < 2:
            self.top.height = self.move_height


class Bird:
    def __init__(self, num_tests):
        self.y_vel_initial = -10
        self.rect = pygame.rect.Rect(16, 450, 32, 32)
        self.fitness = [0] * num_tests
        self.velocity = [0, self.y_vel_initial]
        self.dead = False
        self.last_pipe_gap_crossed = 0  # large reward once per pipe for crossing the empty gap
        self.last_frame_alive = 0
        self.gravity = .981

    def restart_test(self):
        self.rect = pygame.rect.Rect(16, 450, 32, 32)
        self.velocity = [0, self.y_vel_initial]
        self.dead = False
        self.last_pipe_gap_crossed = 0
        self.last_frame_alive = 0
        self.gravity = .981

    def set_gravity(self, g):
        self.gravity = g

    def set_jump(self, j):
        self.velocity[1] = j


class FlappyDarwin:
    def __init__(self, hardware=None, ticks_per_update=30, num_tests=1, get_seed_fun=lambda: time()):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.FPS = 60
        self.evo_mode = 0  # 0 minimal, 1 presentation, 2 no drawing.
        self.QUIT_SIGNAL = False
        self.get_seed_fun = get_seed_fun
        seed(get_seed_fun())

        ASSET_PATH = os.path.join(os.getcwd(), "Assets")
        self.background = pygame.image.load(os.path.join(ASSET_PATH, "background.png")).convert()
        self.pipe_up = pygame.image.load(os.path.join(ASSET_PATH, "pipe.png")).convert_alpha()
        self.bird_img = pygame.image.load(os.path.join(ASSET_PATH, "bird.png")).convert_alpha()
        self.pipe_down = pygame.transform.flip(self.pipe_up, 0, 1)

        self.human_playing = hardware is None
        self.score = 0
        self.generation = 0
        self.font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self.frames = 1
        self.num_tests = num_tests
        self.current_test = 0
        self.gen_finished_test = -1

        self.pipes = []
        self.moving_pipes = False
        self.next_pipe = None
        self.hardware = hardware
        self.pop_size = 1 if not hardware else len(hardware)
        self.birds = [Bird(self.num_tests) for _ in range(self.pop_size)]
        self.birds_alive = len(self.birds)
        self.ticks_per_update = ticks_per_update

    def start(self):
        self.generation += 1
        self.restart()
        clock = pygame.time.Clock()
        for i in range(self.num_tests):
            self.current_test = i
            if not self.human_playing:
                [hw.reset() for hw in self.hardware]
                self.restart_test()

            while not all([bird.dead for bird in self.birds]):
                self.update()
                if self.evo_mode != 2:
                    self.draw()
                self.poll()
                if not self.human_playing:
                    self.run_all_hardware()
                else:
                    clock.tick(self.FPS)

    def poll(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.QUIT_SIGNAL = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump()

                if event.key == pygame.K_RETURN:
                    self.evo_mode = (self.evo_mode+1)%3

    def run_all_hardware(self):
        for i, hw in enumerate(self.hardware):
            self.run_single_hardware(hw)

    def run_single_hardware(self, hw):
        ticks = 0
        while ticks < self.ticks_per_update and not hw.EOP:
            hw.tick()
            ticks += 1

    def update(self):
        self.frames += 1
        self.spawn_pipe()
        self.next_pipe = None
        for i in reversed(range(len(self.pipes))):
            self.pipes[i].update()
            if self.pipes[i].top.right > self.birds[0].rect.left:
                self.next_pipe = self.pipes[i]
            if self.birds[0].rect.x > self.pipes[i].top.x and not self.pipes[i].passed:
                self.pipes[i].passed = True
                self.score += 1
            if self.pipes[i].top.right < 0:
                del self.pipes[i]

        for bird in self.birds:
            if not bird.dead:
                bird.velocity[1] += bird.gravity
                bird.rect.y += bird.velocity[1]
                bird.rect.x += bird.velocity[0]

        mid_y = (self.next_pipe.top.bottom + self.next_pipe.bot.top) // 2
        max_distance = (self.next_pipe.bot.top - self.next_pipe.top.bottom) // 2
        regulator = 10
        for bird in self.birds:
            if self.next_pipe.top.bottom <= bird.rect.centery <= self.next_pipe.bot.top:
                bird.fitness[self.current_test] += (1 - abs(mid_y - bird.rect.centery) / max_distance) / regulator
                if bird.last_pipe_gap_crossed == self.score:
                    bird.last_pipe_gap_crossed += 1
                    bird.fitness[self.current_test] += 50

        self.check_dead()

        last_test = 120
        if self.gen_finished_test == -1 and self.score >= last_test:
            self.gen_finished_test = self.generation
            self.moving_pipes = True


    def draw(self):
        if self.evo_mode == 0:
            self.screen.fill((0, 0, 0))
        elif self.evo_mode == 1:
            self.screen.blit(self.background, (0,0))

        gen = self.font.render(F"Gen: {self.generation} Test {self.current_test}/{self.num_tests}", True,
                               (255, 255, 255))
        score = self.font.render(F"Score: {self.score}", True, (255, 255, 255))
        frame = self.font.render(F"Frame: {self.frames}", True, (255, 255, 255))
        alive = self.font.render(F"Alive: {self.birds_alive} / {len(self.birds)}", True, (255, 255, 255))
        self.screen.blit(gen, (8, 8))
        self.screen.blit(score, (8, 16 + gen.get_size()[1]))
        self.screen.blit(frame, (8, 32 + score.get_size()[1] * 2))
        self.screen.blit(alive, (8, 48 + score.get_size()[1] * 3))

        for pipe in self.pipes:
            if self.evo_mode == 0:
                pygame.draw.rect(self.screen, (255, 255, 255), pipe.top, 3)
                pygame.draw.rect(self.screen, (255, 255, 255), pipe.bot, 3)
            elif self.evo_mode == 1:
                self.screen.blit(self.pipe_down, (pipe.top.x, pipe.top.bottom - self.pipe_down.get_size()[1]))
                self.screen.blit(self.pipe_up, pipe.bot)

        if self.evo_mode == 0:
            pygame.draw.rect(self.screen, (255, 255, 0), self.next_pipe.top, 3)
            pygame.draw.rect(self.screen, (255, 255, 0), self.next_pipe.bot, 3)

        for bird in self.birds:
            if not bird.dead:
                if self.evo_mode == 0:
                    color = (255, 0, 0)
                    if self.next_pipe.top.bottom <= bird.rect.centery <= self.next_pipe.bot.top:
                        color = (0, 255, 0)
                    pygame.draw.rect(self.screen, color, bird.rect, 3)
                elif self.evo_mode == 1:
                    self.screen.blit(self.bird_img, bird.rect)

        pygame.display.flip()

    def spawn_pipe(self):
        pipe_horizontal_buffer = 600

        if not self.pipes:
            if self.num_tests > 1:
                self.pipes.append(Pipe(self.HEIGHT, self.WIDTH, self.moving_pipes))
                ht = 10 + ((self.HEIGHT - 270) * self.current_test // self.num_tests)
                self.pipes[-1].top = pygame.rect.Rect(self.WIDTH // 2, 0, 100, ht)
                hb = ht + 250
                self.pipes[-1].bot = pygame.rect.Rect(self.WIDTH // 2, hb, 100, self.HEIGHT - hb)

        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > pipe_horizontal_buffer:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH, self.moving_pipes))

    def jump(self, id_=0):
        self.birds[id_].velocity[1] = self.birds[id_].y_vel_initial

    def set_hardware(self, hardware):
        self.hardware = hardware

    def restart_test(self):
        self.pipes.clear()
        self.next_pipe = None
        self.score = 0
        self.frames = 1
        [bird.restart_test() for bird in self.birds]
        self.birds_alive = len(self.birds)

    def restart(self):
        self.pipes.clear()
        self.next_pipe = None
        self.birds = [Bird(self.num_tests) for _ in range(self.pop_size)]
        self.score = 0
        self.frames = 1
        self.birds_alive = len(self.birds)
        seed(self.get_seed_fun())


    def check_dead(self):
        for bird in self.birds:
            if bird.dead:
                continue
            if bird.rect.bottom >= self.HEIGHT or bird.rect.top <= 0 or bird.rect.right >= self.WIDTH:
                self.kill_bird(bird)
                continue

        if self.next_pipe.top.left <= self.birds[0].rect.right and self.next_pipe.top.right >= self.birds[0].rect.left:
            for bird in self.birds:
                if bird.dead:
                    continue
                if bird.rect.bottom >= self.next_pipe.bot.top or bird.rect.top <= self.next_pipe.top.bottom:
                    self.kill_bird(bird)

    def kill_bird(self, bird):
        assert not bird.dead
        bird.fitness[self.current_test] += self.frames
        bird.dead = True
        bird.last_frame_alive = self.frames
        self.birds_alive -= 1
