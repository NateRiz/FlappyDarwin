def add(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = hardware.registers[a] + hardware.registers[b]


def sub(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = hardware.registers[a] - hardware.registers[b]


def mul(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = hardware.registers[a] * hardware.registers[b]


def div(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    if hardware.registers[b] == 0: return
    hardware.registers[dest] = hardware.registers[a] / hardware.registers[b]


def eq(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = float(hardware.registers[a] == hardware.registers[b])


def greater(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = float(hardware.registers[a] > hardware.registers[b])


def less(hardware, args):
    a, b, dest = args
    if a < 0 or a >= len(hardware.registers): return
    if b < 0 or b >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = float(hardware.registers[a] < hardware.registers[b])


def not_(hardware, args):
    a, dest, _ = args
    if a < 0 or a >= len(hardware.registers): return
    if dest < 0 or dest >= len(hardware.registers): return
    hardware.registers[dest] = float(not hardware.registers[a])


def inc(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return
    hardware.registers[args[0]] += 1


def dec(hardware, args):
    hardware.registers[args[0]] -= 1
    if args[0] < 0 or args[0] >= len(hardware.registers): return


def assign(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return
    hardware.registers[args[0]] = args[1]


def copy(hardware, args):
    if args[0] < 0 or args[0] >= len(hardware.registers): return
    if args[1] < 0 or args[1] >= len(hardware.registers): return
    hardware.registers[args[0]] = hardware.registers[args[1]]


def while_(hardware, args, _):
    if args[0] < 0 or args[0] >= len(hardware.registers): return False
    return hardware.registers[args[0]] == 0


def for_(hardware, args, increment):
    if args[0] < 0 or args[0] >= len(hardware.registers): return False
    return abs(hardware.registers[args[0]] - increment) == 0
