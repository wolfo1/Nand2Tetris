"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.
    """
    # C command types
    C_MATH = "C_ARITHMETIC"
    C_PUSH = "C_PUSH"
    C_POP = "C_POP"
    C_LABEL = "C_LABEL"
    C_GOTO = "C_GOTO"
    C_IFGOTO = "C_IF-GOTO"
    C_FUNCTION = "C_FUNCTION"
    C_RETURN = "C_RETURN"
    C_CALL = "C_CALL"
    # groups of types of commands.
    MEMORY_CMDS = [C_PUSH, C_POP]
    BRANCHING_CMDS = [C_LABEL, C_GOTO, C_IFGOTO]
    FUNC_CMDS = [C_FUNCTION, C_CALL]
    # delete comments that starts with this prefix.
    COMMENT_PREFIX = "//"

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        # delete every comment in the text
        for i in range(len(self.input_lines)):
            comment_index = self.input_lines[i].find(Parser.COMMENT_PREFIX)
            if comment_index != -1:
                self.input_lines[i] = self.input_lines[i][:comment_index]
        # delete all whitespaces
        self.input_lines = [line.replace(" ", "") for line in self.input_lines]
        # delete all empty lines
        self.input_lines = [line for line in self.input_lines if line != ""]
        # index will be used to point to current instruction.
        self.curr_cmd = -1  # -1 means uninitialized.

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.curr_cmd < len(self.input_lines) - 1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.curr_cmd += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IFGOTO", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # go over each possibility.
        line = self.input_lines[self.curr_cmd]
        if self.C_POP[2:].lower() in line:
            return self.C_POP
        elif self.C_PUSH[2:].lower() in line:
            return self.C_PUSH
        elif self.C_LABEL[2:].lower() in line:
            return self.C_LABEL
        elif self.C_IFGOTO[2:].lower() in line:
            return self.C_IFGOTO
        elif self.C_GOTO[2:].lower() in line:
            return self.C_GOTO
        elif self.C_FUNCTION[2:].lower() in line:
            return self.C_FUNCTION
        elif self.C_CALL[2:].lower() in line:
            return self.C_CALL
        elif self.C_RETURN[2:].lower() in line:
            return self.C_RETURN
        else:
            return self.C_MATH

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        line = self.input_lines[self.curr_cmd]
        # get the length of the command itself
        cmd_length = len(self.command_type()) - 2
        if self.command_type() != self.C_RETURN:
            # base case, arithmetic command
            if self.command_type() == self.C_MATH:
                return line
            # case 2, branching command with no number in the end
            elif self.command_type() in self.BRANCHING_CMDS:
                return line[cmd_length:]
            # case 3, find the index of the first digit
            else:
                digit_index = [char.isdigit() for char in line].index(True)
                return line[cmd_length:digit_index]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        line = self.input_lines[self.curr_cmd]
        if self.command_type() in self.MEMORY_CMDS or self.command_type() in self.C_FUNCTION:
            digit_index = [char.isdigit() for char in line].index(True)
            return int(line[digit_index:])
