from random import randint, seed
from time import time, sleep

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def right(self):
        return self.x+self.w

    @property
    def left(self):
        return self.x

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def top(self):
        return self.y

    @property
    def centery(self):
        return (self.y+self.h)//2


class Pipe:
    spawned = 0

    def __init__(self, height, width, moving_pipes=False):
        self.passed = False
        self.pipe_speed = 3
        Pipe.spawned += 1
        gap_size = max(0, 250 - 10 * Pipe.spawned)
        ht = randint(0, height - gap_size)
        self.top = Rect(width, 0, 100, ht)
        self.moving_pipes = moving_pipes
        self.move_height = randint(0, height - gap_size)

        hb = ht + gap_size
        self.bot = Rect(width, hb, 100, height - hb)

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
        self.rect = Rect(16, 450, 32, 32)
        self.fitness = [0] * num_tests
        self.velocity = [0, self.y_vel_initial]
        self.dead = False
        self.last_pipe_gap_crossed = 0  # large reward once per pipe for crossing the empty gap
        self.last_frame_alive = 0
        self.gravity = .981

    def restart_test(self):
        self.rect = Rect(16, 450, 32, 32)
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
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.evo_mode = 0  # 0 minimal, 1 presentation, 2 no drawing.
        self.QUIT_SIGNAL = False
        self.get_seed_fun = get_seed_fun
        seed(get_seed_fun())

        self.human_playing = hardware is None
        self.score = 0
        self.generation = 0
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
        for i in range(self.num_tests):
            self.current_test = i
            if not self.human_playing:
                [hw.reset() for hw in self.hardware]
                self.restart_test()

            while not all([bird.dead for bird in self.birds]):
                self.update()
                self.run_all_hardware()

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


    def spawn_pipe(self):
        pipe_horizontal_buffer = 600

        if not self.pipes:
            if self.num_tests > 1:
                self.pipes.append(Pipe(self.HEIGHT, self.WIDTH, self.moving_pipes))
                ht = 10 + ((self.HEIGHT - 270) * self.current_test // self.num_tests)
                self.pipes[-1].top = Rect(self.WIDTH // 2, 0, 100, ht)
                hb = ht + 250
                self.pipes[-1].bot = Rect(self.WIDTH // 2, hb, 100, self.HEIGHT - hb)

        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > pipe_horizontal_buffer:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH, self.moving_pipes))

    def jump(self, id_=0):
        self.birds[id_].velocity[1] = self.birds[id_].y_vel_initial

    def set_hardware(self, hardware):
        self.hardware = hardware

    def restart_test(self):
        self.pipes.clear()
        self.next_pipe = None
        Pipe.spawned = 0
        self.score = 0
        self.frames = 1
        [bird.restart_test() for bird in self.birds]
        self.birds_alive = len(self.birds)

    def restart(self):
        self.pipes.clear()
        self.next_pipe = None
        self.birds = [Bird(self.num_tests) for _ in range(self.pop_size)]
        Pipe.spawned = 0
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
