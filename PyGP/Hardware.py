from random import randint, choice
from enum import Enum
from time import time, sleep

"""
###################################################
### Python Genetic Programming Virtual Hardware ###
###################################################

Quick Use:
-Create an Instruction Library and a Hardware with it.
-Add Any instructions needed to the IL
-Run with Tick() until EOP (End Of Program) or end manually.

Warnings:
-Do not mutate the hardware or modify the program while it is running. 
--You must manually call RESET to update the cache when it is mutated
"""


class Hardware:

    def __init__(self, inst_lib, trait=None, min_prog_len=8, max_prog_len=96, ips=0, ):
        self.instructions = []  # The actual program : List of Instruction Objects
        self.IP = 0  # Instruction Pointer
        self.IPS = ips  # Caps the hardware at x instructions per second
        self.EOP = False  # have we reached the end of the program yet?
        self.registers = [0.0] * 24
        self.inst_lib = inst_lib
        self.fitness = -1
        self.cache_dirty = True
        self.last_tick_time = 0
        self.MIN_PROGRAM_LENGTH = min_prog_len
        self.MAX_PROGRAM_LENGTH = max_prog_len
        self.traits = trait  # Arbitrary information the user gives to the HW. Does not get copied.
        self.verbose = False
        self.file = None
        self.close_map = {}  # tells a Close where its corresponding Block is
        self.block_map = {}  # tells a Block where its corresponding Close is

    def reset(self):
        self.IP = 0
        self.EOP = False
        self.registers = [0.0] * 24
        self.fitness = -1
        self.cache_dirty = True
        self.last_tick_time = 0
        self.verbose = False
        if self.file:
            self.file.close()

    def clear_program(self):
        self.instructions.clear()
        self.reset()

    def copy(self):
        hw = Hardware(self.inst_lib, None, self.MIN_PROGRAM_LENGTH, self.MAX_PROGRAM_LENGTH, self.IPS)

        for i in self.instructions:
            inst = self.inst_lib.lib[i.name]
            hw.instructions.append(inst[0](*inst[1:]))
            hw.instructions[-1].args = list(i.args)

        return hw

    def set_verbose(self):
        self.verbose = True
        self.file = open(f"{self.traits}.txt", "w")

    def tick(self):
        if self.IP < 0 or self.IP >= len(self.instructions):
            return

        if self.cache_dirty:
            self.cache()

        if self.IPS > 0:
            elapsed = time() - self.last_tick_time
            if elapsed < (1 / self.IPS):
                sleep((1 / self.IPS) - elapsed)

        if self.file:
            self.file.write(F"Inst Ptr: {self.IP}\n")
            self.file.write(str([F"{i}: {reg}" for i, reg in enumerate(self.registers) if reg]))
            self.file.write("\n")
            self.file.write(F"{str(self.instructions[self.IP])} [{self.instructions[self.IP].increment}]")
            self.file.write("\n\n")
        ip_next_state = self.instructions[self.IP].run(self)
        self.update_ip(ip_next_state)
        self.EOP = self.IP >= len(self.instructions)
        self.last_tick_time = time()

    def cache(self):
        self.cache_dirty = False
        stack = []
        for i, inst in enumerate(self.instructions):
            if inst.is_block:
                stack.append(i)
            elif inst.name == "Close":
                if stack:
                    blk = stack.pop()
                    self.close_map[i] = blk
                    self.block_map[blk] = i
                else:
                    self.close_map[i] = i+1
        for _ in range(len(stack)):
            self.instructions.append(self.inst_lib.get_inst("Close"))
            blk = stack.pop()
            self.close_map[len(self.instructions)-1] = blk
            self.block_map[blk] = len(self.instructions)-1

    def update_ip(self, ip_next_state):
        if ip_next_state == IP_next_state.LOOP_END:
            self.IP = self.block_map[self.IP] + 1

        elif ip_next_state == IP_next_state.LOOP_START:
            self.IP = self.close_map[self.IP]

        else:
            self.IP += 1

    def __len__(self):
        return len(self.instructions)

    def cache_fitness(self, fitness):
        self.fitness = fitness

    def generate_program(self):
        prog_len = randint(self.MIN_PROGRAM_LENGTH, self.MAX_PROGRAM_LENGTH)
        insts = list(self.inst_lib.lib.values())
        i = 0
        while i < prog_len:
            inst = choice(insts)
            self.instructions.append(inst[0](*inst[1:]))
            self.instructions[-1].args[0] = randint(0, len(self.registers)-1)
            self.instructions[-1].args[1] = randint(0, len(self.registers)-1)
            self.instructions[-1].args[2] = randint(0, len(self.registers)-1)
            i += 1

    def load_program(self, name):
        with open(name, "r") as file:
            for line in file:
                if not line.strip(): continue

                line = line.split()
                inst_name = line[0]
                il = self.inst_lib.lib[inst_name]
                inst = il[0](*il[1:])
                i = 0
                for arg in line:
                    if arg.isdigit():
                        inst.args[i] = int(arg)
                        i += 1
                        if i >= 3:
                            break
                self.instructions.append(inst)

    def __str__(self):
        ret = [str(self.IP), str(self.registers)]
        tabs = 0
        for idx, i in enumerate(self.instructions):
            if i.name == "Close" and tabs >= 1:
                tabs -= 1
            ret.append(f"{str(idx)+'.':>3} " + "\t" * tabs + str(i))
            if i.is_block:
                tabs += 1

        return "\n".join(ret)


class InstructionLibrary:
    def __init__(self):
        self.lib = {}

    def add_inst(self, name, callback, is_block):
        self.lib[name] = (Instruction, name, callback, is_block)

    def get_inst(self, name):
        inst = self.lib[name]
        return inst[0](*inst[1:])


class Instruction:
    def __init__(self, name, callback, is_block):
        self.name = name
        self.args = [0, 0, 0]
        self.callback = callback
        self.__repr__ = self.__str__
        self.is_block = is_block
        self.STATES = [IP_next_state.NEXT, IP_next_state.LOOP_START, IP_next_state.LOOP_END]
        self.increment = 0

    def run(self, hardware):
        state = self.callback(hardware, self.args)
        if self.is_block:
            self.increment += 1
            if self.STATES[state] == IP_next_state.LOOP_END:
                self.increment = 0
        return self.STATES[state]

    def __str__(self):
        return F"{self.name:<8} {tuple(self.args)}"


class IP_next_state(Enum):
    NEXT = 0
    LOOP_START = 1
    LOOP_END = 2
