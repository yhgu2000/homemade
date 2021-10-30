__version__ = "3.1 (2021-10-29)"
__copyright__ = """recode v%(version)s

Copyright (c) 2019-2020 by Yuhao Gu. All rights reserved.
"""

import os
from collections import Counter
from fnmatch import fnmatch
from typing import Union

import chardet
import click

default_from_encodings = (
    "UTF-8",
    "UTF-8-SIG",
    "BIG5",
    "GB2312",
    "GB18030",
    "EUC-TW",
    "HZ-GB-2312",
    "ISO-2022-CN",
)


class UnkownEncoding(RuntimeError):
    pass


def detect_encoding(file_path: str) -> str:
    with open(file_path, "rb") as f:
        s = f.read(4096)
    ans = chardet.detect(s)
    if ans["confidence"] < 0.8:
        raise UnkownEncoding()
    return ans["encoding"].upper()


def translate_newlines(newlines: Union[str, tuple, None]) -> str:
    codec = {"\r": "CR", "\n": "LF", "\r\n": "CRLF"}
    if type(newlines) is str:
        return codec[newlines]
    elif type(newlines) is tuple:
        return ",".join(map(codec.__getitem__, newlines))
    return "NONE"


def atomic_write(path: str, s: str, encoding: str, newline: str):
    temp = path + "~~~~~"
    try:
        with open(temp, "w", encoding=encoding, newline=newline) as f:
            f.write(s)
        os.remove(path)
        os.rename(temp, path)
    except BaseException as e:
        if os.path.exists(temp):
            os.remove(temp)
        raise e
    return


@click.command()
@click.version_option(__version__, message=__copyright__)
@click.argument(
    "pathes",
    nargs=-1,
    type=click.Path(exists=True, writable=True),
)
@click.option(
    "-r",
    "--recursive",
    help="Search directory recursively.",
    type=click.Path(exists=True, file_okay=False),
    multiple=True,
)
@click.option(
    "--include",
    help="Only include files that matches this pattern.",
    default="*",
)
@click.option(
    "--exclude",
    help="Exclude files that matches this pattern.",
    default="",
)
@click.option(
    "-f",
    "--from",
    "froms",
    help=f"Source encodings. Default: {','.join(default_from_encodings)}",
    default=default_from_encodings,
    multiple=True,
)
@click.option(
    "-t",
    "--to",
    help="Recode to target encoding.",
    type=str,
)
@click.option(
    "-n",
    "--newline",
    "eof",
    help="Reformat to target end of line.",
    type=click.Choice(
        ["CR", "LF", "CRLF"],
        case_sensitive=False,
    ),
)
@click.option(
    "-e",
    "--encoding",
    "force_encoding",
    help="Specify source encoding.",
    type=str,
)
def cli(
    pathes: tuple[str],
    recursive: tuple[str],
    include: str,
    exclude: str,
    froms: tuple[str],
    to: str,
    eof: str,
    force_encoding: str,
):
    """文本文件重编码脚本，具备编码识别、指定输出编码、行尾格式化功能。

    \b
    1. 转换一个文件的编码和行尾
        recode file -t utf-8 --eof=LF
    \b
    2. （递归）识别目录里所有文件的编码，将符合的源编码转换到目标编码
        recode dir1 -r dir2 -f gb2312 big5 -t utf-8
    \b
    3. 强制指定源编码
        recode file -r dir -e gb2312 -t utf-8
    \b
    4. 保持原编码，只修改行尾
        recode file dir --eof=CR
    \b
    5. 模式包含与排除，同时匹配时，优先选择排除
        recode -r dir1 dir2 --include "a*" --exclude "*.cpp"
    """

    def match(name):
        return not fnmatch(name, exclude) and fnmatch(name, include)

    def gen_matched_files():
        for path in pathes:
            if os.path.isfile(path):
                if match(os.path.basename(path)):
                    yield path

            elif os.path.isdir(path):
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    if match(name) and os.path.isfile(full_path):
                        yield full_path

        for dir in recursive:
            for path, _, files in os.walk(dir):
                for file in files:
                    if match(file):
                        yield os.path.join(path, file)
        return

    results = Counter()

    if to:
        to = to.upper()
    if eof:
        newline = {"CR": "\r", "LF": "\n", "CRLF": "\r\n"}[eof]
    else:
        newline = None

    for path in gen_matched_files():
        try:
            result = None

            if not force_encoding:
                encoding = detect_encoding(path)

            if to is None:
                if eof is None:
                    # 什么都不做模式，只统计文本编码
                    result = click.style(f"[{encoding}]", fg="green")

                else:
                    # 只格式化行尾
                    with open(path, "r", encoding=encoding) as f:
                        content = f.read()
                        if f.newlines == newline:
                            result = click.style("[SKIPPED]", fg="green")
                        else:
                            newlines = translate_newlines(f.newlines)
                    if result is None:
                        atomic_write(path, content, encoding, newline)
                        result = click.style(
                            f"[{newlines} -> {eof}]", fg="green"
                        )

            else:
                # 全功能模式
                if encoding == to:
                    result = click.style("[SKIPPED]", fg="green")
                elif encoding not in froms:
                    result = click.style(
                        f"[{encoding}]", fg="black", bg="yellow"
                    )
                else:
                    with open(path, "r", encoding=encoding) as f:
                        content = f.read()
                    atomic_write(path, content, to, newline)
                    result = click.style(f"[{encoding} -> {to}]", fg="green")

        except BaseException as e:
            result = click.style(f"[{type(e).__name__}]", bg="red")

        results[result] += 1
        click.echo(result + " " + path)

    # 打印统计结果
    if results:
        click.echo("\nRESULTS:")
        for result, count in results.items():
            click.echo(f"\t{result}: {count}")
    return


def test():
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-r",
            r"C:\Users\GuYuhao\Desktop\2",
            "-t",
            "gbk",
        ],
    )
    return result


if __name__ == "__main__":
    cli()
    # print(test())
