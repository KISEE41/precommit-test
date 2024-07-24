from __future__ import annotations

from nbformat.notebooknode import NotebookNode


class NotebookExecutionFailed(Exception):
    pass


class CellCheck:
    """
    Class to check each cell for particulat this.
    For now, checking for error is only implemented.
    """

    def preprocess(self, nb: NotebookNode) -> bool:
        """
        Process each cell to check whether the execution of shell
        encounter some error.

        Parameters
        ----------
        nb : NotebookNode
            Notebook being converted

        Return
        ---------
        None

        """
        # itterating over the notebook cells
        for index, cell in enumerate(nb.cells):
            # the output is only present only if the cell is of code type
            if cell["cell_type"] == "code" and cell["outputs"]:
                # check for the error
                self.preprocess_cell(index, cell)
        else:
            return

    def preprocess_cell(self, index, cell) -> None:
        """
        checking each cell if it encounter some error; if it encounter with
        an error, raise an exception.

        Parameters
        ----------
        cell : NotebookNode cell
            Notebook cell being processed
        index : int
            Index of the cell being processed

        Return
        ---------
        None
        """
        # if the cell ouput type is error raise exeception
        # along with the type of exception
        if cell.outputs[0]["output_type"] == "error":
            raise NotebookExecutionFailed(
                {
                    f"""Error at cell {cell["execution_count"]} -
                    {cell.outputs[0]["ename"]}:{cell.outputs[0]["evalue"]}""",
                },
            )
