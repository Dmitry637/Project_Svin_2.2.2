from __future__ import annotations

import argparse
import sys

from src.config import ConfigError, load_config
from src.maven import Dependency, DependencyResolutionError, MavenRepository


EXIT_SUCCESS = 0
EXIT_DEPENDENCY_ERROR = 1
EXIT_CONFIG_ERROR = 2
EXIT_INTERRUPTED = 130


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Вариант №7, этап 2: получение и вывод прямых зависимостей "
            "Maven-пакета заданной версии."
        )
    )
    parser.add_argument(
        "--config",
        default="config.ini",
        metavar="FILE",
        help="путь к INI-файлу (по умолчанию: config.ini)",
    )
    return parser


def _print_dependencies(dependencies: list[Dependency]) -> None:
    print("Прямые зависимости Maven:")

    if not dependencies:
        print("Прямые зависимости не объявлены.")
        return

    for dependency in dependencies:
        details = [f"scope={dependency.scope}"]
        if dependency.optional:
            details.append("optional=true")
        print(f"- {dependency.coordinates} [{', '.join(details)}]")


def _print_error(message: str) -> None:
    print(message, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = load_config(args.config)
        dependencies = MavenRepository(config).direct_dependencies()
    except ConfigError as exc:
        _print_error(f"Ошибка конфигурации: {exc}")
        return EXIT_CONFIG_ERROR
    except DependencyResolutionError as exc:
        _print_error(f"Ошибка получения зависимостей: {exc}")
        return EXIT_DEPENDENCY_ERROR
    except KeyboardInterrupt:
        _print_error("\nОперация отменена пользователем.")
        return EXIT_INTERRUPTED

    print(f"Пакет: {config.package_name}:{config.package_version}")
    _print_dependencies(dependencies)
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
