"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

# the prefix A command or C command starts with
A_CMD_PREFIX = "0"
C_CMD_PREFIX = "111"


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    symbols = SymbolTable()
    parser = Parser(input_file)
    address_count = 0
    # first pass. comments are already deleted in Parser class init.
    while parser.has_more_commands():
        parser.advance()
        # add each L command to SymbolTable
        if parser.command_type() == Parser.L_CMD:
            symbols.add_entry(parser.symbol(), address_count)
        else:
            address_count += 1
    # Second Pass.
    parser.reset()
    var_count = 0
    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()
        if cmd_type == Parser.A_CMD:
            a_symbol = parser.symbol()
            # A command is numeric or variable, writes binary cmd accordingly
            if a_symbol.isnumeric():
                a_binary = '{0:015b}'.format(int(a_symbol))
            else:
                if not symbols.contains(a_symbol):
                    symbols.add_entry(a_symbol, var_count + SymbolTable.FIRST_USABLE_INDEX)
                    var_count += 1
                a_binary = '{0:015b}'.format(symbols.get_address(a_symbol))
            print(A_CMD_PREFIX + a_binary, file=output_file)

        elif cmd_type == Parser.C_CMD:
            # builds C command using Code class and writes into output file
            c_command = Code.comp(parser.comp())
            c_command += Code.dest(parser.dest())
            c_command += Code.jump(parser.jump())
            print(C_CMD_PREFIX + c_command, file=output_file)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
