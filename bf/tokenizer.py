from dataclasses import dataclass

from enum import Enum, auto

class CommandType(Enum):
    INC_POINTER = auto()
    DEC_POINTER = auto()
    INC_DATA = auto()
    DEC_DATA = auto()
    SET_DATA = auto()
    RIGHT_SCAN = auto()
    LEFT_SCAN = auto()
    ADD_OFFSET_DATA = auto()
    ADD_OFFSET_DATA_INV = auto()
    SUB_OFFSET_DATA = auto()
    SUB_OFFSET_DATA_INV = auto()
    OUTPUT = auto()
    INPUT = auto()
    LOOP_START = auto()
    LOOP_END = auto()

# ---------- TOKEN CLASSES ----------
@dataclass
class Token:
    pass

@dataclass
class CommandToken(Token):
    type: CommandType

    def __init__(self, type: CommandType):
        self.type = type

@dataclass
class NumberInBracesToken(Token):
    value: int

    def __init__(self, value: int):
        self.value = value

@dataclass
class NumberInPipesToken(Token):
    value: int

    def __init__(self, value: int):
        self.value = value


# ---------- EXCEPTIONS ----------

class TokenizationError(Exception):
    pass


class MalformedIRError(TokenizationError):
    def __init__(self, message: str):
        super().__init__(message)


class MissingClosingCharacterError(TokenizationError):
    def __init__(self, open_char: str, index: int):
        message = f"ERROR: No closing '{open_char}' for '{open_char}' at index {index}"
        super().__init__(message)


class InvalidNumberError(TokenizationError):
    def __init__(self, num_str: str, index: int):
        message = f"ERROR: Can't convert string \"{num_str}\" to int at index {index}"
        super().__init__(message)


def tokenize(src: str) -> list[Token]:
    tokens: list[Token] = []
    idx = 0
    src_len = len(src)

    while idx < src_len:
        match src[idx]:
            case '>':
                tokens.append(CommandToken(CommandType.INC_POINTER))
            case '<':
                tokens.append(CommandToken(CommandType.DEC_POINTER))
            case '+':
                tokens.append(CommandToken(CommandType.INC_DATA))
            case '-':
                tokens.append(CommandToken(CommandType.DEC_DATA))
            case '=':
                tokens.append(CommandToken(CommandType.SET_DATA))
            case 'S':
                idx += 1
                if idx >= src_len:
                    raise MalformedIRError(f"ERROR: Unexpected end after 'S' at index {idx-1}")
                match src[idx]:
                    case '>':
                        tok: Token = CommandToken(CommandType.RIGHT_SCAN)
                        tokens.append(tok)
                    case '<':
                        tok: Token = CommandToken(CommandType.LEFT_SCAN)
                        tokens.append(tok)
                    case _:
                        raise MalformedIRError(f"ERROR: Malformed IR after 'S' at index {idx}")
            case 'a':
                idx += 1
                if idx >= src_len:
                    raise MalformedIRError(f"ERROR: Unexpected end after 'a' at index {idx-1}")
                match src[idx]:
                    case '+':
                        tok: Token = CommandToken(CommandType.ADD_OFFSET_DATA_INV)
                        tokens.append(tok)
                    case '-':
                        tok: Token = CommandToken(CommandType.ADD_OFFSET_DATA)
                        tokens.append(tok)
                    case _:
                        raise MalformedIRError(f"ERROR: Malformed IR after 'a' at index {idx}")
            case 's':
                idx += 1
                if idx >= src_len:
                    raise MalformedIRError(f"ERROR: Unexpected end after 's' at index {idx-1}")
                match src[idx]:
                    case '+':
                        tok: Token = CommandToken(CommandType.SUB_OFFSET_DATA_INV)
                        tokens.append(tok)
                    case '-':
                        tok: Token = CommandToken(CommandType.SUB_OFFSET_DATA)
                        tokens.append(tok)
                    case _:
                        raise MalformedIRError(f"ERROR: Malformed IR after 's' at index {idx}")
            case '.':
                tokens.append(CommandToken(CommandType.OUTPUT))
            case ',':
                tokens.append(CommandToken(CommandType.INPUT))
            case '[':
                tokens.append(CommandToken(CommandType.LOOP_START))
            case ']':
                tokens.append(CommandToken(CommandType.LOOP_END))
            case '{':
                open_idx = idx
                idx += 1
                # Find index of matching curly brace
                while idx < len(src) and src[idx] != '}':
                    idx += 1
                if idx == len(src):
                    raise MissingClosingCharacterError('{', open_idx)
                # Get value of string in curly braces
                num_str = src[open_idx+1:idx]
                num: int = 0
                try:
                    num = int(num_str)
                except ValueError:
                    raise InvalidNumberError(num_str, open_idx+1)
                tok = NumberInBracesToken(num)
                tokens.append(tok)
            case '|':
                open_idx = idx
                idx += 1
                # Find index of matching curly brace
                while idx < len(src) and src[idx] != '|':
                    idx += 1
                if idx == len(src):
                    raise MissingClosingCharacterError('|', open_idx)
                # Get value of string in curly braces
                num_str = src[open_idx+1:idx]
                num: int = 0
                try:
                    num = int(num_str)
                except ValueError:
                    raise InvalidNumberError(num_str, open_idx+1)
                tok = NumberInPipesToken(num)
                tokens.append(tok)
        idx += 1
    return tokens

