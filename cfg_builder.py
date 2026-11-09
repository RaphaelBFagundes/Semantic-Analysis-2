"""Construa um CFG auxiliar por função, preservando os nós da AST."""

from __future__ import annotations

import load_previous  # Disponibiliza os módulos das etapas anteriores.

from ast_nodes import (
    Assignment, Block, BoolLiteral, CallStmt, FunctionDecl,
    IfStmt, PrintStmt, ReturnStmt, Stmt, VarDecl, WhileStmt
)
from cfg import BlockId, Branch, CFG, Jump, Return, ScopeExit


class CFGBuilder:
    def build(self, function: FunctionDecl) -> CFG:
        self.cfg = CFG(function)
        body_entry = self.cfg.new_block()
        self.cfg.terminate(self.cfg.entry, Jump(body_entry.id))
        continuation = self._build_block(function.body, body_entry.id)
        if continuation is not None:
            self.cfg.terminate(continuation, Jump(self.cfg.fallthrough_exit))
        return self.cfg

    def _build_block(self, block: Block, current: BlockId) -> BlockId | None:
        """Percorra um bloco da AST e devolva sua continuação normal.

        `current` identifica um bloco básico aberto. Comandos sequenciais
        permanecem nele. Comandos de controle podem mudar a continuação.
        None indica que os caminhos deste bloco não alcançam o próximo comando.
        """
        curr: BlockId | None = current
        for statement in block.statements:
            if curr is None:
                # Comandos após um retorno ou caminho encerrado não prolongam o caminho
                break
            curr = self._build_statement(statement, curr)

        if curr is not None:
            # Ao sair normalmente do bloco, adiciona a marca ScopeExit
            scope = block.metadata.get("scope")
            if scope is not None:
                self.cfg.blocks[curr].operations.append(ScopeExit(scope))

        return curr

    def _build_statement(self, statement: Stmt, current: BlockId) -> BlockId | None:
        """Incorpore um comando ao CFG e devolva sua continuação normal."""
        if isinstance(statement, (VarDecl, Assignment, PrintStmt, CallStmt)):
            self.cfg.blocks[current].operations.append(statement)
            return current
        elif isinstance(statement, Block):
            return self._build_block(statement, current)
        elif isinstance(statement, IfStmt):
            return self._build_if(statement, current)
        elif isinstance(statement, WhileStmt):
            return self._build_while(statement, current)
        elif isinstance(statement, ReturnStmt):
            self.cfg.terminate(current, Return(statement))
            return None
        else:
            raise TypeError(f"comando inesperado na AST: {type(statement).__name__}")

    def _build_if(self, statement: IfStmt, current: BlockId) -> BlockId | None:
        """Construa o fluxo da condicional e devolva sua continuação."""
        then_entry = self.cfg.new_block()
        else_entry = self.cfg.new_block()

        self.cfg.terminate(
            current,
            Branch(
                condition=statement.condition,
                true_target=then_entry.id,
                false_target=else_entry.id,
            ),
        )

        then_exit = self._build_block(statement.then_block, then_entry.id)

        if statement.else_block is not None:
            else_exit = self._build_block(statement.else_block, else_entry.id)
        else:
            else_exit = else_entry.id

        # Se nenhum dos ramos continua, a condicional não tem continuação normal
        if then_exit is None and else_exit is None:
            return None

        join_block = self.cfg.new_block()
        if then_exit is not None:
            self.cfg.terminate(then_exit, Jump(join_block.id))
        if else_exit is not None:
            self.cfg.terminate(else_exit, Jump(join_block.id))

        return join_block.id

    def _build_while(self, statement: WhileStmt, current: BlockId) -> BlockId | None:
        """Construa o fluxo do laço e devolva sua continuação."""
        header = self.cfg.new_block()
        self.cfg.terminate(current, Jump(header.id))

        is_while_true = isinstance(statement.condition, BoolLiteral) and statement.condition.value is True

        body_entry = self.cfg.new_block()
        exit_block = self.cfg.new_block()

        self.cfg.terminate(
            header.id,
            Branch(
                condition=statement.condition,
                true_target=body_entry.id,
                false_target=exit_block.id,
            ),
        )

        body_exit = self._build_block(statement.body, body_entry.id)
        if body_exit is not None:
            self.cfg.terminate(body_exit, Jump(header.id))

        if is_while_true:
            # while (true) não possui saída normal
            return None

        return exit_block.id
