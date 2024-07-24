from __future__ import annotations

from loguru import logger

from .parser_base import Parser
from .utils import read_files


class PythonParser(Parser):
    def _read_file(self, path_to_file):
        return read_files(path_to_file)

    def extract_solutions(self, path_to_file):
        contents = self._read_file(path_to_file)
        submissions = self._extract_solution(contents)
        return submissions

    def inject_solution(self, path_to_file, solutions):
        contents = self._read_file(path_to_file)
        return self._inject_solution(contents, solutions)


if __name__ == "__main__":
    grader_file = "resources/assignment_v2.py"
    submission_file = "resources/assignment_v2_original.py"
    parser = PythonParser()
    solutions = parser.extract_solutions(grader_file)
    logger.info(solutions)
    contents = parser.inject_solution(submission_file, solutions)
    logger.info("Injected Contents")
    logger.info(contents)
    logger.info("Grader contents")
    logger.info(parser._read_file(grader_file))
