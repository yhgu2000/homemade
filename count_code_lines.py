import os
import re
from typing import Optional

import chardet

includes = [
    r"^.*\.py$",
    r"^.*\.(?:js|jsx|ts|tsx)$",
]

excludes = [
    r"^.*\.idea.*$",
    r"^.*\.vs.*$",
    r"^.*\.vscode.*$",
    r"^.*venv.*$",
    r"^.*node_modules.*$",
    r"^.*build.*$"
]


def open_smartly(file, *args, **kwargs):
    with open(file, "rb") as rbf:
        encoding = chardet.detect(rbf.read(1024))["encoding"]
    return open(file, *args, encoding=encoding, **kwargs)


includes = [re.compile(i) for i in includes]
excludes = [re.compile(i) for i in excludes]


def match_and_count(file: str, allow_empty=False) -> Optional[int]:
    def func0(x: str):
        return 1

    def func1(x: str):
        return 1 if x.strip() != "" else 0

    func = func1 if allow_empty else func0
    try:
        for pattern in includes:
            if pattern.match(file):
                if any(map(lambda x: x.match(file), excludes)):
                    return
                with open_smartly(file) as f:
                    return sum(map(func, f))
    except BaseException:
        pass
    return


counter = 0
for root, dirs, files in os.walk("."):
    for file in files:
        full_path = os.path.join(root, file)
        line_nums = match_and_count(full_path)
        if line_nums:
            print("[{}]\t{}".format(line_nums, full_path))
            counter += line_nums

print()
print("total: ", counter)
