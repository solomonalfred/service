from pathlib import Path
from typing import Dict
import re
import os
from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph


PARAGRAPHS = "paragraphs"
TABLES = "tables"
TAG_PLACEHOLDER = "{`{tag}`}"

def check_file_exists(path: str | Path) -> bool:
    if os.path.exists(path):
        return True
    return False

def open_word(src_path: str | Path) -> Document:
    if not check_file_exists(src_path):
        raise FileNotFoundError("File not found")
    try:
        doc = Document(src_path)
    except Exception as e:
        raise Exception(f"Wrong file format: {e}")
    else:
        return doc

def save_template(template: Document, dst_path: str | Path) -> None:
    try:
        template.save(dst_path)
    except Exception as e:
        raise Exception(f"Can't save filled template: {e}")

def read_table(template: Document, tags: Dict[str, str]):
    for row in template.rows:
        for cell in row.cells:
            read_block(cell, tags)

def read_paragraph(template: Document, tags: Dict[str, str]):
    for run in template.runs:
        for tag, value in tags.items():
            plh = TAG_PLACEHOLDER.format(tag=tag)
            if plh in run.text:
                run.text = run.text.replace(plh, value)

def read_block(template: Document, tags: Dict[str, str]) -> None:
    for paragraph in getattr(template, PARAGRAPHS, []):
        read_paragraph(paragraph, tags)
    for table in getattr(template, TABLES, []):
        read_table(table, tags)

def render_template(template: Document, tags: Dict[str, str]):
    read_block(template, tags)
    for section in template.sections:
        read_block(section.header, tags)
        read_block(section.footer, tags)

if __name__ == "__main__":
    path = "../../../docs/Договор ИП.docx"
    tags = {
        "realm": "world",
        "user_name": "Alice",
    }
    doc = open_word(path)
