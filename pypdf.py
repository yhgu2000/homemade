__version__ = "0.1 (2023-4-1)"
__copyright__ = """pypdf v%(version)s

Copyright (c) 2019-2020 by Yuhao Gu. All rights reserved.
"""


import click
from PyPDF2 import (
    PdfFileMerger,
    PdfFileReader,
    PdfFileWriter,
    PageObject,
    PaperSize,
    Transformation,
)


@click.group()
@click.version_option(__version__, message=__copyright__)
def cli():
    """基于PyPDF2的实用工具"""


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
    type=click.Path(exists=False, writable=True),
    default="output.pdf",
)
def merge(inputs: tuple[str], output: str):
    """将一组PDF文件中的页按顺序合并为一个文件"""

    merger = PdfFileMerger()
    for i in inputs:
        with open(i, "rb") as f:
            merger.append(PdfFileReader(f))
    merger.write(output)


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
def reduce_to_a3x2(input, output):
    """将文档缩印为A5，然后将每两页A5拼成一页A4"""

    def scale_to_a3(page: PageObject):
        fact = float(
            min(
                PaperSize.A5.width / page.mediaBox.width,
                PaperSize.A5.height / page.mediaBox.height,
            )
        )
        page.add_transformation(Transformation().scale(fact, fact))
        # page.scale_by(fact)
        # page.scale_to(PaperSize.A5.width, PaperSize.A5.height)

    with open(input, "rb") as fin, open(output, "wb") as fout:
        pdf_reader = PdfFileReader(fin)
        pdf_writer = PdfFileWriter()

        with click.progressbar(
            length=pdf_reader.numPages,
            label="处理页面...",
        ) as bar:
            for i in range(1, pdf_reader.numPages, 2):
                page_left = pdf_reader.pages[i - 1]
                page_right = pdf_reader.pages[i]

                scale_to_a3(page_left)
                scale_to_a3(page_right)

                page_both = PageObject.createBlankPage(
                    None, PaperSize.A4.height, PaperSize.A4.width
                )
                page_both.mergeTranslatedPage(page_left, 0, 0)
                page_both.mergeTranslatedPage(page_right, PaperSize.A5.width, 0)

                pdf_writer.add_page(page_both)

                bar.update(2)

            if i < pdf_reader.numPages:
                page_left = pdf_reader.pages[pdf_reader.numPages - 1]

                scale_to_a3(page_left)

                page_both = PageObject.createBlankPage(
                    None, PaperSize.A4.height, PaperSize.A4.width
                )
                page_both.mergeTranslatedPage(page_left, 0, 0)

                pdf_writer.add_page(page_both)

                bar.update(1)

        click.echo("写入文件...", nl=False)
        pdf_writer.write(fout)
        click.echo(" OK!")


cli()
