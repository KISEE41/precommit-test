from __future__ import annotations

import re

from nbconvert.exporters.exporter import ResourcesDict
from nbformat.notebooknode import NotebookNode
from nbgrader import utils
from nbgrader.preprocessors import NbGraderPreprocessor


class GetAutoGrades(NbGraderPreprocessor):
    def preprocess(
        self,
        nb: NotebookNode,
        resources: ResourcesDict,
    ) -> tuple[NotebookNode, ResourcesDict]:
        nb, resources = super().preprocess(nb, resources)

        return nb, resources

    def _add_score(self, cell: NotebookNode, resources: ResourcesDict) -> None:
        auto_score, _ = utils.determine_grade(cell, self.log)
        if auto_score is None:
            auto_score = 0
        try:
            tags = cell["metadata"]["tags"]
        except KeyError:
            tags = []
        # Choose the task id from the collection of tags
        # ['Ex-1-Task-1', 'traing block', 'tag1', 'tag2'] -> ['Ex-1-Task-1']
        task_name = re.compile(r"(Ex-\d+-Task-\d+)")
        task_id = [tag for tag in tags if task_name.match(tag)]
        if len(task_id) == 0:
            task_id = "No task id found"
        if len(task_id) == 1:
            task_id = task_id[0]

        manually_graded = utils.is_grade(cell) and utils.is_solution(cell)

        resources["scores"].append(
            {
                "taskId": task_id,
                "total": cell["metadata"]["nbgrader"].get("points", 0),
                "obtainedMarks": auto_score,
                "manuallyGraded": manually_graded,
            },
        )
        resources["total_obtained"] += auto_score
        resources["total_marks"] += cell["metadata"]["nbgrader"].get(
            "points",
            0,
        )

    def _add_comment(
        self,
        cell: NotebookNode,
        resources: ResourcesDict,
    ) -> None:
        if cell.metadata.nbgrader.get(
            "checksum",
            None,
        ) == utils.compute_checksum(
            cell,
        ) and not utils.is_task(cell):
            pass
            # self.log("No Response")

    def preprocess_cell(
        self,
        cell: NotebookNode,
        resources: ResourcesDict,
        cell_index: int,
    ) -> tuple[NotebookNode, ResourcesDict]:
        if utils.is_grade(cell):
            self._add_score(cell, resources)

        if utils.is_solution(cell):
            self._add_comment(cell, resources)

        if utils.is_task(cell):
            self._add_comment(cell, resources)

        return cell, resources
