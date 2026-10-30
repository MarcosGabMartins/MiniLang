import pytest
from minilang.analysis.parser import Parser, ParseError
from minilang.spec.tokens import Token, TokenType

def test_advance_no_eof_devolve_eof_e_nao_move_cursor():
    tokens = [Token(TokenType.EOF, "", 1, 1)]
    parser = Parser(tokens)
    
    primeiro = parser.advance()
    assert primeiro.type is TokenType.EOF
    assert parser.current == 0
    
    segundo = parser.advance()
    assert segundo.type is TokenType.EOF
    assert parser.current == 0

def test_expect_com_tipo_errado_levanta_parse_error():
    tokens = [Token(TokenType.IDENT, "x", 1, 1), Token(TokenType.EOF, "", 1, 2)]
    parser = Parser(tokens)
    
    with pytest.raises(ParseError) as exc_info:
        parser.expect(TokenType.SEMICOLON, "';'")
        
    diagnostic = exc_info.value.diagnostic
    assert diagnostic.line == 1
    assert diagnostic.column == 1
    assert diagnostic.message == "esperado ';', encontrado 'x'"

def test_match_sem_casar_nao_consome():
    tokens = [Token(TokenType.IDENT, "x", 1, 1), Token(TokenType.EOF, "", 1, 2)]
    parser = Parser(tokens)
    
    casou = parser.match(TokenType.PLUS, TokenType.MINUS)
    
    assert not casou
    assert parser.current == 0
    assert parser.peek().type is TokenType.IDENT