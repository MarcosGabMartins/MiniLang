"""Análise sintática da MiniLang: descendente recursiva, um método por não-terminal

dev_note:
    O parser mantém um cursor sobre a lista de tokens. Toda leitura passa por peek/advance/match/expect, e advance
    nunca passa do EOF - o lexer garante que ele é o último token

    Correspondência com o enunciado: programa -> program, lista_itens -> item_list, item -> item,
    declaracao -> declaration, atribuicao -> assignment, saida -> output, expressao -> expression,
    termo -> term, fator -> factor
"""

from ..spec.grammar import ADDITIVE_OPERATORS, MULTIPLICATIVE_OPERATORS
from ..spec.syntax_tree import (Assignment, Binary, Declaration, Expression, Integer, Item, Output,
                                Program, Variable)
from ..spec.tokens import Diagnostic, Token, TokenType


class ParseError(Exception):
    """Só desenrola a pilha até parse() - nunca sai do módulo"""

    def __init__(self, diagnostic: Diagnostic):
        super().__init__(str(diagnostic))
        self.diagnostic = diagnostic


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0        # Indice do token sob o cursor

    # --- Grupo 1 --- Olhar sem consumir
    def at_end(self) -> bool:
        return self.peek().type is TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    # --- Grupo 2 --- Consumir
    def advance(self) -> Token:
        token = self.peek()
        if not self.at_end():       # O EOF nunca é ultrapassado
            self.current += 1
        return token

    def match(self, *types: TokenType) -> bool:
        if self.peek().type not in types:
            return False

        self.advance()
        return True

    def expect(self, token_type: TokenType, expected: str) -> Token:
        if self.peek().type is token_type:
            return self.advance()
        raise self.error(expected)

    # --- Grupo 3 --- Diagnóstico
    def error(self, expected: str) -> ParseError:
        token = self.peek()
        found = "fim da entrada" if token.type is TokenType.EOF else repr(token.lexeme)
        return ParseError(Diagnostic(
            token.lexeme, token.line, token.column, f"esperado {expected}, encontrado {found}"
        ))

    # --- Grupo 4 --- Entrada pública
    def parse(self) -> tuple[Program | None, list[Diagnostic]]:
        try:
            return self.program(), []
        except ParseError as error:
            return None, [error.diagnostic]

    # --- Grupo 5 --- Comandos           (Fase 4 - Pessoa 5)
    def program(self) -> Program:
        pass
        
    def item_list(self) -> list[Item]:
        pass
        
    def item(self) -> Item:
        pass
        
    def assignment(self) -> Assignment:
        pass

    def declaration(self) -> Declaration:
        self.expect(TokenType.KW_INT, "'int'")
        name = self.expect(TokenType.IDENT, "identificador")
        self.expect(TokenType.SEMICOLON, "';'")
        return Declaration(name)

    def output(self) -> Output:
        self.expect(TokenType.KW_PRINT, "'print'")
        self.expect(TokenType.LPAREN, "'('")
        value = self.expression()
        self.expect(TokenType.RPAREN, "')'")
        self.expect(TokenType.SEMICOLON, "';'")
        return Output(value)

    # --- Grupo 6 --- Expressões         (Fase 3 - Pessoa 4)
    def expression(self) -> Expression:
        pass

    def term(self) -> Expression:
        left = self.factor()
        while self.peek().type in MULTIPLICATIVE_OPERATORS:
            operator = self.advance()
            right = self.factor()
            left = Binary(operator, left, right)
        return left

    def factor(self) -> Expression:
        token = self.peek()
        if token.type is TokenType.INT_LITERAL:
            return Integer(self.advance())
        if token.type is TokenType.IDENT:
            return Variable(self.advance())
        if self.match(TokenType.LPAREN):
            inner = self.expression()
            self.expect(TokenType.RPAREN, "')'")
            return inner                    # Parênteses não viram nó
        raise self.error("numero, identificador ou '('")