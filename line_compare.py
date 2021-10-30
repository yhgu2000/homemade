import sys
import os
import chardet


def detect_encoding(file_path: str):
    """判断给定路径文件的编码
    """
    with open(file_path, "rb") as f:
        return chardet.detect(f.read(1024))["encoding"]
    return


def main():
    line_number = 0
    differences = 0
    f1_path = sys.argv[1]
    f2_path = sys.argv[2]
    f1 = open(f1_path, encoding=detect_encoding(f1_path))
    f2 = open(f2_path, encoding=detect_encoding(f2_path))
    for line1, line2 in zip(f1, f2):
        line1 = line1.strip()
        line2 = line2.strip()
        line_number += 1
        if(line1 != line2):
            differences += 1
            print(line_number, ':')
            print("->", line1)
            print("->", line2)
    f1.close()
    f2.close()
    print("found", differences, "difference(s)")
    return


if __name__ == "__main__":
    main()
