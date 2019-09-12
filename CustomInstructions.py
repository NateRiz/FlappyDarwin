from time import sleep


def jump(hardware, game):
    game.jump(hardware.id)
    return 0


def get_bird_height(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.birds[hardware.id].rect.y
    return 0


def get_gap_top(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    for pipe in game.pipes:
        if pipe.top.x > game.birds[hardware.id].rect.right:
            hardware.registers[args[0]] = pipe.top.bottom
            break
    return 0


def get_gap_bot(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    for pipe in game.pipes:
        if pipe.top.x > game.birds[hardware.id].rect.right:
            hardware.registers[args[0]] = pipe.bot.top
            break
    return 0


def wait():
    sleep(.25)
    return 0
