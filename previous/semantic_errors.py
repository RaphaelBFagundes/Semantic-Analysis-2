"""Contrato fixo dos diagnósticos semânticos. Não altere este arquivo."""

from __future__ import annotations

import enum
from collections.abc import Iterable
from dataclasses import dataclass

from ast_nodes import SourceSpan


class SemanticErrorKind(enum.Enum):
    DUPLICATE_FUNCTION = "duplicate_function"
    DUPLICATE_DECLARATION = "duplicate_declaration"
    UNDECLARED_VARIABLE = "undeclared_variable"
    UNDECLARED_FUNCTION = "undeclared_function"
    INVALID_MAIN = "invalid_main"
    VOID_PARAMETER = "void_parameter"
    VOID_VARIABLE = "void_variable"
    INTEGER_LITERAL_OUT_OF_RANGE = "integer_literal_out_of_range"
    INVALID_UNARY_OPERAND = "invalid_unary_operand"
    INVALID_BINARY_OPERANDS = "invalid_binary_operands"
    INITIALIZER_TYPE_MISMATCH = "initializer_type_mismatch"
    ASSIGNMENT_TYPE_MISMATCH = "assignment_type_mismatch"
    CONDITION_TYPE_MISMATCH = "condition_type_mismatch"
    ARITY_MISMATCH = "arity_mismatch"
    ARGUMENT_TYPE_MISMATCH = "argument_type_mismatch"
    VOID_VALUE_USED = "void_value_used"
    RETURN_MISMATCH = "return_mismatch"


@dataclass(frozen=True, slots=True)
class SemanticDiagnostic:
    kind: SemanticErrorKind
    message: str
    span: SourceSpan

    @property
    def line(self) -> int:
        return self.span.start_line

    @property
    def column(self) -> int:
        return self.span.start_column

    def __str__(self) -> str:
        return (
            f"erro semântico [{self.kind.value}] em {self.line}:{self.column}: "
            f"{self.message}"
        )


class SemanticError(Exception):
    def __init__(self, diagnostics: Iterable[SemanticDiagnostic]):
        self.diagnostics = tuple(diagnostics)
        if not self.diagnostics:
            raise ValueError("SemanticError exige ao menos um diagnóstico")
        super().__init__(str(self))

    def __str__(self) -> str:
        return "\n".join(str(diagnostic) for diagnostic in self.diagnostics)
