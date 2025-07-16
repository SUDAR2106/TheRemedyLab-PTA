"""OCR + digital‑file text extraction + metric parsing + abnormal‑flagging.
Supports PDF, DOCX, CSV, and JSON uploads.
Improved to:
• Match metrics only when they appear at the **start of a line** (after optional whitespace), preventing the
  'cholesterol' alias from picking up 'Non‑HDL Cholesterol' values.
• Prioritise **longer aliases first** to avoid partial‑phrase collisions.
• Derive common lipid ratios if missing.
• Gracefully flag metrics lacking reference ranges.
• Rely solely on `utils.metrics` for alias data.
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, Tuple, Union

import cv2
import fitz                    # PyMuPDF (for PDF → image in OCR fallback)
import pandas as pd
import pdfplumber
import pytesseract
import docx                     # python‑docx

from utils.metrics import METRIC_ALIASES, ALIAS_LOOKUP, REF_RANGES

# ➡️ If Tesseract is not in PATH, set it here
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

FlaggedMetric = Tuple[str, str]   # (value‑string, colour)

# ---------------------------------------------------------------------------
# Helper: build alias patterns anchored to line‑start, sorted by length‑desc
# ---------------------------------------------------------------------------

def _build_alias_patterns() -> list[tuple[re.Pattern, str]]:
    # Sort aliases by length (desc) so longer, more specific phrases match first
    sorted_aliases = sorted(ALIAS_LOOKUP.items(), key=lambda x: -len(x[0]))
    patterns: list[tuple[re.Pattern, str]] = []
    for alias, canonical in sorted_aliases:
        # Anchor to start of line (after optional whitespace) to avoid mid‑line collisions
        pat = re.compile(rf"^\s*{re.escape(alias)}\b", re.IGNORECASE)
        patterns.append((pat, canonical))
    return patterns

ALIAS_PATTERNS = _build_alias_patterns()

# ---------------------------------------------------------------------------
# Extract text for each supported file type
# ---------------------------------------------------------------------------

def _extract_text_pdf(path: str) -> str:
    """Prefer embedded text; fall back to OCR on first page."""
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        print(f"[extract] pdfplumber error: {exc}")

    if len(text.strip()) < 20:  # likely scanned
        try:
            doc = fitz.open(path)
            pix = doc[0].get_pixmap(dpi=300)
            tmp = "_tmp_ocr.png"
            pix.save(tmp)
            img = cv2.imread(tmp)
            text = pytesseract.image_to_string(img)
            os.remove(tmp)
        except Exception as exc:
            print(f"[extract] PDF‑OCR error: {exc}")
    return text


def _extract_text_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:
        print(f"[extract] DOCX read error: {exc}")
        return ""


def _extract_text_csv(path: str) -> str:
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        return df.to_string(index=False)
    except Exception as exc:
        print(f"[extract] CSV read error: {exc}")
        return ""


def _extract_text_json(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as exc:
        print(f"[extract] JSON read error: {exc}")
        return ""

# ---------------------------------------------------------------------------
# Utility to pull first float from a string
# ---------------------------------------------------------------------------

def _clean_number(token: str) -> Union[float, None]:
    token = token.replace(",", "")
    m = re.search(r"[-+]?[0-9]*\.?[0-9]+", token)
    if m:
        try:
            return float(m.group())
        except ValueError:
            pass
    return None

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_metrics(input: Union[str, os.PathLike], is_path: bool = True) -> Dict[str, FlaggedMetric]:
    """Accepts either file path or raw text based on is_path."""
    if is_path:
        ext = os.path.splitext(str(input).lower())[1]
        if ext == ".pdf":
            text = _extract_text_pdf(input)
        elif ext in {".docx", ".doc"}:
            text = _extract_text_docx(input)
        elif ext == ".csv":
            text = _extract_text_csv(input)
        elif ext == ".json":
            text = _extract_text_json(input)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    else:
        text = input  # input is raw text directly
        
    # Initialise dict with None
    values: Dict[str, Union[float, None]] = {m: None for m in METRIC_ALIASES}

    lines = text.splitlines()

    # -----------------------------------------------------------
    # Pass 1: Free-form text parsing (existing logic)
    # -----------------------------------------------------------
    for raw in lines:
        line_lc = raw.lower()
        line = re.sub(r"[\-–=|]+", ":", line_lc)
        for alias_raw, canonical in ALIAS_LOOKUP.items():
            if re.search(rf"\b{re.escape(alias_raw)}\b", line):
                segment = line.split(alias_raw, 1)[1]
                val = _clean_number(segment)
                if val is not None and values[canonical] is None:
                    values[canonical] = val

    # -----------------------------------------------------------
    # Pass 2: Table-based parsing (| delimited lab reports)
    # -----------------------------------------------------------
    for line in lines:
        if '|' not in line or len(line) < 10:
            continue  # skip non-table lines
        cols = [c.strip().lower() for c in line.strip().strip('|').split('|')]
        if len(cols) < 2:
            continue
        metric_text = cols[0]
        value_text = cols[1]
        for alias, canonical in ALIAS_LOOKUP.items():
            if alias in metric_text and values[canonical] is None:
                val = _clean_number(value_text)
                if val is not None:
                    values[canonical] = val

    # -----------------------------------------------------------
    # Derive ratios
    # -----------------------------------------------------------
    def _derive(key: str, func):
        if values.get(key) is None:
            try:
                result = func()
                if result is not None and not (result != result):  # exclude NaN
                    values[key] = round(result, 2)
            except ZeroDivisionError:
                pass

    _derive("LDL/HDL Ratio", lambda: values["LDL"] / values["HDL"] if values["LDL"] and values["HDL"] else None)
    _derive("Total Cholesterol/HDL Ratio", lambda: values["Total Cholesterol"] / values["HDL"] if values["Total Cholesterol"] and values["HDL"] else None)
    _derive("TG/HDL Ratio", lambda: values["Triglycerides"] / values["HDL"] if values["Triglycerides"] and values["HDL"] else None)
    _derive("Non-HDL Cholesterol", lambda: values["Total Cholesterol"] - values["HDL"] if values["Total Cholesterol"] and values["HDL"] else None)

    return _flag(values)
# def extract_metrics(path: str) -> Dict[str, FlaggedMetric]:
#     """Universal extractor – returns colour‑flagged metric dict."""
#     ext = os.path.splitext(path.lower())[1]
#     if ext == ".pdf":
#         text = _extract_text_pdf(path)
#     elif ext in {".docx", ".doc"}:
#         text = _extract_text_docx(path)
#     elif ext == ".csv":
#         text = _extract_text_csv(path)
#     elif ext == ".json":
#         text = _extract_text_json(path)
#     else:
#         raise ValueError(f"Unsupported file type: {ext}")

#     values: Dict[str, Union[float, None]] = {m: None for m in METRIC_ALIASES}

#     # -----------------------------------------------------------
#     # Pass 1: extract explicit values line‑by‑line
#     # -----------------------------------------------------------
#     for raw in text.splitlines():
#         # fast path – skip empty or too short lines
#         if len(raw) < 3:
#             continue
#         # collapse multiple delimiters
#         line = re.sub(r"[\-–=|]+", ":", raw)
#         for pat, canonical in ALIAS_PATTERNS:
#             if pat.search(line):
#                 segment = pat.split(line, maxsplit=1)[1]
#                 val = _clean_number(segment)
#                 if val is not None and (values[canonical] is None):
#                     values[canonical] = val
#                 # continue scanning for other metrics on same line

#     # -----------------------------------------------------------
#     # Pass 2: derive common lipid ratios if missing
#     # -----------------------------------------------------------
#     def _derive(key: str, func):
#         if values.get(key) is None:
#             try:
#                 res = func()
#                 if res is not None and not (res != res):  # exclude NaN
#                     values[key] = round(res, 2)
#             except ZeroDivisionError:
#                 pass

#     _derive("LDL/HDL Ratio", lambda: values["LDL"] / values["HDL"] if values["LDL"] and values["HDL"] else None)
#     _derive("Total Cholesterol/HDL Ratio", lambda: values["Total Cholesterol"] / values["HDL"] if values["Total Cholesterol"] and values["HDL"] else None)
#     _derive("TG/HDL Ratio", lambda: values["Triglycerides"] / values["HDL"] if values["Triglycerides"] and values["HDL"] else None)
#     _derive("Non-HDL Cholesterol", lambda: values["Total Cholesterol"] - values["HDL"] if values["Total Cholesterol"] and values["HDL"] else None)

#     return _flag(values)

# ---------------------------------------------------------------------------
# Flagging helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
#  Convenience: expose generic text extractor
# ---------------------------------------------------------------------------
def extract_text(path: str) -> str:
    """Return raw text for any supported report file."""
    ext = os.path.splitext(path.lower())[1]
    if ext == ".pdf":
        return _extract_text_pdf(path)
    elif ext in {".docx", ".doc"}:
        return _extract_text_docx(path)
    elif ext == ".csv":
        return _extract_text_csv(path)
    elif ext == ".json":
        return _extract_text_json(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ---------------------------------------------------------------------------
#  Patient meta‑information parser
# ---------------------------------------------------------------------------
import re
from typing import Dict
from PIL import Image
import pytesseract

def extract_patient_info(text: str) -> Dict[str, str]:
    info = {
        "Patient Name": None,
        "Patient ID": None,
        "Age": None,
        "Sex": None,
        "Report Date": None,
        "UHID": None,
        "Lab ID": None,
    }

    patterns = {
        "Patient Name": [
            r"Name\s*[:\-]?\s*(Baby\.?|Master\.?)?\s*([A-Z][a-zA-Z .'-]+)",
            r"Patient Name\s*[:\-]?\s*([A-Z][a-zA-Z .'-]+)",
        ],
        "Patient ID": [
            r"(?:Patient ID|PID|Reg\.?\s*No\.?)\s*[:\-]?\s*(\S+)"
        ],
        "Age": [
            r"Age\s*/\s*Sex\s*[:\-]?\s*(\d+\s*(?:YRS|Years|Mon|Months)?)",
            r"Age\s*[:\-]?\s*(\d+\s*(?:YRS|Years|Mon|Months)?)"
        ],
        "Sex": [
            r"Age\s*/\s*Sex\s*[:\-]?\s*\d+\s*(?:YRS|Mon|Months)?\s*/\s*(M|F)",
            r"Sex\s*[:\-]?\s*(Male|Female|M|F|Other)"
        ],
        "Report Date": [
            r"(?:Report(?:ed)? on|Date|Generated on|Registered on|Collected on)\s*[:\-]?\s*([0-3]?\d[/\-\.][01]?\d[/\-\.]\d{4})"
        ],
        "UHID": [
            r"UHID\s*No\s*[:\-]?\s*(\S+)"
        ],
        "Lab ID": [
            r"LAB\s*ID\s*No\s*[:\-]?\s*(\S+)"
        ]
    }

    for key, regex_list in patterns.items():
        for pattern in regex_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "Patient Name":
                    parts = match.groups()
                    value = " ".join(p for p in parts if p).strip()
                else:
                    value = match.group(1).strip()

                if key == "Sex":
                    if value.upper() in ["M", "MALE"]:
                        info[key] = "Male"
                    elif value.upper() in ["F", "FEMALE"]:
                        info[key] = "Female"
                    else:
                        info[key] = value.capitalize()
                else:
                    info[key] = value
                break
    return info

# --- OCR Step ---
def get_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text
# import re
# from typing import Dict

# def extract_patient_info(text: str) -> Dict[str, str]:
#     info = {
#         "Patient Name": None,
#         "Patient ID": None,
#         "Age": None,
#         "Sex": None,
#         "Report Date": None,
#         "UHID": None,
#         "Lab ID": None,
#     }

#     patterns = {
#         "Patient Name": [
#             r"Name\s*[:\-]?\s*(Baby\.?|Master\.?)?\s*([A-Z][a-zA-Z .'-]+)",  # Baby / Master prefix
#             r"Patient Name\s*[:\-]?\s*([A-Z][a-zA-Z .'-]+)",
#             r"Mr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
#         ],
#         "Patient ID": [
#             r"(?:Patient ID|PID|Reg\.?\s*No\.?)\s*[:\-]?\s*(\S+)"
#         ],
#         "Age": [
#             r"Age\s*/\s*Sex\s*[:\-]?\s*(\d+\s*(?:YRS|Years|Mon|Months)?)",
#             r"Age\s*[:\-]?\s*(\d+\s*(?:YRS|Years|Mon|Months)?)"
#         ],
#         "Sex": [
#             r"Age\s*/\s*Sex\s*[:\-]?\s*\d+\s*(?:YRS|Mon|Months)?\s*/\s*(M|F)",
#             r"Sex\s*[:\-]?\s*(Male|Female|M|F|Other)"
#         ],
#         "Report Date": [
#             r"(?:Report(?:ed)? on|Date|Generated on|Registered on|Collected on)\s*[:\-]?\s*([0-3]?\d[/\-\.][01]?\d[/\-\.]\d{4}(?:\s*\d{1,2}:\d{2}\s*[APMapm]{2})?)"
#         ],
#         "UHID": [
#             r"UHID\s*No\s*[:\-]?\s*(\S+)"
#         ],
#         "Lab ID": [
#             r"LAB\s*ID\s*No\s*[:\-]?\s*(\S+)"
#         ]
#     }

#     for key, regex_list in patterns.items():
#         for pattern in regex_list:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 # Handle multiple groups (e.g., Baby. + Name)
#                 if key == "Patient Name":
#                     parts = match.groups()
#                     value = " ".join(p for p in parts if p).strip()
#                 else:
#                     value = match.group(1).strip()

#                 # Normalize gender
#                 if key == "Sex":
#                     if value.upper() in ["M", "MALE"]:
#                         info[key] = "Male"
#                     elif value.upper() in ["F", "FEMALE"]:
#                         info[key] = "Female"
#                     else:
#                         info[key] = value.capitalize()
#                 else:
#                     info[key] = value
#                 break  # Use first match only

#     return info


def _flag(values: Dict[str, Union[float, None]]) -> Dict[str, FlaggedMetric]:
    flagged: Dict[str, FlaggedMetric] = {}
    for metric, val in values.items():
        if val is None:
            flagged[metric] = ("❌ Missing", "red")
            continue
        if metric not in REF_RANGES:
            flagged[metric] = (f"{val} (no ref)", "gray")
            continue
        lo, hi = REF_RANGES[metric]
        colour = "green" if lo <= val <= hi else "orange"
        suffix = " ⚠️" if colour == "orange" else ""
        flagged[metric] = (f"{val}{suffix}", colour)
    return flagged

# ---------------------------------------------------------------------------

