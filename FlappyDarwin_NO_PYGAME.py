from random import randint

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

    def __init__(self, height, width):
        self.passed = False
        Pipe.spawned += 1
        gap_size = max(0, 250 - 10 * Pipe.spawned)
        ht = randint(0, height - gap_size)
        self.top = Rect(width, 0, 100, ht)

        hb = ht + gap_size
        self.bot = Rect(width, hb, 100, height - hb)


class Bird:
    def __init__(self, num_tests):
        self.VELOCITY_INITIAL = -10
        self.rect = Rect(16, 450, 32, 32)
        self.fitness = [0] * num_tests
        self.velocity = self.VELOCITY_INITIAL
        self.dead = False
        self.last_pipe_gap_crossed = 0  # large reward once per pipe for crossing the empty gap

    def restart_test(self):
        self.rect = Rect(16, 450, 32, 32)
        self.velocity = self.VELOCITY_INITIAL
        self.dead = False
        self.last_pipe_gap_crossed = 0


class FlappyDarwin:
    def __init__(self, hardware=None, ticks_per_update=30, num_tests=1):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.evo_mode = False
        self.GRAVITY = .981
        self.QUIT_SIGNAL = False
        self.human_playing = hardware is None

        self.pipe_speed = 3
        self.score = 0
        self.generation = 0
        self.frames = 1
        self.num_tests = num_tests
        self.current_test = 0

        self.pipes = []
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
            FlappyDarwin.run_single_hardware(hw)

    @staticmethod
    def run_single_hardware(hw):
        ticks = 0
        while ticks < 50 and not hw.EOP:
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
                bird.fitness[self.current_test] += (1 - abs(mid_y - bird.rect.centery) / max_distance) / regulator
                if bird.last_pipe_gap_crossed == self.score:
                    bird.last_pipe_gap_crossed += 1
                    bird.fitness[self.current_test] += 50

        self.check_dead()

    def spawn_pipe(self):
        pipe_horizontal_buffer = 600

        if not self.pipes:
            """
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))
            ht = 30
            self.pipes[-1].top = pygame.rect.Rect(self.WIDTH // 2, 0, 100, ht)
            hb = ht + 250
            self.pipes[-1].bot = pygame.rect.Rect(self.WIDTH // 2, hb, 100, self.HEIGHT - hb)
            """
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))
            ht = 10 + ((self.HEIGHT - 270) * self.current_test // self.num_tests)
            self.pipes[-1].top = Rect(self.WIDTH // 2, 0, 100, ht)
            hb = ht + 250
            self.pipes[-1].bot = Rect(self.WIDTH // 2, hb, 100, self.HEIGHT - hb)

        if not self.pipes or self.WIDTH - self.pipes[-1].top.right > pipe_horizontal_buffer:
            self.pipes.append(Pipe(self.HEIGHT, self.WIDTH))

    def jump(self, id_=0):
        self.birds[id_].velocity = self.birds[id_].VELOCITY_INITIAL

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
                if bird.rect.top <= self.next_pipe.top.bottom or bird.rect.bottom >= self.next_pipe.bot.top:
                    self.kill_bird(bird)

    def kill_bird(self, bird):
        assert not bird.dead
        bird.fitness[self.current_test] += self.frames
        bird.dead = True
        self.birds_alive-=1
