import unittest

from bf.tokenizer import (
    tokenize,
    CommandType,
    CommandToken,
    NumberInBracesToken,
    NumberInPipesToken,
    MalformedIRError,
    MissingClosingCharacterError,
    InvalidNumberError
)
from typing import cast

class TestTokenizer(unittest.TestCase):

    def test_single_command_tokens(self):
        commands = {
            '>': CommandType.INC_POINTER,
            '<': CommandType.DEC_POINTER,
            '+': CommandType.INC_DATA,
            '-': CommandType.DEC_DATA,
            '=': CommandType.SET_DATA,
            'S>': CommandType.RIGHT_SCAN,
            'S<': CommandType.LEFT_SCAN,
            'a+': CommandType.ADD_OFFSET_DATA_INV,
            'a-': CommandType.ADD_OFFSET_DATA,
            's+': CommandType.SUB_OFFSET_DATA_INV,
            's-': CommandType.SUB_OFFSET_DATA,
            '.': CommandType.OUTPUT,
            ',': CommandType.INPUT,
            '[': CommandType.LOOP_START,
            ']': CommandType.LOOP_END
        }

        for input_str, cmd_type in commands.items():
            with self.subTest(input_str=input_str):
                tokens = tokenize(input_str)
                self.assertEqual(len(tokens), 1)
                self.assertIsInstance(tokens[0], CommandToken)
                self.assertEqual(cast(CommandToken, tokens[0]).type, cmd_type)

    def test_number_in_braces(self):
        tokens = tokenize("{123}")
        self.assertEqual(len(tokens), 1)
        self.assertIsInstance(tokens[0], NumberInBracesToken)
        self.assertEqual(cast(NumberInBracesToken, tokens[0]).value, 123)

    def test_number_in_pipes(self):
        tokens = tokenize("|456|")
        self.assertEqual(len(tokens), 1)
        self.assertIsInstance(tokens[0], NumberInPipesToken)
        self.assertEqual(cast(NumberInPipesToken, tokens[0]).value, 456)

    def test_composite_input(self):
        input_str = ">a-S>+{789}|1011|.[,]"
        tokens = tokenize(input_str)
        expected_types = [
            CommandType.INC_POINTER,
            CommandType.ADD_OFFSET_DATA,
            CommandType.RIGHT_SCAN,
            CommandType.INC_DATA,
            NumberInBracesToken,
            NumberInPipesToken,
            CommandType.OUTPUT,
            CommandType.LOOP_START,
            CommandType.INPUT,
            CommandType.LOOP_END
        ]
        self.assertEqual(len(tokens), len(expected_types))
        for token, expected in zip(tokens, expected_types):
            if isinstance(expected, CommandType):
                self.assertIsInstance(token, CommandToken)
                self.assertEqual(cast(CommandToken, token).type, expected)
            elif expected == NumberInBracesToken:
                self.assertIsInstance(token, NumberInBracesToken)
            elif expected == NumberInPipesToken:
                self.assertIsInstance(token, NumberInPipesToken)

    def test_malformed_ir_after_S(self):
        with self.assertRaises(MalformedIRError):
            tokenize("S*")

    def test_malformed_ir_after_a(self):
        with self.assertRaises(MalformedIRError):
            tokenize("a*")

    def test_malformed_ir_after_s(self):
        with self.assertRaises(MalformedIRError):
            tokenize("s*")

    def test_missing_closing_brace(self):
        with self.assertRaises(MissingClosingCharacterError):
            tokenize("{123")

    def test_missing_closing_pipe(self):
        with self.assertRaises(MissingClosingCharacterError):
            tokenize("|456")

    def test_invalid_number_in_braces(self):
        with self.assertRaises(InvalidNumberError):
            tokenize("{abc}")

    def test_invalid_number_in_pipes(self):
        with self.assertRaises(InvalidNumberError):
            tokenize("|def|")

    def test_unexpected_end_after_S(self):
        with self.assertRaises(MalformedIRError):
            tokenize("S")

    def test_unexpected_end_after_a(self):
        with self.assertRaises(MalformedIRError):
            tokenize("a")

    def test_unexpected_end_after_s(self):
        with self.assertRaises(MalformedIRError):
            tokenize("s")

    def test_unknown_characters(self):
        try:
            tokens = tokenize("!@#$%^&*")
            self.assertEqual(len(tokens), 0)
        except Exception as e:
            self.fail(f"tokenize() raised exception {type(e)} unexpectedly")


if __name__ == '__main__':
    unittest.main()
