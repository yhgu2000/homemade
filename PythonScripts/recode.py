################################################################################
#
# 版权所有 (c) 2019 顾宇浩。保留所有权利。
#
# 文件: recode.py
# 说明：文本文件编码处理脚本
# 版本: v1.1 (2019-12-16)
#
################################################################################
#
#
import parser_framework
import os
import sys
import chardet
import codecs

path = "."              # 全局操作路径/文件
detect_size = 1024      # 文件检查的读取大小
from_encoding = None    # 源编码集
to_encoding = "UTF-8"   # 目标编码
recursive_flag = False  # 递归标志
def detect_encoding(file_path:str):
    """判断给定路径文件的编码
    """
    if from_encoding is None:
        with open(file_path,"rb") as f:
            return chardet.detect(f.read(detect_size))["encoding"]
    else:
        return from_encoding
    return

def recode_file(file_path:str,from_encoding:str,to_encoding:str):
    """按照给定源编码和目标编码重新编码文件
    """
    with open(file_path,"r",encoding = from_encoding) as f:
        content = f.read()
    with open(file_path,"w",encoding = to_encoding) as f:
        f.write(content)
    return

def add_counter(counter:dict,key):
    """计数器加1
    """
    try:
        counter[key] += 1
    except KeyError:
        counter[key] = 1
    return

def zero_checker(zero_args):
    """零位参数检查
    """
    global path
    if len(zero_args) >= 3:
        raise parser_framework.UnexpectedArgument(zero_args[2])
    elif len(zero_args) == 2:
        path = zero_args[1]
        if (not os.path.isdir(path)) and (not os.path.isfile(path)):
            raise parser_framework.InvalidArgument("invalid path: \"" + path + "\"")
    return

def zero_executer(zero_args):
    """零位参数执行
    """
    return

def l_executer(args):
    """-l 选项执行

    如果是文件，列出该文件的编码；
    如果是目录，列出目录下所有文件的编码。
    """
    global path
    global detect_size
    global from_encoding
    global to_encoding
    global option_map
    # 如果目标是文件
    if os.path.isfile(path):
        try:
            print(detect_encoding(path),'-',path)
        except Exception as e:
            print(e)
    # 如果目标是目录
    else:
        counter = {"SKIPPED":0}
        # 如果要求递归
        if recursive_flag:
            for root,dirs,files in os.walk(path):
                for i in files:
                    try:
                        my_path = os.path.join(root,i)
                        encoding = detect_encoding(my_path)
                        print(encoding,'-',my_path)
                        add_counter(counter,encoding)
                    except:
                        print("[SKIPPED]",my_path)
                        add_counter(counter,"SKIPPED")
        # 否则只遍历当前文件夹
        else:
            for i in os.listdir(path):
                my_path = os.path.join(path,i)
                if os.path.isfile(my_path):
                    try:
                        encoding = detect_encoding(my_path)
                        print(encoding,'-',my_path)
                        add_counter(counter,encoding)
                    except:
                        print("[SKIPPED]",my_path)
                        add_counter(counter,"SKIPPED")
        print()
        print("Total:")
        if counter["SKIPPED"] != 0:
            print("%16s" % "SKIPPED",'=',counter["SKIPPED"])
        counter.pop("SKIPPED")
        for key,value in counter.items():
            print("%16s" % key,'=',value)
    return

def a_checker(args):
    """-a 选项检查
    """
    return

def a_executer(args):
    """-a 选项执行

    判断文件是否是源编码，如果是，则转换到目标编码。

    如果是文件，则转换该文件；
    如果是目录，则转换目录下的所有文本文件。
    """
    global path
    global detect_size
    global to_encoding
    global option_map
    if len(args) != 0:
        from_encodings = set(args)
    else:
        from_encodings = {"GB2312","UTF-8-SIG"}
    # 如果目标是文件
    if os.path.isfile(path):
        try:
            encoding = detect_encoding(path)
            if encoding in from_encodings:
                recode_file(path,encoding,to_encoding)
                print(encoding,"->",to_encoding,'-',path)
            else:
                print("encoding \"",encoding,"\" is not in from encodings.",
                      sep="")
                print("nothing to do.")
        except Exception as e:
            print(e)
    # 如果目标是目录
    else:
        counter = {"SKIPPED":0}
        # 如果要求递归
        if recursive_flag:
            for root,dirs,files in os.walk(path):
                for i in files:
                    try:
                        my_path = os.path.join(root,i)
                        encoding = detect_encoding(my_path)
                        if encoding in from_encodings:
                            recode_file(my_path,encoding,to_encoding)
                            print(encoding,"->",to_encoding,'-',my_path)
                            add_counter(counter,encoding)
                    except:
                        print("[SKIPPED]",my_path)
                        add_counter(counter,"SKIPPED")
        # 否则只处理目标目录
        else:
            for i in os.listdir(path):
                my_path = os.path.join(path,i)
                if os.path.isfile(my_path):
                    try:
                        encoding = detect_encoding(my_path)
                        if encoding in from_encodings:
                            recode_file(my_path,encoding,to_encoding)
                            print(encoding,"->",to_encoding,'-',my_path)
                            add_counter(counter,encoding)
                    except:
                        print("[SKIPPED]",my_path)
                        add_counter(counter,"SKIPPED")
        print()
        print("Recode to:",to_encoding)
        print("Total:")
        if counter["SKIPPED"] != 0:
            print("%16s" % "SKIPPED",'=',counter["SKIPPED"])
        counter.pop("SKIPPED")
        for key,value in counter.items():
            print("%16s" % key,'=',value)
    return
    
def r_executer(args):
    """-r 选项执行
    
    设定递归标志位
    """
    global recursive_flag
    recursive_flag = True
    return

def f_checker(args):
    """-f 选项检查
    """
    if len(args) < 1:
        raise parser_framework.MissingArgument("-f")
    elif len(args) > 1:
        raise parser_framework.UnexpectedArgument(args[1])
    return

def f_executer(args):
    """-f 选项执行

    设定强制源编码
    """
    global from_encoding
    from_encoding = args[0]
    return

def t_checker(args):
    """-r 选项检查
    """
    if len(args) < 1:
        raise parser_framework.MissingArgument("-t")
    elif len(args) > 1:
        raise parser_framework.UnexpectedArgument(args[1])
    return

def t_executer(args):
    """-t 选项执行

    设定目标编码
    """
    global to_encoding
    to_encoding = args[0]
    return

def ds_checker(args):
    """-ds 选项检查
    """
    if len(args) < 1:
        raise parser_framework.MissingArgument("-ds")
    elif len(args) > 1:
        raise parser_framework.UnexpectedArgument(args[1])
    if not args[0].isnumeric():
        raise parser_framework.InvalidArgument(args[0] + "is not an integer.")
    return

def ds_executer(args):
    """-ds 选项执行

    设定采样大小
    """
    global detect_size
    detect_size = int(args[0])
    return

def h_executer(args):
    """-h 选项处理

    输出帮助信息
    """
    print("""Help for recode.py

A script tool for text file encoding.

Options:
    -h      show help.
    -f      force source encoding.
    -t      set target encoding.
    -r      recursive mode.
    -ds     set detective size (default: 1024).
    -l      list encoding of a file or files in a folder.
    -a      auto mode.""")
    return

def info():
    """输出脚本信息
    """
    print("""recode.py v1.1
Copyright (c) 2019 by Yuhao Gu. All rights reserved.
For help, use option "-h".""")
    return

def default_executer(args):
    """默认执行函数
    """
    global from_encoding
    if from_encoding is None:
        raise parser_framework.MissingArgument("-f [encoding]")
    a_executer([from_encoding])
    return

def main():
    Option = parser_framework.Option
    option_map = {
        "-h":Option(-1,h_executer),
        "-f":Option(0,f_executer,f_checker),
        "-t":Option(0,t_executer,t_checker),
        "-r":Option(0,r_executer),
        "-ds":Option(0,ds_executer,ds_checker),
        "-l":Option(1,l_executer),
        "-a":Option(2,a_executer,a_checker)
        }
    parser = parser_framework.Parser(option_map,zero_checker,zero_executer,
                                     Option(1,default_executer),info)
    parser(sys.argv)
    return

if __name__ == "__main__":
    main()
