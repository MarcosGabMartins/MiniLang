"""Testes do catálogo da gramática: consistência interna e amarração com o Parser"""

import pytest

from minilang.analysis.lexer import Lexer
from minilang.spec.grammar import (ADDITIVE_OPERATORS, GRAMMAR, MULTIPLICATIVE_OPERATORS, PRODUCTIONS,
                                   Production)
from minilang.spec.tokens import TokenType

EXAMPLES = [(production, example) for production in GRAMMAR for example in production.examples]


def ids(pairs):
    return [f"{production.name}:{example!r}" for production, example in pairs]


def alternatives(rule: str) -> tuple[str, list[list[str]]]:
    left, right = rule.split(" → ")
    return left.strip(), [alternative.split() for alternative in right.split(" | ")]


def first_of(symbol: str) -> frozenset[TokenType]:
    if symbol in TokenType.__members__:
        return frozenset({TokenType[symbol]})
    if symbol.endswith("′"):                    
        return PRODUCTIONS[symbol.removesuffix("′")].operators
    return PRODUCTIONS[symbol].first


def follow_of(symbol: str) -> frozenset[TokenType]:
    return PRODUCTIONS[symbol.removesuffix("′")].follow


def test_production_names_and_methods_are_unique():
    assert len(PRODUCTIONS) == len(GRAMMAR)
    assert len({production.method for production in GRAMMAR}) == len(GRAMMAR)
    assert len({production.function for production in GRAMMAR}) == len(GRAMMAR)


def test_operator_sets_come_from_the_catalog():
    assert ADDITIVE_OPERATORS == {TokenType.PLUS, TokenType.MINUS}
    assert MULTIPLICATIVE_OPERATORS == {TokenType.STAR, TokenType.SLASH}


@pytest.mark.parametrize("production", GRAMMAR, ids=lambda production: production.name)
def test_first_matches_the_rules(production: Production):
    left, alts = alternatives(production.rules[0])
    assert left == production.name
    union = frozenset().union(*(first_of(alt[0]) for alt in alts if alt != ["ε"]))
    assert union == production.first


@pytest.mark.parametrize("production", GRAMMAR, ids=lambda production: production.name)
def test_ll1_alternatives_are_disjoint(production: Production):
    for rule in production.rules:
        left, alts = alternatives(rule)
        sets = [follow_of(left) if alt == ["ε"] else first_of(alt[0]) for alt in alts]
        for index, current in enumerate(sets):
            for other in sets[index + 1:]:
                assert not current & other, f"{rule}: {sorted(t.name for t in current & other)}"


@pytest.mark.parametrize("production", [p for p in GRAMMAR if p.nullable], ids=lambda p: p.name)
def test_nullable_first_and_follow_are_disjoint(production: Production):
    assert not production.first & production.follow


@pytest.mark.parametrize("production", [p for p in GRAMMAR if p.operators], ids=lambda p: p.name)
def test_operators_are_the_first_of_the_continuation(production: Production):
    _, alts = alternatives(production.rules[1])
    operators = {TokenType[alt[0]] for alt in alts if alt != ["ε"]}
    assert operators == production.operators
    assert not production.operators & production.follow


@pytest.mark.parametrize("production, example", EXAMPLES, ids=ids(EXAMPLES))
def test_example_starts_in_first(production: Production, example: str):
    tokens, diagnostics = Lexer(example).scan_tokens()
    assert not diagnostics, f"{example!r} tem erro lexico: {diagnostics}"
    if example == "":
        assert production.nullable, f"{production.name} não aceita a entrada vazia"
        assert tokens[0].type in production.follow
    else:
        assert tokens[0].type in production.first

@pytest.mark.parametrize("production", GRAMMAR, ids=lambda production: production.name)
def test_every_method_exists_in_parser(production: Production):
    from minilang.analysis.parser import Parser
    assert callable(getattr(Parser, production.method, None)), production.method


@pytest.mark.parametrize("production, example", EXAMPLES, ids=ids(EXAMPLES))
def test_example_is_recognized_by_its_own_method(production: Production, example: str):
    from minilang.analysis.parser import Parser

    tokens, _ = Lexer(example).scan_tokens()
    parser = Parser(tokens)
    getattr(parser, production.method)()    
    assert parser.at_end(), f"{production.name} {example!r}: sobrou {parser.peek()}"