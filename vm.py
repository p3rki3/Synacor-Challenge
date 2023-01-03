from collections import deque
import itertools
import time
import sys

class VM:
    def __init__(self, bin_name, instr_name, test=False, slow=False, disasm=False, trace=False):
        self.prog, self.regs, self.stack = [], [0] * 8, deque()
        self.ip = self.a = self.b = self.c = self.instcount = 0
        self.inptr, self.instr, self.inptr_auto, self.instr_auto = 0, [], 0, []  
        self.test, self.slow, self.disasm, self.fulltrace = test, slow, disasm, trace
        self.ops = {0: (self.phalt, 0), 1: (self.pset, 3), 2: (self.ppush, 2), 3: (self.ppop, 2), 4: (self.peq, 4), 5: (self.pgt, 4), 6: (self.pjmp, 0),
                    7: (self.pjt, 3), 8: (self.pjf, 3), 9: (self.padd, 4), 10: (self.pmult, 4), 11: (self.pmod, 4), 12: (self.pand, 4), 13: (self.por, 4),
                    14: (self.pnot, 3), 15: (self.prmem, 3), 16: (self.pwmem, 3), 17: (self.pcall, 0), 18: (self.pret, 0), 19: (self.pout, 2),
                    20: (self.pin, 2), 21: (self.pnoop, 1)}
        self.opcodes = {0: ('halt', 0), 1: ('set', 2), 2: ('push', 1), 3: ('pop', 1), 4: ('eq', 3), 5: ('gt', 3), 6: ('jmp', 1),
                        7: ('jt', 2), 8: ('jf', 2), 9: ('add', 3), 10: ('mult', 3), 11: ('mod', 3), 12: ('and', 3), 13: ('or', 3),
                        14: ('not', 2), 15: ('rmem', 2), 16: ('wmem', 2), 17: ('call', 1), 18: ('ret', 0), 19: ('out', 1),
                        20: ('in', 1), 21: ('noop', 0)}

        self.used_ips = []
        self.tracefile = open("vmtrace.txt", 'w')
        with open(bin_name, "rb") as fp:        # Read in the binary program for the VM
            code = fp.read(2)
            while code:
                self.prog.append(int.from_bytes(code, byteorder='little', signed=False))
                code = fp.read(2)
        print("Read in code of length: ", len(self.prog), " and ready to run the VM...\n")
        for _ in range(len(self.prog), 32768):  # pad to the end of a 15 bit address space
            self.prog.append(0)
        print("Now reading in your instruction list to feed to the VM if there is one")
        try:
            self.instr = open(instr_name, "r").read()  # Read in the input instruction list
        except:
            pass

    def __del__(self):
        print("Executed a total of ", self.instcount, " instructions in the VM\n")
        self.tracefile.close()

    # Each of the following implements a single instruction in the VM; the instruction pointer, stack, registers and program binary are all in the class namespace
    @staticmethod
    def phalt():
        print("\n\nEncountered a halt instruction - stopping the VM\n\n")
        exit(0)

    def pset(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = self.b if self.b < 32768 else self.regs[self.b-32768]

    def ppush(self):
        self.stack.append(self.a if self.a < 32768 else self.regs[self.a-32768])

    def ppop(self):
        try:
            self.regs[self.a if self.a < 32768 else self.a-32768] = self.stack.pop()
        except:
            print('Stack underflow on pop - exiting...')
            exit(1)

    def peq(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = 1 if (self.b if self.b < 32768 else self.regs[self.b-32768]) == (self.c if self.c < 32768 else self.regs[self.c-32768]) else 0

    def pgt(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = 1 if (self.b if self.b < 32768 else self.regs[self.b-32768]) > (self.c if self.c < 32768 else self.regs[self.c-32768]) else 0

    def pjmp(self):
        self.ip = self.a if self.a < 32768 else self.regs[self.a-32768]

    def pjt(self):
        self.ip = self.ip if (self.a if self.a < 32768 else self.regs[self.a-32768]) == 0 else (self.b if self.b < 32768 else self.regs[self.b-32768]) - 3

    def pjf(self):
        self.ip = (self.b if self.b < 32768 else self.regs[self.b-32768]) - 3 if (self.a if self.a < 32768 else self.regs[self.a-32768]) == 0 else self.ip

    def padd(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = ((self.b if self.b < 32768 else self.regs[self.b-32768]) + (self.c if self.c < 32768 else self.regs[self.c-32768])) % 32768

    def pmult(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = ((self.b if self.b < 32768 else self.regs[self.b-32768]) * (self.c if self.c < 32768 else self.regs[self.c-32768])) % 32768

    def pmod(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = ((self.b if self.b < 32768 else self.regs[self.b-32768]) % (self.c if self.c < 32768 else self.regs[self.c-32768]))

    def pand(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = ((self.b if self.b < 32768 else self.regs[self.b-32768]) & (self.c if self.c < 32768 else self.regs[self.c-32768]))

    def por(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = ((self.b if self.b < 32768 else self.regs[self.b-32768]) | (self.c if self.c < 32768 else self.regs[self.c-32768]))

    def pnot(self):
        self.regs[self.a if self.a < 32768 else self.a-32768] = 32767 - (self.b if self.b < 32768 else self.regs[self.b-32768])

    def prmem(self):
        self.regs[self.a - 32768] = self.prog[self.b] if self.b < 32768 else self.prog[self.regs[self.b - 32768]]

    def pwmem(self):
        self.prog[self.a if self.a < 32768 else self.regs[self.a-32768]] = self.b if self.b < 32768 else self.regs[self.b-32768]

    def pcall(self):
        self.stack.append(self.ip+2)
        self.ip = self.a if self.a < 32768 else self.regs[self.a-32768]

    def pret(self): 
        if len(self.stack) == 0:   # empty stack = halt
            print("Stopping program - stack empty on ret")
            exit(0)
        try:
            self.ip = self.stack.pop()
        except:
            print('Stack underflow on ret - exiting...')
            exit(1)

    def pout(self):
        if self.slow:
            for _ in range(250000):       # slow down our output
                pass
        print(chr(self.prog[self.ip+1]) if self.prog[self.ip+1] < 32768 else chr(self.regs[self.prog[self.ip+1]-32768]), end='')

    def pin(self):      # Read from the given instruction list until it is empty, then read from stdin
        nxtchr = self.get_next_inchar()
        if nxtchr:                                  # Read from the list of commands in preference to accepting user input
            print(nxtchr, end='')
            self.regs[self.prog[self.ip+1] - 32768] = ord(nxtchr)
        else:
            self.regs[self.prog[self.ip+1] - 32768] = ord(sys.stdin.read(1))

    @staticmethod
    def pnoop():
        return

    def get_next_inchar(self):
        if self.inptr_auto < len(self.instr_auto):              # Any input string generated by helpers takes precedence over the user's input command file
            self.inptr_auto += 1
            return self.instr_auto[self.inptr_auto-1]
        while True:
            if self.inptr >= len(self.instr):
                return 0
            nxtchr = self.instr[self.inptr]
            if nxtchr == '~':   # stop processing this file
                self.inptr = len(self.instr)
                return 0
            elif nxtchr == '$':      # exit this program
                if len(self.used_ips) > 0:
                    self.output_used_ips()
                exit(0)
            elif nxtchr == '{':
                self.disasm = True
                self.inptr += 2
            elif nxtchr == '}':
                self.disasm = False
                self.inptr += 2
            elif nxtchr == '[':
                self.fulltrace = True
                self.inptr += 2
            elif nxtchr == ']':
                self.fulltrace = False
                self.inptr += 2
            elif nxtchr == '^':
                self.dump_vm()
                self.inptr += 2
            elif nxtchr == '<':
                self.slow = True
                self.inptr += 2
            elif nxtchr == '>':
                self.slow = False
                self.inptr += 2
            elif nxtchr == '=':
                self.instr_auto = solve_coin_puzzle()
                self.inptr_auto = 0
                self.inptr += 1
            elif nxtchr == '@':
                time.sleep(15)
                self.inptr += 1
            elif nxtchr == '!':
                print("\nCalculating energy level and fixing up the code to work the teleporter...\n")
                self.regs[7] = calc_energy_level()
                # now bypass the confirm mechanism
                self.prog[5489] = self.prog[5490] = 21    # noop out this instruction
                self.prog[5495] = 7                       # reverse meaning of the jump test
                self.inptr += 2
            elif nxtchr == '#':    # print any comments to the screen but don't forward to the VM
                print('#: ', end='')
                while nxtchr != '\n':
                    self.inptr += 1                    
                    nxtchr = self.instr[self.inptr]
                    print(nxtchr, end='')
                self.inptr += 1                    
            else:
                self.inptr += 1
                return self.instr[self.inptr-1]

    def run_vm(self):
        print("Running the VM...\n")
        count = 0
        MAX_EXEC = 0    # Used for testing only - sets max number of instructions before aborting; 0 = just keep going
        while self.ip < len(self.prog) and (count < MAX_EXEC or MAX_EXEC == 0):
            count += 1
            if self.disasm and self.ip not in self.used_ips:
                self.used_ips.append(self.ip)
            (op, inc), self.a, self.b, self.c = self.ops[self.prog[self.ip]], self.prog[self.ip+1], self.prog[self.ip+2], self.prog[self.ip+3]

            # This whole section allows us to output a disassembly of what is being executed in real time, together with register values
            if self.fulltrace:
                ops = [' ', ' ', ' ']
                try:
                    (op2, args) = self.opcodes[self.prog[self.ip]]
                except:
                    (op2, args) = 'self_modifying_code?', 0
                if args > 0:
                    for i in range(args):
                        if self.prog[self.ip + i + 1] < 32768:
                            ops[i] = str(self.prog[self.ip + i + 1])
                        elif 32768 <= self.prog[self.ip + i + 1] <= 32775:
                            ops[i] = '[' + str(self.prog[self.ip + i +1] - 32768) + ']'
                        else:
                            ops[i] = 'invalid'
                traceline = '{0: <8}'.format(str(self.ip)) + '{0: <8}'.format(str(self.prog[self.ip])) + '{0: <8}'.format(str(op2)) + '{0: <8}'.format(ops[0]) + '{0: <8}'.format(ops[1]) + '{0: <8}'.format(ops[2]) + str(self.regs) + '\n'
                self.tracefile.writelines(traceline)

            # This is the despatcher - where the real cool n funky magic happens - calling the right function based on a dictionary lookup of the opcode!
            if (self.test and op in [self.phalt, self.pout, self.pnoop]) or self.test == False:
                op()
                self.instcount += 1
            self.ip += inc

    def output_used_ips(self):
        self.used_ips.sort()
        print("Writing out a list of used ip addresses for disassembly")
        with open('usedips.txt', 'w') as fp:
            fp.write('\n'.join(str(ip) for ip in self.used_ips))
            fp.write('\n')

    def dump_vm(self):
        print("Dumping the current vm code to disk")
        with open('dumpvm.bin', "wb") as fp:        # Read in the binary program for the VM
            for p in self.prog:
                fp.write(p.to_bytes(2, 'little'))
    

def solve_coin_puzzle():
    print("Running helper function to solve the puzzle of the coins...")
    coins = {"red": 2, "concave": 7, "corroded": 3, "blue": 9, "shiny": 5 }
    for perm in itertools.permutations(coins):
        if coins[perm[0]] + coins[perm[1]] * coins[perm[2]] ** 2 + coins[perm[3]] ** 3 - coins[perm[4]] == 399:
            print("The correct order is as follows = ", perm, ". Inputting solution into VM...")
            return ''.join("use " + p + " coin\n" for p in perm)
    print("Solution not found; very strange; exiting...")
    exit(1)

def calc_energy_level():
    stored_result = 25734       # Short circuit long boring calc - set to 0 if you really want to wait for it to work out the code
    for i in range(stored_result, 32768):
        calc = funky(funky(i, i), i)
        if calc == 6:
            print(f"The target value for register 8 is {i}; calibrating the teleporter...")
            return i
        if i % 2000 == 0:
            print(f"Checking next 2000 candidate solutions, startng with {i:5d}")

def funky(i, j):
    funk1, funk2 = funky2(i, j + 1, 0x8000), funky2(i, j + 1, j * 0x8000) - 1
    return (funk1 * ((j + 1) * (j + 1) + j) + funk2 // j * (2 * j + 1)) & 0x7fff

def funky2(i, j, k):
    retval = 1
    for _ in range(i):
        retval = (retval * j) % k
    return retval

vm = VM("challenge.bin", "instr.txt", test=False, slow=False, disasm=False, trace=False)  # First argument is the binary program to run, the second argument is a list of instructions to provide as input to the VM
vm.run_vm()
