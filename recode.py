################################################################################
#
# 版权所有 (c) 2019-2020 顾宇浩。保留所有权利。
#
# 文件: recode.py
# 说明：文本文件编码处理脚本
# 版本: v2.2 (2020-5-15)
#
################################################################################

import parser_framework as parf
import os
import sys
import chardet
import codecs

path = "."  # 全局操作路径/文件
detect_size = 1024  # 文件检查的读取大小
from_encoding = {"GB2312", "UTF-8-SIG"}  # 源编码集
to_encoding = "UTF-8"  # 目标编码
recursive_flag = False  # 递归标志


#
def info():
    """输出脚本信息
    """
    print("""recode.py v2.1
Copyright (c) 2019-2020 by Yuhao Gu. All rights reserved.
For help, use option "-h".
""")
    return


def detect_encoding(file_path: str):
    """判断指定路径文件的编码
    """
    with open(file_path, "rb") as f:
        return chardet.detect(f.read(detect_size))["encoding"]
    return


def recode_file(file_path: str, from_encoding: str, to_encoding: str):
    """按照给定源编码和目标编码重新编码文件
    """
    with open(file_path, "r", encoding=from_encoding) as f:
        content = f.read()
    with open(file_path, "w", encoding=to_encoding) as f:
        f.write(content)
    return


def add_counter(counter: dict, key):
    """计数器加1
    """
    try:
        counter[key] += 1
    except KeyError:
        counter[key] = 1
    return


def check_path(path: str):
    return os.path.isdir(path) or os.path.isfile(path)


class MainOption(parf.Option):
    """主选项
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        global path
        if len(args) >= 2:
            raise parf.UnexpectedArgument(args[2])
        elif len(args) == 1:
            path = args[0]
            if (not check_path(path)):
                raise parf.InvalidArgument("invalid path: \"" + path + "\"")
        return

    def execute(self, args):
        return


main_option = MainOption(0)


class ListOption(parf.Option):
    """-l 选项

    如果是文件，列出该文件的编码；
    如果是目录，列出目录下所有文件的编码。
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        global path
        if len(args) == 0:
            return
        if len(args) == 1:
            path = args[0]
            if (not check_path(path)):
                raise parf.InvalidArgument("invalid path: \"" + path + "\"")
            return
        raise parf.UnexpectedArgument(args[1])
        return

    def execute(self, args):
        global path
        global detect_size
        global from_encoding
        global to_encoding
        global option_map
        # 如果目标是文件
        if os.path.isfile(path):
            try:
                print(detect_encoding(path), '-', path)
            except Exception as e:
                print(e)
        # 如果目标是目录
        else:
            counter = {"SKIPPED": 0}
            # 如果要求递归
            if recursive_flag:
                for root, dirs, files in os.walk(path):
                    for i in files:
                        try:
                            my_path = os.path.join(root, i)
                            encoding = detect_encoding(my_path)
                            print("[", encoding, "] ", my_path, sep="")
                            add_counter(counter, encoding)
                        except:
                            print("<SKIPPED>", my_path)
                            add_counter(counter, "SKIPPED")
            # 否则只遍历当前文件夹
            else:
                for i in os.listdir(path):
                    my_path = os.path.join(path, i)
                    if os.path.isfile(my_path):
                        try:
                            encoding = detect_encoding(my_path)
                            print("[", encoding, "] ", my_path, sep="")
                            add_counter(counter, encoding)
                        except:
                            print("<SKIPPED>", my_path)
                            add_counter(counter, "SKIPPED")
            print()
            print("Total:")
            if counter["SKIPPED"] != 0:
                print("%16s" % "SKIPPED", '=', counter["SKIPPED"])
            counter.pop("SKIPPED")
            for key, value in counter.items():
                print("%16s" % key, '=', value)
        return


list_option = ListOption(1)


class AutoOption(parf.Option):
    """-a 选项

    判断文件是否符合转换编码，如果是，则转换到目标编码。

    如果是文件，则转换该文件；
    如果是目录，则转换目录下的所有可识别编码文件。
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        global path
        if len(args) == 0:
            return
        if len(args) == 1:
            path = args[0]
            if (not check_path(path)):
                raise parf.InvalidArgument("invalid path: \"" + path + "\"")
            return
        raise parf.UnexpectedArgument(args[1])
        return

    def execute(self, args):
        global path
        global detect_size
        global to_encoding
        global option_map
        global from_encoding
        # 如果目标是文件
        if os.path.isfile(path):
            try:
                encoding = detect_encoding(path)
                if encoding in from_encoding:
                    recode_file(path, encoding, to_encoding)
                    print(encoding, "->", to_encoding, '-', path)
                else:
                    print("encoding \"",
                          encoding,
                          "\" is not in from encodings",
                          sep="")
                    print("nothing to do.")
            except Exception as e:
                print(e)
        # 如果目标是目录
        else:
            counter = {"SKIPPED": 0}
            # 如果要求递归
            if recursive_flag:
                for root, dirs, files in os.walk(path):
                    for i in files:
                        try:
                            my_path = os.path.join(root, i)
                            encoding = detect_encoding(my_path)
                            if encoding in from_encoding:
                                recode_file(my_path, encoding, to_encoding)
                                print(encoding, "->", to_encoding, '-',
                                      my_path)
                                add_counter(counter, encoding)
                        except:
                            print("[SKIPPED]", my_path)
                            add_counter(counter, "SKIPPED")
            # 否则只处理目标目录
            else:
                for i in os.listdir(path):
                    my_path = os.path.join(path, i)
                    if os.path.isfile(my_path):
                        try:
                            encoding = detect_encoding(my_path)
                            if encoding in from_encoding:
                                recode_file(my_path, encoding, to_encoding)
                                print(encoding, "->", to_encoding, '-',
                                      my_path)
                                add_counter(counter, encoding)
                        except:
                            print("[SKIPPED]", my_path)
                            add_counter(counter, "SKIPPED")
            print()
            print("Recode to:", to_encoding)
            print("Total:")
            if counter["SKIPPED"] != 0:
                print("%16s" % "SKIPPED", '=', counter["SKIPPED"])
            counter.pop("SKIPPED")
            for key, value in counter.items():
                print("%16s" % key, '=', value)
        return


auto_option = AutoOption(2)


class RecursiveOption(parf.Option):
    """-r 选项
    
    开启递归
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def execute(self, args):
        global recursive_flag
        recursive_flag = True
        return


recursive_option = RecursiveOption(0)


class FromOption(parf.Option):
    """-f 选项
    
    指定初始编码
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        if len(args) < 1:
            raise parf.MissingArgument("-f")
        return

    def execute(self, args):
        global from_encoding
        from_encoding = set(args)
        return


from_option = FromOption(0)


class ToOption(parf.Option):
    """-t 选项

    设定目标编码
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        if len(args) < 1:
            raise parf.MissingArgument("-t")
        elif len(args) > 1:
            raise parf.UnexpectedArgument(args[1])
        return

    def execute(self, args):
        global to_encoding
        to_encoding = args[0]
        return


to_option = ToOption(0)


class DetectSizeOption(parf.Option):
    """-ds 选项

    设定文件采样大小
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def check(self, args):
        if len(args) > 1:
            raise parf.UnexpectedArgument(args[1])
        if (len(args) < 1) or (not args[0].isnumeric()):
            raise parf.InvalidArgument("-ds option needs an integer.")
        return

    def execute(self, args):
        global detect_size
        detect_size = int(args[0])
        return


detect_size_option = DetectSizeOption(0)


class HelpOption(parf.Option):
    """-h 选项

    输出帮助信息
    """
    def __init__(self, priority):
        return super().__init__(priority)

    def execute(self, args):
        print("""Help for recode.py

A script tool for text file encoding.

Options:
    -       set path.
    -h      show help.
    -f      set from encoding.
    -t      set target encoding.
    -r      recursive mode.
    -ds     set detective size, default: 1024(Byte).
    -l      list encoding of a file or files in a folder.
    -a      auto detect encoding and recode to target encoding.
""")
        return


help_option = HelpOption(-1)


class DefaultOption(parf.Option):
    """默认执行选项

    将文件从from_encoding重新编码到to_encoding
    """
    def __init__(self):
        return super().__init__(1)

    def execute(self, args):
        global from_encoding
        if len(from_encoding) != 1:
            raise parf.InvalidArgument("-f <encoding>")
        for encoding in from_encoding:
            recode_file(path, encoding, to_encoding)
        return


default_option = DefaultOption()


def main():
    option_map = {
        "-": main_option,
        "-h": help_option,
        "-f": from_option,
        "-t": to_option,
        "-r": recursive_option,
        "-ds": detect_size_option,
        "-l": list_option,
        "-a": auto_option
    }
    p = parf.Parser(option_map, default_option, info)
    parf.auto_process(p, sys.argv)
    return


if __name__ == "__main__":
    main()
