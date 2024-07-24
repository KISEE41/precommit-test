from __future__ import annotations

from loguru import logger
from nbgrader import utils

from .parser_base import Parser
from .utils import read_notebook


class NotebookParser(Parser):
    def _read_file(self, path_to_file):
        return read_notebook(path_to_file)

    def _cells(self, nb):
        if nb.nbformat < 4:
            for ws in nb.worksheets:
                for cell in ws.cells:
                    yield cell
        else:
            for cell in nb.cells:
                if "execution_count" in cell:
                    cell["execution_count"] = None
                yield cell

    def extract_solutions(self, path_to_file) -> dict[str, list]:
        output = []
        nb = self._read_file(path_to_file)
        # logger.debug(nb)
        for cell in self._cells(nb):
            if cell["cell_type"] == "code" and utils.is_grade(cell):
                if "source" in cell:
                    # logger.debug(cell)
                    solution = self._extract_solution(cell)
                    if solution:
                        output.append(solution)
        output = {key: value for d in output for key, value in d.items()}
        return output

    def inject_solution(self, submission_file, solutions: dict):
        output = []
        nb = self._read_file(submission_file)
        for cell in self._cells(nb):
            if cell["cell_type"] == "code":
                logger.debug(cell["source"])

                if utils.is_grade(cell) and "source" in cell:
                    code = cell["source"]
                    code = code.split("\n")
                    injected_code = self._inject_solution(cell, solutions)
                    logger.debug(injected_code)
                    if injected_code:
                        cell["source"] = injected_code
                output.append(cell)
        nb["cells"] = output
        # logger.debug(nb)
        return nb
