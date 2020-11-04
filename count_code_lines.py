import sys
import os
import chardet


def smart_open(path, mode):
    with open(path, "rb") as rbf:
        encoding = chardet.detect(rbf.read(1024))["encoding"]
    return open(path, mode, encoding=encoding)


counter = 0

for root, dirs, files in os.walk("."):
    for i in files:
        if not i.endswith(".py"):
            continue
        sub_counter = 0
        try:
            with smart_open(os.path.join(root, i), "r") as f:
                for j in f:
                    sub_counter += 1
            print(i, sub_counter)
        except:
            sub_counter = 0
        counter += sub_counter

print()
print("total: ", counter)
