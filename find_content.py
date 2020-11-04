import sys
import os
import chardet


def smart_open(path, mode):
    with open(path, "rb") as rbf:
        encoding = chardet.detect(rbf.read(1024))["encoding"]
    return open(path, mode, encoding=encoding)


def search_file(file_path, str_to_find):
    try:
        with smart_open(file_path, "r") as f:
            if str_to_find in f.read():
                return True
    except:
        pass
    return False


def traverse(find_path, str_to_find):
    counter = 0
    for root, dirs, files in os.walk(find_path):
        for i in files:
            file_path = os.path.join(root, i)
            if search_file(file_path, str_to_find):
                counter += 1
                print(file_path)
    return counter


if __name__ == "__main__":
    print("find file with content \"", sys.argv[1], "\"", sep="")
    print()
    n = traverse(".", sys.argv[1])
    print()
    print("found", n, "files")
