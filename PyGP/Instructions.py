def clamp(n):
    if n < -2147483648:
        return -2147483648
    if n > 2147483648:
        return 2147483648
    return n


def add(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = clamp(hardware.registers[a] + hardware.registers[b])
    return 0


def sub(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = clamp(hardware.registers[a] - hardware.registers[b])
    return 0


def mul(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    hardware.registers[dest] = clamp(hardware.registers[a] * hardware.registers[b])
    return 0


def div(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    if hardware.registers[b] == 0: return 0
    hardware.registers[dest] = clamp(hardware.registers[a] / hardware.registers[b])
    return 0


def mod(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return 0
    if b < 0 or b >= len(hardware.registers): return 0
    if dest < 0 or dest >= len(hardware.registers): return 0
    if hardware.registers[b] == 0: return 0
    hardware.registers[dest] = clamp(hardware.registers[a] % hardware.registers[b])
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
    hardware.registers[args[0]] = clamp(hardware.registers[args[0]]+1)
    return 0


def dec(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = clamp(hardware.registers[args[0]]-1)
    return 0


def assign(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = clamp(args[1])
    return 0


def copy(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 0
    if args[1] < 0 or args[1] >= len(hardware.registers): return 0
    hardware.registers[args[0]] = clamp(hardware.registers[args[1]])
    return 0


def while_(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 2
    if hardware.registers[args[0]] == 0:
        return 2
    return 0


def for_(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return 2
    inst = hardware.instructions[hardware.IP]
    increment = inst.increment
    if abs(hardware.registers[args[0]]) - increment <= 0:
        return 2
    return 0


def if_(hardware, args):  # Not a normal conditional. Can be broken out of with 'break'
    if args[0] < 0 or args[0] >= len(hardware.registers): return 2
    inst = hardware.instructions[hardware.IP]
    increment = inst.increment
    if hardware.registers[args[0]] == 0 or increment != 0:
        return 2
    return 0
"""
broken on first level of program (if not in block)
def break_(_, __):
    return 2
"""

def close(_, __):
    return 1


