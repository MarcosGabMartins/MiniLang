"""Nós da árvore sintática abstrata da MiniLang e o visualizador textual

dev_note:
    Os nós guardam o Token de origem, não só o lexema - a análise semântica vai precisar da posição
    Os rótulos seguem o enunciado (Programa, Declaracao(x), Binaria(+)) porque são saída, não identificadores
    Parênteses não viram nó: o agrupamento já está na forma da árvore
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokens import Token


@dataclass(frozen=True)
class Integer:
    value: Token

    def label(self) -> str:
        return f"Inteiro({self.value.lexeme})"      # Lexema como veio: 007 não vira 7

    def children(self) -> tuple[Node, ...]:
        return ()

    def __str__(self) -> str:
        return self.label()


@dataclass(frozen=True)
class Variable:
    name: Token

    def label(self) -> str:
        return f"Variavel({self.name.lexeme})"

    def children(self) -> tuple[Node, ...]:
        return ()

    def __str__(self) -> str:
        return self.label()


@dataclass(frozen=True)
class Binary:
    operator: Token
    left: Expression
    right: Expression

    def label(self) -> str:
        return f"Binaria({self.operator.lexeme})"

    def children(self) -> tuple[Node, ...]:
        return (self.left, self.right)

    def __str__(self) -> str:
        return f"Binaria({self.operator.lexeme}, {self.left}, {self.right})"


@dataclass(frozen=True)
class Declaration:
    name: Token

    def label(self) -> str:
        return f"Declaracao({self.name.lexeme})"

    def children(self) -> tuple[Node, ...]:
        return ()

    def __str__(self) -> str:
        return self.label()


@dataclass(frozen=True)
class Assignment:
    name: Token
    value: Expression

    def label(self) -> str:
        return f"Atribuicao({self.name.lexeme})"

    def children(self) -> tuple[Node, ...]:
        return (self.value,)

    def __str__(self) -> str:
        return f"Atribuicao({self.name.lexeme}, {self.value})"


@dataclass(frozen=True)
class Output:
    value: Expression

    def label(self) -> str:
        return "Saida"

    def children(self) -> tuple[Node, ...]:
        return (self.value,)

    def __str__(self) -> str:
        return f"Saida({self.value})"


@dataclass(frozen=True)
class Program:
    items: tuple[Item, ...]

    def label(self) -> str:
        return "Programa"

    def children(self) -> tuple[Node, ...]:
        return self.items

    def __str__(self) -> str:
        return f"Programa([{', '.join(str(item) for item in self.items)}])"


Expression = Integer | Variable | Binary
Item = Declaration | Assignment | Output
Node = Program | Item | Expression


def format_tree(node: Node) -> str:
    lines = [node.label()]

    def walk(parent: Node, prefix: str) -> None:
        children = parent.children()
        for index, child in enumerate(children):
            last = index == len(children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.label())
            walk(child, prefix + ("    " if last else "│   "))

    walk(node, "")
    return "\n".join(lines)