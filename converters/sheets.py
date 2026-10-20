"""Spreadsheets with pandas + openpyxl (xlrd for .xls, odfpy for .ods)."""
import html
import json
from pathlib import Path

import pandas as pd

from .tools import ConversionError


def _read(src):
    try:
        if Path(src).suffix.lower() == ".csv":
            return {"Sheet1": pd.read_csv(src)}
        return pd.read_excel(src, sheet_name=None)
    except Exception as e:
        raise ConversionError(f"This spreadsheet could not be read: {e}")


def convert(src, out_dir, fmt, opts):
    sheets, stem = _read(src), Path(src).stem
    if fmt == "csv":
        outs = []
        for name, df in sheets.items():  # one CSV per sheet
            out = Path(out_dir) / (f"{stem}.csv" if len(sheets) == 1 else f"{stem}_{name}.csv")
            df.to_csv(out, index=False, encoding="utf-8-sig")  # BOM so Excel shows accents correctly
            outs.append(out)
        return outs
    out = Path(out_dir) / f"{stem}.{fmt}"
    if fmt == "xlsx":
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            for name, df in sheets.items():
                df.to_excel(w, sheet_name=str(name)[:31], index=False)
    elif fmt == "json":
        data = {n: json.loads(df.to_json(orient="records", date_format="iso", force_ascii=False))
                for n, df in sheets.items()}
        out.write_text(json.dumps(next(iter(data.values())) if len(data) == 1 else data,
                                  ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "html":
        parts = [f"<h2>{html.escape(str(n))}</h2>{df.to_html(index=False, na_rep='')}" for n, df in sheets.items()]
        out.write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(stem)}</title></head>'
                       f'<body>{"".join(parts)}</body></html>', encoding="utf-8")
    return [out]
