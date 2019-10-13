def jump(hardware, game):
    game.jump(hardware.traits)
    return 0


def get_bird_height(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.birds[hardware.traits].rect.centery
    return 0


def get_gap_top(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.next_pipe.top.bottom
    return 0


def get_gap_bot(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.next_pipe.bot.top
    return 0


def get_gap_midpoint(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = (game.next_pipe.bot.top + game.next_pipe.bot.top) // 2
    return 0


def get_pipe_x(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.next_pipe.x
    return 0


def get_screen_height(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = game.HEIGHT
    return 0


"""
import pygame
def check_pixel_collide(hardware, args, game):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    if args[1] < 0 or args[1] >= len(hardware.registers): return 0
    if args[2] < 0 or args[2] >= len(hardware.registers): return 0
    found = False
    rect = pygame.rect.Rect(hardware.registers[args[0]], hardware.registers[args[1]], 4, 4)
    pygame.draw.rect(game.screen, (255, 0, 0), rect)
    for pipe in game.pipes:
        if pipe.top.collidepoint(hardware.registers[args[0]], hardware.registers[args[1]]):
            hardware.registers[args[2]] = 1
            found = True
            break
    if not found:
        hardware.registers[args[2]] = 0

    return 0
"""
