import re
from re import Pattern

from app.dicts.names import BRANDS, MODELS


def parse(pattern: Pattern[str], text: str) -> str:
    if m := re.search(pattern, text):
        match = m.groupdict()
        match["full_match"] = m.group()
        match["rest"] = text.replace(match["full_match"], "", 1).strip()
    else:
        match: dict = {"full_match": "", "rest": text}
    return match


def parse_size(text: str) -> dict[str, str]:
    size_pattern = (
        r"(?:"
        r"(?:(?P<width>\d{2,3})[/xX*]?)?"
        r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        r"\s*(?P<diameter>((?:(?:RZ|Z)?R)|/)\d{2}(?:[,.]\d)?(?:[CС]|LT)?)"
        r") "
    )
    size_pattern2 = (
        r"(?:"
        r"(?P<diameter>(?:(?:RZ|Z)?R)\d{2}(?:[,.]\d)?(?:[CС]|LT)?)"
        r"\s*(?:(?P<width>\d{2,3})[/xX*]?)?"
        r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        r") "
    )
    c_pattern = r"(?:\s*(?P<comercial>[CС]) )"

    result = parse(size_pattern, text)
    try:
        if result["width"] is None:
            result = parse(size_pattern2, text)
    except KeyError:
        if result["full_match"] == "":
            raise ValueError("Size not found in text")

    if result["height"] is None:
        result["height"] = ""

    if "/" in result["diameter"]:
        result["diameter"] = result["diameter"].replace("/", "R")

    result["diam"] = result["diameter"].strip("ZRCСLT")

    _c = parse(c_pattern, result.get("rest", ""))
    result["comercial"] = _c.get("comercial", "")
    result["rest"] = (
        result.get("rest", "").replace(_c.get("full_match", ""), "").strip()
    )

    return result


def parse_model_and_brand(text: str = "", seq: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    if seq:
        result = parse_size(text)
    rest = result.get("rest", text).upper().replace("_", " ")

    brand_pattern = re.compile(
        "|".join(
            f"(?P<_{str(e)}>{re.escape(v)})" for e, v in enumerate(list(BRANDS.keys()))
        ),
        re.IGNORECASE,
    )
    brand_match = parse(brand_pattern, rest)
    # if brand_match:
    #     result["rest"] = brand_match["rest"]
    brand = BRANDS.get(brand_match.get("full_match", ""), "?")

    model = "?"
    if m := MODELS.get(brand, None):

        model_pattern = re.compile(
            "|".join(
                f"(?P<_{str(e)}>{re.escape(v)})" for e, v in enumerate(list(m.keys()))
            ),
            re.IGNORECASE,
        )
        model_match = parse(model_pattern, brand_match.get("rest", ""))
        model = m.get(model_match.get("full_match", ""), "?")
        if brand_match:
            result["rest"] = brand_match["rest"]
        result["rest"] = model_match.get("rest", "")

    result["brand"] = brand
    result["model"] = model
    return result


def parse_indexes(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_model_and_brand(text=text, seq=True)
    rest = result.get("rest", text)

    indexes_pattern = r"\b(?:(?P<indexes>\d{2,3}(?:/\d{2,3})?\s?(?:[A-ZТ]|ZR)))\b"
    indexes_match = parse(indexes_pattern, rest)
    result["indexes"] = indexes_match.get("indexes", "?")
    result["rest"] = indexes_match.get("rest", "")
    return result


def parse_suv(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_indexes(text=text, seq=True)
    rest = result.get("rest", text)

    suv_pattern = r"(?P<suv> SUV)\b"
    suv_match = parse(suv_pattern, rest)
    result["suv"] = suv_match.get("suv", "")
    result["rest"] = suv_match.get("rest", "")
    return result


def parse_xl(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_suv(text=text, seq=True)
    rest = result.get("rest", text)

    xl_pattern = r"(?P<xl> XL)\b"
    xl_match = parse(xl_pattern, rest)
    result["xl"] = xl_match.get("xl", "")
    result["rest"] = xl_match.get("rest", "")
    return result


def parse_stud(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_xl(text=text, seq=True)
    rest = result.get("rest", text)

    stud_pattern = r"(?P<stud>(?:^|\s)(ШИПЫ|ШИП|Ш|STUD)\b)"
    stud_match = parse(stud_pattern, rest)

    if stud_match.get("stud", None):
        result["stud"] = True
    else:
        result["stud"] = False
    result["rest"] = stud_match.get("rest", "")
    return result


def parse_year(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_stud(text=text, seq=True)
    rest = result.get("rest", text)

    year_pattern = r"(?:(?P<year>20\d{2})( ГОД|ГОД|Г|Г\.))\b"
    year_match = parse(year_pattern, rest)
    result["year"] = year_match.get("year", "")
    result["rest"] = year_match.get("rest", "")
    return result


def parse_all(text: str) -> dict[str, str]:
    result: dict[str, str] = parse_year(text=text, seq=True)
    return result
