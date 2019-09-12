from random import randint, choice
from enum import Enum

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
    def __init__(self, inst_lib, id=0):
        self.instructions = []  # The actual program : List of Instruction Objects
        self.IP = 0  # Instruction Pointer
        self.EOP = False  # have we reached the end of the program yet?
        self.registers = [0.0] * 24
        self.inst_lib = inst_lib
        self.fitness = -1
        self.block_cache = 0
        self.cache_dirty = True
        self.id = id  # For external use. Must handle uniqueness outside of this class.

        self.MAX_PROGRAM_LENGTH = 96
        self.MIN_PROGRAM_LENGTH = 1

    def reset(self):
        self.IP = 0
        self.EOP = False
        self.registers = [0.0] * 24
        self.fitness = -1
        self.cache_dirty = True

    def tick(self):
        if self.cache_dirty:
            self.cache()
        if self.IP < 0 or self.IP >= len(self.instructions):
            return
        ip_next_state = self.instructions[self.IP].run(self)
        self.update_ip(ip_next_state)
        self.EOP = self.IP >= len(self.instructions)

    def cache(self):
        self.cache_dirty = False
        first_block = False
        for inst in self.instructions:
            if inst.is_block:
                self.block_cache += 1
                first_block = True
            elif inst.name == "Close" and first_block:
                self.block_cache -= 1
        for _ in range(self.block_cache):
            self.instructions.append(self.inst_lib.get_inst("Close"))

    def update_ip(self, ip_next_state):
        next_ip = -1

        if ip_next_state == IP_next_state.LOOP_END:
            open_block = 0
            ip = self.IP
            while ip < len(self.instructions):
                if self.instructions[ip].name == "Close":
                    open_block -= 1
                    if open_block == 0:
                        next_ip = ip + 1  # we want to go to the line after the close.
                        break
                elif self.instructions[ip].is_block:
                    open_block += 1
                ip += 1

            if next_ip < len(self.instructions) and self.instructions[next_ip]:
                self.IP = next_ip
                ip_next_state = IP_next_state.LOOP_START

        if ip_next_state == IP_next_state.LOOP_START:
            open_block = 0
            ip = self.IP
            while ip >= 0:
                if self.instructions[ip].name == "Close":
                    open_block += 1
                elif self.instructions[ip].is_block:
                    open_block -= 1
                    if open_block == 0:
                        next_ip = ip  # retest the while loop
                        break
                ip -= 1

        if next_ip != -1:
            self.IP = next_ip
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
            self.instructions[-1].args[0] = randint(0, len(self.registers))
            self.instructions[-1].args[1] = randint(0, len(self.registers))
            self.instructions[-1].args[2] = randint(0, len(self.registers))
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
        first_block = False
        tabs = 0
        for i in self.instructions:
            if i.name == "Close" and first_block:
                tabs -= 1
            ret.append("\t" * tabs + str(i))
            if i.is_block:
                tabs += 1
                first_block = True


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

    def run(self, hardware):
        state = self.callback(hardware, self.args)
        return self.STATES[state]

    def __str__(self):
        return F"{self.name:<8} {tuple(self.args)}"


class IP_next_state(Enum):
    NEXT = 0
    LOOP_START = 1
    LOOP_END = 2
