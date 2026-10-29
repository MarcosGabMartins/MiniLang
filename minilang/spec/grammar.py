"""Catálogo da gramática da MiniLang (G2) para o analisador sintático

    Cada não-terminal carrega a definição teórica dos slides (produções de G2, FIRST e FOLLOW) e aponta para o
    método do Parser que o implementa. Os conjuntos são só notação: o parser é descendente recursivo escrito à
    mão e não é dirigido por esta tabela

    A tabela é a fonte única dos operadores de cada nível (ADDITIVE_OPERATORS e MULTIPLICATIVE_OPERATORS) e o
    lugar onde a correspondência de nomes vira dado verificável: o nome do slide (Expr), o da função do
    enunciado (expressao) e o do método do Parser (expression) ficam lado a lado
"""

from dataclasses import dataclass

from .tokens import TokenType

# Conjuntos que se repetem entre as entradas
_COMMAND_START = frozenset({TokenType.KW_INT, TokenType.IDENT, TokenType.KW_PRINT})
_COMMAND_FOLLOW = _COMMAND_START | {TokenType.EOF}
_EXPRESSION_START = frozenset({TokenType.LPAREN, TokenType.IDENT, TokenType.INT_LITERAL})
_EXPRESSION_END = frozenset({TokenType.SEMICOLON, TokenType.RPAREN})


@dataclass(frozen=True)
class Production:
    name: str                       # Não-terminal dos slides (A06/A07): "Expr"
    function: str                   # Função que o enunciado pede (T02 s5): "expressao"
    method: str                     # Método do Parser que a implementa: "expression"
    purpose: str
    rules: tuple[str, ...]          # Produções de G2, incluindo a continuação - só documentação
    first: frozenset[TokenType]     # Sem ε; `nullable` diz se ε entra
    follow: frozenset[TokenType]
    examples: tuple[str, ...]
    nullable: bool = False
    operators: frozenset[TokenType] = frozenset()   # Só Expr e Termo


GRAMMAR: list[Production] = [
    Production(
        name="Programa",
        function="programa",
        method="program",
        purpose="Símbolo inicial: uma lista de itens seguida do fim da entrada. O programa vazio é válido.",
        rules=("Programa → ListaItens",),
        first=_COMMAND_START,
        follow=frozenset({TokenType.EOF}),
        nullable=True,
        examples=("", "print(y);", "int x;\nx = 2 + 3 * 4;\nprint(x);"),
    ),
    Production(
        name="ListaItens",
        function="lista_itens",
        method="item_list",
        purpose="Zero ou mais comandos em sequência. Termina no EOF; qualquer outro token tem que iniciar um item.",
        rules=("ListaItens → Item ListaItens | ε",),
        first=_COMMAND_START,
        follow=frozenset({TokenType.EOF}),
        nullable=True,
        examples=("", "int x;", "int x;\nx = 1;\nprint(x);"),
    ),
    Production(
        name="Item",
        function="item",
        method="item",
        purpose="Um comando. O primeiro token decide qual: 'int', identificador ou 'print'.",
        rules=("Item → Declaracao | Atribuicao | Saida",),
        first=_COMMAND_START,
        follow=_COMMAND_FOLLOW,
        examples=("int x;", "x = 10;", "print(x);"),
    ),
    Production(
        name="Declaracao",
        function="declaracao",
        method="declaration",
        purpose="Declara uma variável inteira. Não há declaração com inicialização (A06 s89).",
        rules=("Declaracao → KW_INT IDENT SEMICOLON",),
        first=frozenset({TokenType.KW_INT}),
        follow=_COMMAND_FOLLOW,
        examples=("int x;", "int total;", "int intx;"),
    ),
    Production(
        name="Atribuicao",
        function="atribuicao",
        method="assignment",
        purpose="Atribui o valor de uma expressão a uma variável.",
        rules=("Atribuicao → IDENT ASSIGN Expr SEMICOLON",),
        first=frozenset({TokenType.IDENT}),
        follow=_COMMAND_FOLLOW,
        examples=("x = 10;", "x = 2 + 3 * 4;", "total = saldo + 10 - desconto;"),
    ),
    Production(
        name="Saida",
        function="saida",
        method="output",
        purpose="Imprime o valor de uma expressão entre parênteses.",
        rules=("Saida → KW_PRINT LPAREN Expr RPAREN SEMICOLON",),
        first=frozenset({TokenType.KW_PRINT}),
        follow=_COMMAND_FOLLOW,
        examples=("print(y);", "print(2 + 3 * 4);", "print((2 + 3) * 4);"),
    ),
    Production(
        name="Expr",
        function="expressao",
        method="expression",
        purpose="Nível de menor precedência: soma e subtração, associativas à esquerda na AST.",
        rules=(
            "Expr → Termo Expr′",
            "Expr′ → PLUS Termo Expr′ | MINUS Termo Expr′ | ε",
        ),
        first=_EXPRESSION_START,
        follow=_EXPRESSION_END,
        operators=frozenset({TokenType.PLUS, TokenType.MINUS}),
        examples=("2", "total-2", "10 - 3 - 2", "saldo + 10 - desconto", "(2 + 3) * 4"),
    ),
    Production(
        name="Termo",
        function="termo",
        method="term",
        purpose="Nível intermediário: multiplicação e divisão, associativas à esquerda na AST.",
        rules=(
            "Termo → Fator Termo′",
            "Termo′ → STAR Fator Termo′ | SLASH Fator Termo′ | ε",
        ),
        first=_EXPRESSION_START,
        follow=frozenset({TokenType.PLUS, TokenType.MINUS}) | _EXPRESSION_END,
        operators=frozenset({TokenType.STAR, TokenType.SLASH}),
        examples=("2", "2 * 3", "8 / 4 / 2", "a * (b - c) / d"),
    ),
    Production(
        name="Fator",
        function="fator",
        method="factor",
        purpose="Nível de maior precedência: literal, identificador ou expressão entre parênteses.",
        rules=("Fator → LPAREN Expr RPAREN | IDENT | INT_LITERAL",),
        first=_EXPRESSION_START,
        follow=frozenset({TokenType.STAR, TokenType.SLASH, TokenType.PLUS, TokenType.MINUS}) | _EXPRESSION_END,
        examples=("x", "007", "(2 + 3)", "((x))"),
    ),
]

PRODUCTIONS = {production.name: production for production in GRAMMAR}

# Os conjuntos que o Parser consulta - derivados da tabela, nunca repetidos 
ADDITIVE_OPERATORS = PRODUCTIONS["Expr"].operators
MULTIPLICATIVE_OPERATORS = PRODUCTIONS["Termo"].operators