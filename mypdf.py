__version__ = "0.2 (2024-10-7)"
__copyright__ = """mypdf v%(version)s

Copyright (c) 2019-2024 by Yuhao Gu. All rights reserved.
"""


import click


@click.group()
@click.version_option(__version__, message=__copyright__)
def cli():
    """基于 pypdf 的 PDF 文件实用工具"""


@cli.command()
@click.argument(
    "input",
    nargs=1,
    type=click.Path(exists=True, readable=True, dir_okay=False),
)
@click.argument(
    "seperators",
    nargs=-1,
    type=click.INT,
)
@click.option(
    "-o",
    "--output",
    "output",
    help="输出目录",
    type=click.Path(exists=False, writable=True, file_okay=False),
)
@click.option(
    "-a",
    "--all",
    "all",
    help="拆分为所有单页",
    is_flag=True,
)
def split(input: str, seperators: list[int], output: str | None, all: bool):
    """将 INPUT 按 SEPERATORS 给出的页码（首页为1）拆分为多个文件"""

    import os
    import os.path as osp

    from pypdf import PdfReader, PdfWriter

    if output is None:
        output = osp.splitext(input)[0]
    os.makedirs(output, exist_ok=True)

    pdf_reader = PdfReader(input)
    num_pages = pdf_reader.get_num_pages()

    if all:
        for i in range(num_pages):
            out_path = osp.join(output, f"{i+1}.pdf")
            click.echo(out_path + " ...", nl=False)
            with open(out_path, "wb") as f:
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.get_page(i))
                pdf_writer.write(f)
            click.echo(" OK")
        return

    seps = {i for i in seperators if 0 < i < num_pages}
    seps.add(num_pages)
    seperators = sorted(seps)
    last = 0
    for sep in seperators:
        sep -= 1
        out_path = osp.join(output, f"{last + 1}-{sep}.pdf")
        click.echo(out_path + " ...", nl=False)
        with open(out_path, "wb") as f:
            pdf_writer = PdfWriter()
            pdf_writer.append(pdf_reader, pages=(last, sep))
            pdf_writer.write(f)
        click.echo(" OK")
        last = sep
    click.echo("DONE")


@cli.command()
@click.argument(
    "inputs",
    nargs=-1,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "-o",
    "--output",
    "output",
    help="输出文件名",
    type=click.Path(exists=False, writable=True, dir_okay=False),
    default="merge-output.pdf",
)
def merge(inputs: tuple[str], output: str):
    """将 INPUTS 中的页面按指定顺序合并为一个文件

    如果 INPUTS 中包含目录，则将目录中的 .pdf 后缀文件按字典序合并输出
    """

    import os
    import os.path as osp
    from shlex import quote

    from pypdf import PdfReader, PdfWriter

    pdf_writer = PdfWriter()

    for input in inputs:
        if os.path.isdir(input):
            files = [f for f in os.listdir(input) if f.endswith(".pdf")]
            files.sort()
            for file in files:
                path = osp.join(input, file)
                click.echo(path + " ...", nl=False)
                pdf_reader = PdfReader(path)
                pdf_writer.append(pdf_reader)
                click.echo(" OK")
        else:
            click.echo(input + " ...", nl=False)
            pdf_reader = PdfReader(input)
            pdf_writer.append(pdf_reader)
            click.echo(" OK")

    click.echo("\n输出 " + quote(output))
    with open(output, "wb") as f:
        pdf_writer.write(f)
    click.echo("DONE")


@cli.command()
@click.argument(
    "input",
    nargs=1,
    type=click.Path(exists=True, readable=True, dir_okay=False),
)
@click.option(
    "-o",
    "--output",
    "output",
    help="输出目录",
    type=click.Path(exists=False, writable=True, file_okay=False),
)
def extract_images(input: str, output: str | None):
    """提取 INPUT 中的图片到目录"""

    import json
    import os
    import os.path as osp
    from shlex import quote

    from pypdf import PdfReader

    if output is None:
        output = osp.splitext(input)[0]
    os.makedirs(output, exist_ok=True)

    pdf_reader = PdfReader(input)
    num_pages = pdf_reader.get_num_pages()

    def recongnize_format(image_data: bytes) -> str:
        if image_data.startswith(b"\x89\x50\x4e\x47"):
            return "png"
        if image_data.startswith(b"\xff\xd8\xff"):
            return "jpg"
        if image_data.startswith(b"\x47\x49\x46"):
            return "gif"
        if image_data.startswith(b"\x42\x4d"):
            return "bmp"
        if image_data.startswith(b"\x25\x50\x44\x46"):
            return "pdf"
        return "img"

    names = dict[str, str]()
    for pageno in range(num_pages):
        page = pdf_reader.get_page(pageno)
        for i, img in enumerate(page.images):
            name = f"{pageno+1}-{i+1}.{recongnize_format(img.data)}"
            names[name] = img.name
            click.echo(name + " ...", nl=False)
            with open(osp.join(output, name), "wb") as f:
                f.write(img.data)
            click.echo(" OK")

    click.echo("\n输出 " + quote(osp.join(output, "names.json")))
    with open(osp.join(output, "names.json"), "w") as f:
        json.dump(names, f, indent=2)
    click.echo("DONE")


@cli.command()
def extract_attachments():
    """提取 PDF 中的附件"""

    raise NotImplementedError


@cli.command()
def encrypt():
    """加密 PDF"""

    raise NotImplementedError


@cli.command()
def decrypt():
    """解密 PDF"""

    raise NotImplementedError


@cli.command()
@click.argument(
    "input",
    nargs=1,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "-o",
    "--output",
    "output",
    help="输出文件",
    type=click.Path(exists=False, writable=True),
    default="output.pdf",
)
def reduce_to_a5x2(input: str, output: str):
    """把 INPUT 缩放到A5，然后每两页A5拼成一页A4"""

    from shlex import quote

    from pypdf import PageObject, PaperSize, PdfReader, PdfWriter, Transformation

    def scale_to_a5(page: PageObject):
        fact = float(
            min(
                PaperSize.A5.width / page.mediabox.width,
                PaperSize.A5.height / page.mediabox.height,
            )
        )
        page.add_transformation(Transformation().scale(fact, fact))

    with open(input, "rb") as fin, open(output, "wb") as fout:
        pdf_reader = PdfReader(fin)
        pdf_writer = PdfWriter()

        with click.progressbar(
            length=pdf_reader.get_num_pages(),
            label="处理页面...",
        ) as bar:
            for i in range(1, pdf_reader.get_num_pages(), 2):
                page_left = pdf_reader.pages[i - 1]
                page_right = pdf_reader.pages[i]

                scale_to_a5(page_left)
                scale_to_a5(page_right)

                page_both = PageObject.create_blank_page(
                    None, PaperSize.A4.height, PaperSize.A4.width
                )
                page_both.merge_translated_page(page_left, 0, 0)
                page_both.merge_translated_page(page_right, PaperSize.A5.width, 0)

                pdf_writer.add_page(page_both)

                bar.update(2)

            if i < pdf_reader.get_num_pages():
                page_left = pdf_reader.pages[pdf_reader.get_num_pages() - 1]

                scale_to_a5(page_left)

                page_both = PageObject.create_blank_page(
                    None, PaperSize.A4.height, PaperSize.A4.width
                )
                page_both.merge_translated_page(page_left, 0, 0)

                pdf_writer.add_page(page_both)

                bar.update(1)

        click.echo("\n输出 " + quote(output))
        pdf_writer.write(fout)
        click.echo("DONE")


cli()
