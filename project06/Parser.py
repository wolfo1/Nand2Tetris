"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """
    # types of commands
    A_CMD = "A_COMMAND"
    L_CMD = "L_COMMAND"
    C_CMD = "C_COMMAND"

    # comment prefix
    COMMENT_PREFIX = "//"

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

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
        self.curr_instruction = -1  # -1 means uninitialized.

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.curr_instruction < len(self.input_lines) - 1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.curr_instruction += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        line = self.input_lines[self.curr_instruction]
        # decides on command type based on existance of @ or ( and )
        if '@' in line:
            return Parser.A_CMD
        elif '(' in line and ')' in line:
            return Parser.L_CMD
        else:
            return Parser.C_CMD

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == Parser.A_CMD or \
                self.command_type() == Parser.L_CMD:
            line = self.input_lines[self.curr_instruction]
            # delete all characters that are not the symbol itself
            line = line.replace('(', "")
            line = line.replace(')', "")
            line = line.replace('@', "")
            return line

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        line = self.input_lines[self.curr_instruction]
        if self.command_type() == Parser.C_CMD:
            if '=' not in line:
                return ""
            index = line.find('=')
            return line[:index]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        line = self.input_lines[self.curr_instruction]
        if self.command_type() == Parser.C_CMD:
            eq_index = line.find('=')
            colon_index = line.find(';')
            if colon_index == -1:
                return line[eq_index+1:]
            return line[eq_index + 1:colon_index]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        line = self.input_lines[self.curr_instruction]
        if self.command_type() == Parser.C_CMD:
            colon_index = line.find(';')
            if colon_index == -1:
                return ""
            return line[colon_index+1:]

    def reset(self) -> None:
        """
        function resets the parser current instruction to -1 (before start)
        :return: None
        """
        self.curr_instruction = -1
