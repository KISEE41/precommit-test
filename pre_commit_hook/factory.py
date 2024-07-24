from __future__ import annotations

import pathlib

from loguru import logger

from .notebook_parser import NotebookParser
from .python_parser import PythonParser


class ParserFactory:
    PYTHON = ".py"
    NOTEBOOK = ".ipynb"

    def __call__(self, path: str):
        filepath = pathlib.Path(path)
        if filepath.suffix == self.PYTHON:
            logger.debug("Python Parser")
            return PythonParser()
        elif filepath.suffix == self.NOTEBOOK:
            logger.debug("Ipynb Parser")
            return NotebookParser()

        return None


if __name__ == "__main__":
    factory = ParserFactory()
    parser = factory("resources/assignment_v2.py")
    submissions = parser.extract_solutions()
    logger.info(submissions)
    parser_ipynb = factory("resources/assignment_v2.ipynb")
    submissions = parser_ipynb.extract_solutions()
    logger.info(submissions)
