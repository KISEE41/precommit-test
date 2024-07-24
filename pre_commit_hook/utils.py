from __future__ import annotations

import fileinput
import glob
import importlib
import itertools
import os
import pathlib
import re

import nbformat
import pandas as pd


def read_files(path: str) -> list[str]:
    filepath = pathlib.Path(path)
    status = os.path.isfile(filepath)
    if status and filepath.suffix == ".py":
        with open(path) as file:
            lines = file.read()
    else:
        raise FileNotFoundError(f"{path} not found")

    return lines.split("\n")


def read_notebook(path: str):
    filepath = pathlib.Path(path)
    status = os.path.isfile(filepath)
    if status and filepath.suffix == ".ipynb":
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    else:
        raise FileNotFoundError(f"{path} not found")
    return nb


def find_leading_spaces(some_string):
    return sum(1 for _ in itertools.takewhile(str.isspace, some_string))


def give_identation(some_string):
    return re.sub("^", " " * 4, some_string, flags=re.MULTILINE)


def reformat(ans):
    new_ans = dict()
    string = "\n"
    for key, value in ans.items():
        val = [f"{i}{string}" for i in value]
        values = "".join(val)
        new_ans[key] = values
    data = fix_identation(new_ans)
    return data


def fix_identation(new_ans):

    data = {}
    for key, value in new_ans.items():
        leading_space = find_leading_spaces(value)
        if leading_space == 0:
            val = give_identation(value)
            data[key] = val
        else:
            data[key] = value
    return data


def write_file_tag_and_code(nb_tag_and_code):
    if not nb_tag_and_code:
        return {"msg": "Empty File submitted", "status": False, "data": None}
    try:
        path = "outputs/student_soln.py"
        for line in fileinput.input(path, inplace=True):
            line = line.rstrip()
            if not line:
                continue
            for f_key, f_value in nb_tag_and_code.items():
                if f_key in line:
                    line = line.replace(f_key, f_value)
            # print(line) writes the code in inlinecode.py file
            # donot comment or remove following print statement
            print(line)
    except Exception:
        return {
            "msg": "Could not write Student answer",
            "status": False,
            "data": None,
        }
    return {"msg": "Success", "status": True, "data": None}


def cal_marks_inline(path):
    # inlinecode_marks: list = []
    inlinecode_marks = None
    try:
        inline = importlib.import_module(path)
        marks_obj = inline.Grader()
        inlinecode_marks = marks_obj()
        inlinecode_marks = calculate_total_obtained(inlinecode_marks)
    except Exception as e:
        print("Exception on importing file", str(e))
        return inlinecode_marks
    return inlinecode_marks


def calculate_total_obtained(marks):
    """Aggregate the marks of different testcase"""
    df = pd.DataFrame(marks)
    aggeregate_marks = df.groupby(["taskId"]).sum().reset_index(level=0)
    return aggeregate_marks.to_dict(orient="records")


def find_ipynb_files() -> list:
    """
    Find all the ipynb files that exists inside resources folder.

    Parameters:
    ------
    None

    Returns:
    -----
    (list): list consisting of the pathlike string
    """
    # using glob finding all ipynb files inside resources folder
    ipynb_files = glob.glob("resources/**/*.ipynb", recursive=True)

    # returning the array
    return ipynb_files
