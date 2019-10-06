import pygame
from random import randint
from threading import Thread
from time import sleep


class Pipe:
    spawned = 0

    def __init__(self, height, width):
        self.passed = False
        Pipe.spawned += 1
        gap_size = max(0, 250 - 10 * Pipe.spawned)
        ht = randint(0, height - gap_size)
        self.top = pygame.rect.Rect(width, 0, 100, ht)

        hb = ht + gap_size
        self.bot = pygame.rect.Rect(width, hb, 100, height - hb)


class Bird:
    def __init__(self):
        self.VELOCITY_INITIAL = -10
        self.rect = pygame.rect.Rect(16, 450, 32, 32)
        self.fitness = 0
        self.velocity = self.VELOCITY_INITIAL
        self.dead = False
        self.ready_to_start = False
        self.ready_for_update = False
        self.last_pipe_gap_crossed = 0  # large reward once per pipe for crossing the empty gap


class FlappyDarwin:
    def __init__(self, hardware=None, ticks_per_update=30):
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
        self.next_pipe = None
        self.hardware = hardware
        self.pop_size = 1 if not hardware else len(hardware)
        self.birds = [Bird() for _ in range(self.pop_size)]
        self.ticks_per_update = ticks_per_update

    def start(self):
        self.generation += 1

        while not all([bird.dead for bird in self.birds]):
            self.update()
            if not self.evo_mode:
                self.draw()
            self.poll()
            self.run_all_hardware()

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

    def run_all_hardware(self):
        """
        threads = [Thread(target=self.run_single_hardware,
                          args=(i, hw)) for i, hw in enumerate(self.hardware)
                   if not self.birds[i].dead and not hw.EOP]
        for t in threads:
            t.start()

        for t in threads:
            t.join()
        """
        for i, hw in enumerate(self.hardware):
            self.run_single_hardware(i, hw)

    def run_single_hardware(self, i, hw):
        ticks = 0
        while ticks < self.ticks_per_update and not hw.EOP:
            hw.tick()
            ticks += 1

    def update(self):
        self.frames += 1
        self.spawn_pipe()
        self.next_pipe = None
        for i in reversed(range(len(self.pipes))):
            self.pipes[i].top.x -= self.pipe_speed
            self.pipes[i].bot.x -= self.pipe_speed
            if self.pipes[i].top.right > self.birds[0].rect.left:
                self.next_pipe = self.pipes[i]
            if self.birds[0].rect.x > self.pipes[i].top.x and not self.pipes[i].passed:
                self.pipes[i].passed = True
                self.score += 1
            if self.pipes[i].top.right < 0:
                del self.pipes[i]

        for bird in self.birds:
            bird.velocity += self.GRAVITY
            bird.rect.y += bird.velocity

        mid_y = (self.next_pipe.top.bottom + self.next_pipe.bot.top) // 2
        max_distance = (self.next_pipe.bot.top - self.next_pipe.top.bottom) // 2
        regulator = 10
        for bird in self.birds:
            if self.next_pipe.top.bottom <= bird.rect.centery <= self.next_pipe.bot.top:
                bird.fitness += (1 - abs(mid_y - bird.rect.centery) / max_distance) / regulator
                if bird.last_pipe_gap_crossed == self.score:
                    bird.last_pipe_gap_crossed += 1
                    bird.fitness += 50

        self.check_dead()

    def draw(self):
        self.screen.fill((0, 0, 0))

        gen = self.font.render(F"Gen: {self.generation}", True, (255, 255, 255))
        score = self.font.render(F"Score: {self.score}", True, (255, 255, 255))
        frame = self.font.render(F"Frame: {self.frames}", True, (255, 255, 255))
        self.screen.blit(gen, (8, 8))
        self.screen.blit(score, (8, 16 + gen.get_size()[1]))
        self.screen.blit(frame, (8, 32 + score.get_size()[1] + gen.get_size()[1]))

        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.top, 3)
            pygame.draw.rect(self.screen, (255, 255, 255), pipe.bot, 3)

        pygame.draw.rect(self.screen, (255, 255, 0), self.next_pipe.top, 3)
        pygame.draw.rect(self.screen, (255, 255, 0), self.next_pipe.bot, 3)

        for bird in self.birds:
            if not bird.dead:
                color = (255, 0, 0)
                if self.next_pipe.top.bottom <= bird.rect.centery <= self.next_pipe.bot.top:
                    color = (0, 255, 0)
                pygame.draw.rect(self.screen, color, bird.rect, 3)

        pygame.display.flip()

    def spawn_pipe(self):
        pipe_horizontal_buffer = 600

        if not self.pipes:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))
            ht = 30
            self.pipes[-1].top = pygame.rect.Rect(self.WIDTH // 2, 0, 100, ht)
            hb = ht + 250
            self.pipes[-1].bot = pygame.rect.Rect(self.WIDTH // 2, hb, 100, self.HEIGHT - hb)

            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))
            ht = 300
            self.pipes[-1].top = pygame.rect.Rect(self.WIDTH // 2 + pipe_horizontal_buffer, 0, 100, ht)
            hb = ht + 250
            self.pipes[-1].bot = pygame.rect.Rect(self.WIDTH // 2 + pipe_horizontal_buffer, hb, 100, self.HEIGHT - hb)

        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > pipe_horizontal_buffer:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))

    def jump(self, id_=0):
        self.birds[id_].velocity = self.birds[id_].VELOCITY_INITIAL

    def set_hardware(self, hardware):
        self.hardware = hardware

    def restart(self):
        self.pipes.clear()
        self.next_pipe = None
        self.birds = [Bird() for _ in range(self.pop_size)]
        Pipe.spawned = 0
        self.score = 0
        self.frames = 1

    def check_dead(self):
        for bird in self.birds:
            if bird.dead:
                continue
            if bird.rect.bottom >= self.HEIGHT or bird.rect.top <= 0:
                self.kill_bird(bird)

        if self.next_pipe.top.left <= self.birds[0].rect.right or self.next_pipe.top.right <= self.birds[0].rect.left:
            for bird in self.birds:
                if bird.dead:
                    continue
                if self.next_pipe.top.colliderect(bird.rect) or self.next_pipe.bot.colliderect(bird.rect):
                    self.kill_bird(bird)

    def kill_bird(self, bird):
        assert not bird.dead
        bird.fitness += self.frames
        bird.dead = True
