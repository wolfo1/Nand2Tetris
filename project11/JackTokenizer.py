"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


def parseLine(line):
    res = []
    line = line.split()
    for i in range(len(line)):
        start_idx = 0
        for j in range(len(line[i])):
            if line[i][j] in JackTokenizer.SYMBOLS:
                if line[i][start_idx:j] != "":
                    res.append(line[i][start_idx:j])
                res.append(line[i][j])
                start_idx = j + 1
        if start_idx < len(line[i]):
            res.append(line[i][start_idx:])
    return res


class JackTokenizer:
    COMMENT_PREFIX = "//"
    OPEN_COMMENT_PREFIX = "/*"
    CLOSE_COMMENT_PREFIX = "*/"
    SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
               '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
    KEYWORDS = ['class', 'constructor', 'function', 'method', 'field',
                'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
                'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
    STRING_PREFIX = "\""

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        input_lines = input_stream.read().splitlines()
        self.isString = False
        self.tokens = []
        self.currToken = -1  # -1 means uninitialized.
        comment = False
        # delete all comments, in line or long comments.
        pre_tokens = []
        for i in range(len(input_lines)):
            # find "/*" and "*/" if exists in line
            long_comment_open = input_lines[i].find(JackTokenizer.OPEN_COMMENT_PREFIX)
            long_comment_close = input_lines[i].find(JackTokenizer.CLOSE_COMMENT_PREFIX)
            # find "//" if exists in line
            comment_index = input_lines[i].find(JackTokenizer.COMMENT_PREFIX)
            # if there is a comment in line, delete it
            if comment:
                if long_comment_close != -1:
                    comment = False
                input_lines[i] = ""
            if comment_index != -1:
                input_lines[i] = input_lines[i][:comment_index]
            if long_comment_open != -1:
                if long_comment_close == -1:
                    comment = True
                input_lines[i] = ""
            if input_lines[i] != "":
                pre_tokens.append(input_lines[i].lstrip())

        # parse all text, split by characters while leaving string constants intact.
        for line in pre_tokens:
            start_idx = line.find(JackTokenizer.STRING_PREFIX)
            while start_idx != -1:
                for i in range(start_idx + 1, len(line)):
                    if line[i] == JackTokenizer.STRING_PREFIX:
                        end_idx = i
                        break
                self.tokens += parseLine(line[:start_idx])
                self.tokens.append(line[start_idx:end_idx + 1])
                line = line[end_idx + 1:]
                start_idx = line.find(JackTokenizer.STRING_PREFIX)
            self.tokens += parseLine(line)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?
        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.currToken < len(self.tokens) - 1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.currToken += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        token = self.tokens[self.currToken]
        if token[0] == JackTokenizer.STRING_PREFIX:
            if token[-1] != JackTokenizer.STRING_PREFIX:
                self.isString = True
            return "STRING_CONST"
        elif token[-1] == JackTokenizer.STRING_PREFIX:
            self.isString = False
            return "STRING_CONST"
        elif self.isString:
            return "STRING_CONST"
        elif token in JackTokenizer.KEYWORDS:
            return "KEYWORD"
        elif token in JackTokenizer.SYMBOLS:
            return "SYMBOL"
        elif token.isdigit():
            return "INT_CONST"
        else:
            return "IDENTIFIER"

    def get_name(self):
        if self.token_type() == "KEYWORD":
            return self.keyword().lower()
        elif self.token_type() == "SYMBOL":
            return self.symbol()
        elif self.token_type() == "IDENTIFIER":
            return self.identifier()
        elif self.token_type() == "INT_CONST":
            return self.int_val()
        elif self.token_type() == "STRING_CONST":
            return self.string_val()

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            return self.tokens[self.currToken].upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        if self.token_type() == "SYMBOL":
            return self.tokens[self.currToken]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        if self.token_type() == "IDENTIFIER":
            return self.tokens[self.currToken]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        if self.token_type() == "INT_CONST":
            return int(self.tokens[self.currToken])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        if self.token_type() == "STRING_CONST":
            return self.tokens[self.currToken][1:-1]
