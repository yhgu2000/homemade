"""行尾格式化器
"""

import sys
import os

if len(sys.argv) < 2:
    top = "."
else:
    top = sys.argv[1]

for root, dirs, files in os.walk(top):
    for file in files:
        path = os.path.join(root, file)

        try:
            content = open(path, "r", encoding="utf-8").read()
        except BaseException:
            print("[SKIPPED]", path)
            continue

        open(path, "w", newline="\n", encoding="utf-8").write(content)
        print(path)

input("DONE")
