from __future__ import annotations

import argparse
from pathlib import Path

from Lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic import SemanticAnalyzer
from semantic_errors import SemanticError


def main(argv: list[str] | None = None) -> int:
    argument_parser = argparse.ArgumentParser(
        description="Execute a Análise Semântica 1 da MicroC."
    )
    argument_parser.add_argument("source", type=Path, metavar="arquivo.mc")
    args = argument_parser.parse_args(argv)

    try:
        source = args.source.read_text(encoding="utf-8")
        program = Parser(Lexer(source).scan()).parse()
        SemanticAnalyzer().analyze(program)
    except (OSError, UnicodeError) as error:
        argument_parser.error(f"erro ao ler {str(args.source)!r}: {error}")
        return 2
    except (LexerError, ParserError, SemanticError) as error:
        argument_parser.exit(1, f"{error}\n")
        return 1
    except NotImplementedError as error:
        argument_parser.exit(3, f"scaffold incompleto: {error}\n")
        return 3

    print("programa válido na Análise Semântica 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
