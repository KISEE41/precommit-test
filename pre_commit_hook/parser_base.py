from __future__ import annotations

import re
from abc import ABC, abstractmethod

from loguru import logger

TASK_STUB = r"\s*?#{1,3} (Ex-\d+-Task-\d+)"
BEGIN_SOLUTION_DELIMETER = r"# BEGIN SOLUTION"
END_SOLUTION_DELIMETER = r"# END SOLUTION"
STUB_LINES = "# Your Code Here".split("\n")
NO_SOLUTION_FOUND = "# No solution found"


class Parser(ABC):
    task_id_delimeter = TASK_STUB
    begin_solution_delimeter = BEGIN_SOLUTION_DELIMETER
    end_solution_delimeter = END_SOLUTION_DELIMETER
    stub_lines = STUB_LINES
    no_solution_found = NO_SOLUTION_FOUND

    def _extract_solution(self, lines) -> dict[str, list]:
        """Extract the solution blocks from soltion blocks

        Parameters
        ----------
        path : str
            path to the python file

        Returns
        -------
        submissions: dict
            A dictionary containing the exercise  name as key  and the
            solution line(s) in list as the value

        Raise
        -----
        RuntimeError

        """
        new_lines = []
        submissions: dict = dict()
        in_solution = False
        task_id = None

        for line in lines:
            match = re.match(self.task_id_delimeter, line)
            if match:
                task_id = match.group(1)
                submissions[task_id] = []

            if self.begin_solution_delimeter in line:
                if task_id is None:
                    raise RuntimeError("No tasks associated")

                if in_solution:
                    raise RuntimeError(
                        f"Encountered nested {self.begin_solution_delimeter}",
                    )

                in_solution = True
            elif self.end_solution_delimeter in line:
                in_solution = False
                task_id = None
                new_lines.append(line)
            elif not in_solution:
                new_lines.append(line)
            elif in_solution:
                match = re.match(r"(\s*)(.*)", line)
                if match:
                    code_line = line
                    # indent = match.group(1)
                    logger.debug(code_line)
                submissions[task_id].append(code_line)

        if in_solution:
            raise RuntimeError(f"No {self.end_solution_delimeter} found")

        return submissions

    def _inject_solution(self, lines, solutions: dict):
        """Inserts the solution block based on the task_id delimeter

        Parameters
        ----------
        lines : TODO
        solutions : TODO

        Returns
        -------
        TODO

        """
        new_lines = []
        in_solution = False
        task_id: str | None = None

        for line in lines:
            # begin the solution area
            match = re.match(self.task_id_delimeter, line)
            if match:
                task_id = match.group(1)

            if self.begin_solution_delimeter in line:
                # Check if it has any task associated with it
                if not task_id:
                    raise RuntimeError("Task not associated")
                # check to maktask_id sure this isn't a nested BEGIN
                # SOLUTION region
                if in_solution:
                    raise RuntimeError(
                        "encountered nested begin solution statements",
                    )

                in_solution = True

                # replace it with the stub, indented as necessary
                match = re.match(r"\s*", line)
                # indent = ""
                # if match:
                #     indent = match.group(0)
                submission_lines = solutions.get(
                    task_id,
                    [self.no_solution_found],
                )
                logger.debug(submission_lines)
                new_lines.append(line)
                for stub_line in submission_lines:
                    new_lines.append(stub_line)

            # end the solution area
            elif self.end_solution_delimeter in line:
                in_solution = False
                task_id = None
                new_lines.append(line)

            # add lines as long as it's not in the solution area
            elif not in_solution:
                new_lines.append(line)

        # we finished going through all the lines, but didn't find a
        # matching END SOLUTION statment
        if in_solution:
            raise RuntimeError("no end solution statement found")

        return "\n".join(new_lines)

    def _check_tags(self, tags: list) -> str:
        if "Testing-Cell" in tags:
            for tag in tags:
                match = re.match(
                    r"\s*?#{1,3} (Ex-\d+-Task-\d+)",
                    " ".join(["###", tag]),
                )
                if match:
                    return match.group(1)
            else:
                raise RuntimeError(
                    "Check tags in the cell. Error in testing cell.",
                )

    def _inject_cell(self, cell, tests: dict):
        """Inserts the solution block based on the task_id delimeter

        Parameters
        ----------
        lines : TODO
        solutions : TODO

        Returns
        -------
        TODO

        """
        task_id: str | None = None

        # begin the solution area
        task_id = self._check_tags(tags=cell.metadata["tags"])

        if task_id:
            return tests.get(task_id)

        else:
            raise RuntimeError("Task not associated")

    def _extract_cell(self, cell):
        """Extract the solution of the blocks from solution blocks

        Parameters
        ----------
        cell : nb.cell
            path to the python file

        Returns
        -------
        submissions: dict
            A dictionary containing the exercise  name as key  and the
            solution line(s) in list as the value

        Raise
        -----
        RuntimeError

        """
        assertion_tests: dict = dict()
        task_id = None

        # Extract the task_id of the task
        # task_id is extracted from the nb metadat that nbgrader provide
        # i,e. in the tags metadata
        # logger.debug(cell)
        if cell.metadata.get("tags"):
            match = re.match(
                self.task_id_delimeter,
                " ".join(["###", cell.metadata["tags"][0]]),
            )
            if match:
                task_id = match.group(1)
                assertion_tests[task_id] = ""

            assertion_tests[task_id] = cell.get("source")

            logger.debug(assertion_tests)

        else:
            raise RuntimeError("No task_id associated")

        return assertion_tests

    @abstractmethod
    def _read_file(self, path_to_file: str):
        raise NotImplementedError("_read_file not implemented")

    @abstractmethod
    def extract_solutions(
        self,
        path_to_file,
    ) -> dict[str, list]:
        """Finds the relevant locations for the cell blokcs

        Returns
        -------
        submissions: dict
            Returns the exercise and key value pair
        """
        raise NotImplementedError("extract_solutions not implemented")

    @abstractmethod
    def inject_solution(self, grader_file, solutions: dict):
        raise NotImplementedError("Function not implemented")
