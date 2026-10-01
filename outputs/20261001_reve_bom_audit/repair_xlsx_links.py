"""Repair the XLSX external-link relationships unsupported by artifact-tool.

Only sheet1 hyperlink references and their relationship targets are changed.
Cell data, formula caches, formatting, and other ZIP members remain untouched.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
import os
import sys

from lxml import etree
from openpyxl import load_workbook


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SHEET = "xl/worksheets/sheet1.xml"
RELS = "xl/worksheets/_rels/sheet1.xml.rels"


def repair(path: Path) -> None:
    workbook = load_workbook(path, read_only=True, data_only=False)
    sheet = workbook["Sheet1"]
    visible = {f"G{row}": sheet[f"G{row}"].value for row in range(4, 71)}
    if any(not isinstance(url, str) or not url.startswith("https://") for url in visible.values()):
        raise ValueError("Expected an HTTPS URL in every BOM link cell")
    workbook.close()

    temp_path = None
    try:
        with ZipFile(path, "r") as original:
            sheet_xml = etree.fromstring(original.read(SHEET))
            rel_xml = etree.fromstring(original.read(RELS))
            links = sheet_xml.find(f"{{{MAIN}}}hyperlinks")
            if links is None:
                raise ValueError("Expected hyperlinks container in source worksheet")
            rel_by_id = {
                rel.get("Id"): rel for rel in rel_xml.findall(f"{{{PACKAGE_REL}}}Relationship")
            }
            link_by_ref = {
                link.get("ref"): link for link in links.findall(f"{{{MAIN}}}hyperlink")
            }
            next_id = 1
            while f"rId{next_id}" in rel_by_id:
                next_id += 1
            for cell, url in visible.items():
                link = link_by_ref.get(cell)
                if link is None:
                    rid = f"rId{next_id}"
                    next_id += 1
                    link = etree.SubElement(links, f"{{{MAIN}}}hyperlink", ref=cell)
                    link.set(f"{{{OFFICE_REL}}}id", rid)
                    rel = etree.SubElement(rel_xml, f"{{{PACKAGE_REL}}}Relationship")
                    rel.set("Id", rid)
                    rel.set("Type", f"{OFFICE_REL}/hyperlink")
                    rel.set("TargetMode", "External")
                    rel_by_id[rid] = rel
                rid = link.get(f"{{{OFFICE_REL}}}id")
                rel = rel_by_id.get(rid)
                if rel is None:
                    raise ValueError(f"Missing relationship {rid} for {cell}")
                rel.set("Target", url)

            rewritten = {
                SHEET: etree.tostring(sheet_xml, encoding="UTF-8", xml_declaration=True),
                RELS: etree.tostring(rel_xml, encoding="UTF-8", xml_declaration=True),
            }
            with NamedTemporaryFile(suffix=".xlsx", dir=path.parent, delete=False) as temp:
                temp_path = Path(temp.name)
            with ZipFile(temp_path, "w") as fixed:
                for member in original.infolist():
                    fixed.writestr(member, rewritten.get(member.filename, original.read(member.filename)))
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Pass exactly one XLSX path")
    repair(Path(sys.argv[1]))
