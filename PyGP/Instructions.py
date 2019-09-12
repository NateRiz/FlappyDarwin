def add(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = hardware.registers[a] + hardware.registers[b]
    return 0


def sub(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = hardware.registers[a] - hardware.registers[b]
    return 0


def mul(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = hardware.registers[a] * hardware.registers[b]
    return 0


def div(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    if hardware.registers[b] == 0: return 0
    hardware.registers[dest] = hardware.registers[a] / hardware.registers[b]
    return 0


def eq(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = float(hardware.registers[a] == hardware.registers[b])
    return 0


def greater(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = float(hardware.registers[a] > hardware.registers[b])
    return 0


def less(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = float(hardware.registers[a] < hardware.registers[b])
    return 0


def not_(hardware, args):
    a, dest, _ = args
    if a < 0 or a >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = float(not hardware.registers[a])
    return 0


def inc(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] += 1
    return 0


def dec(hardware, args):
    hardware.registers[args[0]] -= 1
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    return 0


def assign(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = args[1]
    return 0


def copy(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    if args[1] < 0 or args[1] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = hardware.registers[args[1]]
    return 0


def while_(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 2
    if hardware.registers[args[0]] == 0:
        return 2
    return 0
"""
def for_(hardware, args, increment):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 2
    return abs(hardware.registers[args[0]] - increment) == 0
"""

def close(_, __):
    return 1
