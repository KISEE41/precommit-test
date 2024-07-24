from __future__ import annotations

from nbconvert.exporters.exporter import ResourcesDict


class ScoreNotMatch(Exception):
    pass


class CheckPoint:
    """
    Check whether the points assigned to the exercise matches the
    obtained point.

    [Note: only for the instructor file (the grader must grade full marks
    to grader/instructor file, otherwise it means there are some issues with
    the file.)]
    """

    def preprocess(self, resources: ResourcesDict) -> bool:
        """
        Process each cell to check whether the execution of shell
        encounter some error.

        Parameters
        ----------
        resources : ResourcesDict
            resources that consists of metadata like scores

        Return
        ---------
        bool

        """
        # check if the total obtained points matches the total points of assignment
        if resources["total_obtained"] != resources["total_marks"]:
            # check in which exerice there is an issue
            for ex in resources["scores"]:
                self.preprocess_cell()

        return

    def preprocess_cell(self, ex: dict) -> None:
        """
        check in which exericise there is an issue

        Parameters
        ----------
        ex : dict
            metadata of each exercise

        Return
        ---------
        None
        """
        if ex["total"] != ex["obtainedMarks"]:
            raise ScoreNotMatch(
                f"Score doesnot match. There might be some issue in exercise {ex["taskId"]}",
            )
