"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    KINDINDEX = {"STATIC": 0, "FIELD": 1, "ARG": 2, "VAR": 3}

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.classTable = {}
        self.subroutineTable = {}
        self.indexes = [-1, -1, -1, -1]
        self.classScope = True

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # NOTE: "THIS" SHOULD BE THE FIRST ARGUMENT IN SUBROUTINE SCOPE
        self.subroutineTable = {}
        self.classScope = False
        self.indexes[2] = -1
        self.indexes[3] = -1

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        kind = kind.upper()
        if kind == "STATIC" or kind == "FIELD":
            self.indexes[SymbolTable.KINDINDEX[kind]] += 1
            self.classTable[name] = [type, kind, self.indexes[SymbolTable.KINDINDEX[kind]]]
        elif kind == "ARG" or kind == "VAR":
            self.indexes[SymbolTable.KINDINDEX[kind]] += 1
            self.subroutineTable[name] = [type, kind, self.indexes[SymbolTable.KINDINDEX[kind]]]

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.indexes[SymbolTable.KINDINDEX[kind]] + 1

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.classTable.get(name):
            return self.classTable.get(name)[1]
        elif self.subroutineTable.get(name):
            return self.subroutineTable.get(name)[1]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.classTable.get(name):
            return self.classTable.get(name)[0]
        elif self.subroutineTable.get(name):
            return self.subroutineTable.get(name)[0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if self.classTable.get(name):
            return self.classTable.get(name)[2]
        elif self.subroutineTable.get(name):
            return self.subroutineTable.get(name)[2]
