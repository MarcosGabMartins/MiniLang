"""Testes dos nós da AST e do visualizador textual

dev_note:
    Os nós são montados à mão, sem lexer, e comparados pela forma compacta (str), como o test_lexer
    compara strings compactas de tokens
"""

import pytest

from minilang.spec.syntax_tree import (Assignment, Binary, Declaration, Integer, Output, Program,
                                       Variable, format_tree)
from minilang.spec.tokens import Token, TokenType


def token(token_type: TokenType, lexeme: str) -> Token:
    return Token(token_type, lexeme, 1, 1)      # Posição fixa: aqui só importa a forma


def integer(lexeme: str) -> Integer:
    return Integer(token(TokenType.INT_LITERAL, lexeme))


def variable(name: str) -> Variable:
    return Variable(token(TokenType.IDENT, name))


def binary(symbol: str, token_type: TokenType, left, right) -> Binary:
    return Binary(token(token_type, symbol), left, right)


# 2 + 3 * 4
PRECEDENCE = binary("+", TokenType.PLUS, integer("2"),
                    binary("*", TokenType.STAR, integer("3"), integer("4")))

# (2 + 3) * 4
PARENTHESES = binary("*", TokenType.STAR,
                     binary("+", TokenType.PLUS, integer("2"), integer("3")), integer("4"))

# 10 - 3 - 2
LEFT_ASSOCIATIVITY = binary("-", TokenType.MINUS,
                            binary("-", TokenType.MINUS, integer("10"), integer("3")), integer("2"))

# int x; x = 2 + 3 * 4; print(x);
SLIDE_PROGRAM = Program((
    Declaration(token(TokenType.IDENT, "x")),
    Assignment(token(TokenType.IDENT, "x"), PRECEDENCE),
    Output(variable("x")),
))

COMPACT = [
    (Program(()), "Programa([])"),
    (integer("2"), "Inteiro(2)"),
    (integer("007"), "Inteiro(007)"),
    (variable("total"), "Variavel(total)"),
    (Declaration(token(TokenType.IDENT, "x")), "Declaracao(x)"),
    (Output(variable("y")), "Saida(Variavel(y))"),
    (Assignment(token(TokenType.IDENT, "x"), integer("10")), "Atribuicao(x, Inteiro(10))"),
    (PRECEDENCE, "Binaria(+, Inteiro(2), Binaria(*, Inteiro(3), Inteiro(4)))"),
    (PARENTHESES, "Binaria(*, Binaria(+, Inteiro(2), Inteiro(3)), Inteiro(4))"),
    (LEFT_ASSOCIATIVITY, "Binaria(-, Binaria(-, Inteiro(10), Inteiro(3)), Inteiro(2))"),
    (SLIDE_PROGRAM,
     "Programa([Declaracao(x), Atribuicao(x, Binaria(+, Inteiro(2), Binaria(*, Inteiro(3), "
     "Inteiro(4)))), Saida(Variavel(x))])"),
]

TREES = [
    (Program(()), "Programa"),
    (variable("x"), "Variavel(x)"),
    (PRECEDENCE,
     "Binaria(+)\n"
     "├── Inteiro(2)\n"
     "└── Binaria(*)\n"
     "    ├── Inteiro(3)\n"
     "    └── Inteiro(4)"),
    # O Atribuicao é o irmão do meio: seus filhos usam o prefixo '│   '
    (SLIDE_PROGRAM,
     "Programa\n"
     "├── Declaracao(x)\n"
     "├── Atribuicao(x)\n"
     "│   └── Binaria(+)\n"
     "│       ├── Inteiro(2)\n"
     "│       └── Binaria(*)\n"
     "│           ├── Inteiro(3)\n"
     "│           └── Inteiro(4)\n"
     "└── Saida\n"
     "    └── Variavel(x)"),
]


@pytest.mark.parametrize("node, expected", COMPACT)
def test_compact_form(node, expected):
    assert str(node) == expected


@pytest.mark.parametrize("node, expected", TREES)
def test_format_tree(node, expected):
    assert format_tree(node) == expected


def test_empty_program_has_no_children():
    assert Program(()).children() == ()


def test_integer_keeps_the_lexeme_as_written():
    assert integer("007").label() == "Inteiro(007)"


def test_nodes_keep_the_origin_token():
    origin = Token(TokenType.IDENT, "x", 3, 7)
    assert Variable(origin).name.line == 3
    assert Variable(origin).name.column == 7


def test_nodes_are_frozen():
    node = integer("2")
    with pytest.raises(Exception):
        node.value = token(TokenType.INT_LITERAL, "3")