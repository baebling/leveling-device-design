"""List named STEP assembly products and their positioned shape bounds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence, TDF_Tool
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool


def label_name(label: TDF_Label) -> str:
    attribute = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attribute):
        return attribute.Get().ToExtString()
    return ""


def shape_bounds(label: TDF_Label) -> dict[str, float] | None:
    shape = XCAFDoc_ShapeTool.GetShape_s(label)
    if shape.IsNull():
        return None
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return {
        "xmin": round(xmin, 6),
        "xmax": round(xmax, 6),
        "ymin": round(ymin, 6),
        "ymax": round(ymax, 6),
        "zmin": round(zmin, 6),
        "zmax": round(zmax, 6),
        "xlen": round(xmax - xmin, 6),
        "ylen": round(ymax - ymin, 6),
        "zlen": round(zmax - zmin, 6),
    }


def label_entry(label: TDF_Label) -> str:
    entry = TCollection_AsciiString()
    TDF_Tool.Entry_s(label, entry)
    return entry.ToCString()


def walk(shape_tool: XCAFDoc_ShapeTool, label: TDF_Label, depth: int) -> list[dict[str, object]]:
    referred = TDF_Label()
    is_reference = XCAFDoc_ShapeTool.IsReference_s(label)
    target = label
    if is_reference and XCAFDoc_ShapeTool.GetReferredShape_s(label, referred):
        target = referred
    row = {
        "depth": depth,
        "entry": label_entry(label),
        "name": label_name(label) or label_name(target),
        "is_reference": is_reference,
        "is_assembly": XCAFDoc_ShapeTool.IsAssembly_s(target),
        "is_simple_shape": XCAFDoc_ShapeTool.IsSimpleShape_s(target),
        "bounds_mm": shape_bounds(label),
    }
    rows = [row]
    children = TDF_LabelSequence()
    if XCAFDoc_ShapeTool.GetComponents_s(target, children, False):
        for index in range(1, children.Length() + 1):
            rows.extend(walk(shape_tool, children.Value(index), depth + 1))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    XCAFApp_Application.GetApplication_s()
    document = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    if reader.ReadFile(str(args.step.resolve())) != 1:
        raise RuntimeError("STEP read failed")
    if not reader.Transfer(document):
        raise RuntimeError("STEP transfer failed")

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(document.Main())
    roots = TDF_LabelSequence()
    shape_tool.GetFreeShapes(roots)
    rows = []
    for index in range(1, roots.Length() + 1):
        rows.extend(walk(shape_tool, roots.Value(index), 0))
    report = {
        "source": str(args.step.resolve()),
        "root_count": roots.Length(),
        "labels": rows,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
