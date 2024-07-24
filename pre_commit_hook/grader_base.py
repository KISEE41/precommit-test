from __future__ import annotations

from pathlib import Path

from loguru import logger
from nbconvert.exporters.exporter import ResourcesDict
from nbgrader.preprocessors import ClearOutput, Execute

from .autogrades import GetAutoGrades
from .cell_check import CellCheck
from .check_points import CheckPoint
from .utils import read_notebook

# from nbconvert.exporters.exporter import ResourcesDict


class Grader:
    def check_instructor_file(self, instructor_file: str):
        # read notebook
        nb = read_notebook(instructor_file)
        logger.debug("Reading Notobook - completed")

        # # notebook read is in the form of json format
        # logger.debug(nb)

        resources = ResourcesDict(
            None,
            {
                "scores": [],
                "total_obtained": 0,
                "total_marks": 0,
                "metadata": {"path": str(Path(instructor_file).parents[0])},
            },
        )

        # Clear Solutions
        nb, resources = ClearOutput().preprocess(nb=nb, resources=resources)

        # Execute notebook
        nb, resources = Execute().preprocess(nb=nb, resources=resources)
        logger.debug("Execution of the file completed")
        # logger.debug(nb)

        # Checking if there is any error in the notebook
        _ = CellCheck().preprocess(nb=nb)
        logger.debug("No errors in the execution of notebook")

        # Autogrades the notebook
        nb, resources = GetAutoGrades().preprocess(nb=nb, resources=resources)
        logger.debug("Autograde completed successfully")
        logger.debug(resources)

        # check the assignment if there are some issues
        # the grader must give full score for instructor file
        # checking if the grader has does so
        _ = CheckPoint().preprocess(resources=resources)
        logger.debug("Score match as it should be.")

        # returning the notebook and the resources consisting of metadata
        return nb, dict(resources)
