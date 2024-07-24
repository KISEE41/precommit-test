from __future__ import annotations

from loguru import logger

from .grader_base import Grader
from .utils import find_ipynb_files


def check_notebook() -> None:
    # finding all the ipynb files path
    files = find_ipynb_files()

    # intializing the grader
    grader = Grader()

    # looping over the files
    for file in files:
        # Extracting the filename
        filename = file.split("\\")[-1]

        # for now only applicable to instructor file
        # and the instuctor file consists of keyword 'Instructor' in filename
        if "Instructor" in filename:
            try:
                logger.info(f"Checking for file: {filename}")

                # check the file
                nb, resources = grader.check_instructor_file(
                    instructor_file=file,
                )

            # if there occurs some kind of exception
            except Exception as err:
                logger.exception(err)
