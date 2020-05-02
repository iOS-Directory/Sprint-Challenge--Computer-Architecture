"""CPU functionality."""

import sys

# LDI: load "immediate", store a value in a register, or "set this register to this value".
LDI = 0b10000010  # Decimal = 130
# PRN: a pseudo-instruction that prints the numeric value stored in a register.
PRN = 0b01000111  # Decimal = 71
HLT = 0b00000001  # # Decimal = 1, HLT: halt the CPU and exit the emulator.
MUL = 0b10100010  # Decimal = 162
ADD = 0b10100000
SP = 7  # Stack Pointer
PUSH = 0b01000101  # Decimal = 69, address `F4` if the stack is empty.
POP = 0b01000110  # Decimal = 170
# Calls a subroutine (function) at the address stored in the register.
CALL = 0b01010000  # Decimal = 80
RET = 0b00010001  # Decimal = 17, Return from subroutine.


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8  # Register R0-R7
        self.ram = [0] * 256
        self.pc = 0  # Program Counter, which is the address/index of the current instruction
        self.running = True
    # Accepts the address to read and return the value stored there.

    def ram_read(self, address):
        return self.ram[address]

    # Accept a value to write, and the address to write it to.
    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        # Read the entry in the comand line to get the file name we pass in
        #sys.argv[0] == "ls8.py"
        #sys.argv[1] == "examples/mult.ls8"
        program_filename = sys.argv[1]
        # print(f"File: {program_filename}")
        # Un-hardcode the machine code
        try:
            with open(program_filename) as f:
                address = 0
                for line in f:
                    # split comments
                    comments = line.strip().split("#")
                    # take only the first element in the line
                    string = comments[0].strip()
                    # Skip empty lines
                    if string == "":
                        continue
                    # Convert binary string to integer
                    int_val = int(string, 2)
                    self.ram[address] = int_val
                    address += 1
                    # close file
                f.close()

        except FileNotFoundError:
            print("No File name found in the command line.")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # It needs to read the memory address that's stored in register `PC
            # Which is the current index in memory
            ir = self.ram_read(self.pc)
            # Sometimes the byte value is a register number,other times it's a constant value
            # Reg/Arg is one index over the pc
            operand_a = self.ram_read(self.pc + 1)
            # Value is one index over the pc
            operand_b = self.ram_read(self.pc + 2)
            # perform the actions needed for the instruction per the LS-8 spec
            if ir == LDI:
                # sets a specified register to a specified value.
                self.reg[operand_a] = operand_b
                self.pc += 3  # Add 3 to skip the operand_a & operand_b
            elif ir == PRN:
                print(self.reg[operand_a])  # Print value in given rgister
                self.pc += 2  # Add 2 to move to HLT
            # Check the LS-8 spec for what the `MUL` instruction does.
            elif ir == MUL:
                # called the `alu()`
                self.alu(ir, operand_a, operand_b)
                self.pc += 3
            elif ir == ADD:
                self.alu(ir, operand_a, operand_b)
                self.pc += 3
            elif ir == PUSH:
                # Decrement the stack pointer
                self.reg[SP] -= 1  # Address of top of stack
                # Copy value from register into memeory RAM
                value = self.reg[operand_a]
                # Get the address
                adress = self.reg[SP]
                #store in memeory
                #self.ram[adress] = value
                self.ram_write(adress, value)
                # increase pointer "SP"
                self.pc += 2
            elif ir == POP:
                # Get the value from the address pointed to by `SP`
                val = self.ram_read(self.reg[SP])
                # Copy the value from the address pointed to by `SP` to the given register.
                self.reg[operand_a] = val
                # Increment `SP`
                self.reg[SP] += 1
                self.pc += 2
            elif ir == CALL:
                # The address of the instruction directly after `CALL` is pushed onto the stack
                self.reg[SP] -= 1
                adress = self.reg[SP]
                value = self.pc + 2
                self.ram_write(adress, value)
                # The PC is set to the address stored in the given register
                self.pc = self.reg[operand_a]
            elif ir == RET:
                # Pop the value from the top of the stack and store it in the `PC`.
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1
            elif ir == HLT:
                running = False
            else:
                print(f"Unknown instruction of: {ir}")
                running = False


# cpu = CPU()
# cpu.load()
# cpu.run()
