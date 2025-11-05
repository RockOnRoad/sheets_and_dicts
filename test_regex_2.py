import re

from app.dicts import names

# Comprehensive test cases for tire specifications
test_cases = [
    # Standard metric formats
    "автошина 205/55 R16 ATTAR S01 94V XL",
    "автошина 155 R14 ATTAR S01 94V XL",
    "автошина 195 R14C KUMHO KC53 106/104",
    "автошина 235/65 R16C ATTAR W03 115/113R Ш",
    "автошина 155/65 R13 KUMHO RS02 121/120M",
    "автошина 195/65 R15 CONTINENTAL CONTIECO 91H",
    "автошина 275/40 R22 ROADCRUZA RA1100 107Т",
    "автошина 265/50 ZR22 YOKOHAMA G057B 112V",
    # Imperial formats
    "автошина 35x12,5 R17 KUMHO AT52 121R Ш",
    "автошина 33x12,5 R18 ROYAL_BLACK ROYAL_M/T 118Q",
    "автошина 30x9,5 R15 BF_GOODRICH MUD_TERRAIN_T/A_KM3 104Q",
    "автошина 31x10,5 R15 YOKOHAMA GEOLANDAR A/T G015 109Q",
    "автошина 31x10,50 R15 TRIANGLE TR292 XL 109S",
    "автошина 33x12,5 R18 ROYAL_BLACK ROYAL_M/T 118Q",
    # Edge cases and variations
    "автошина 7,00 R16 TRIANGLE TR-668A_14PR_LT 118/114L TT",
    "автошина 8,50 R16 BRIDGESTONE R250 121/118M",
    "автошина 9.00 R16 MICHELIN XDE2 121/118M",
    "автошина 7,50 R16C KUMHO RS02 XL 121/120M",
    "автошина 8,25 R16 TRIANGLE TR-690",
    "автошина 7,50 R16 TRIANGLE TRD99 (M+S)",
    # Problematic cases that should be skipped
    "УТ000010627/5: Bf Goodrich Mud Terrain T/a Km3 0 RNone 104Q 4tochki + olta'",
    "автошина 30x9,5 R15 BF_GOODRICH MUD_TERRAIN_T/A_KM3 104Q",
    "Invalid tire format string",
    "Just some random text without tire specs",
    # Complex brand names with spaces
    "автошина 225/45 R17 BF GOODRICH G-FORCE COMP-2 A/S 91W XL",
    "автошина 245/40 R18 MICHELIN PILOT SPORT 4S 97Y XL",
    "автошина 215/55 R16 CONTINENTAL PREMIUM CONTACT 6 97V",
]


for line in test_cases:

    def extract_match(pattern, text):
        if m := re.search(pattern, text):
            full_match = m.group()

            try:
                width = m.group("width").replace(",", ".")
                width = float(width) if "." in width else int(width)
            except AttributeError:
                width = None

            try:
                hei = m.group("height").replace(",", ".")
                hei = float(hei) if "." in hei else int(hei)
            except AttributeError:
                hei = None

            diam = m.group("diameter")
            diam = re.sub(r"[^0-9.,]", "", diam)
            diam = diam.replace(",", ".")

            result = {
                "full": full_match,
                "width": width,
                "height": hei,
                "diameter": diam,
                "rest": text.replace(full_match, "", 1).strip(),
            }
        else:
            result = {
                "full": None,
                "width": None,
                "height": None,
                "diameter": None,
                "rest": text.strip(),
            }
        return result

    size_pattern = (
        r"(?:"
        r"(?:(?P<width>\d{1,3})[x/]?)?"
        r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        r"\s+(?P<diameter>Z?R\d{2}(?:[,.]\d)?[CС]?)"
        r")\s+"
    )
    size_extract = extract_match(size_pattern, line)

    print(size_extract.get("diameter") if isinstance(size_extract, dict) else None)

    # def extract(text: str, find: str) -> str:
    #     found = False
    #     if find in text:
    #         found = True
    #     return found

    # def extract_value(text: str, names_ali: dict) -> str:
    #     text_upper = text.upper().replace("_", " ")
    #     for name_raw, name_std in names_ali.items():
    #         if extract(text=text_upper, find=name_raw):
    #             return name_std
    #     return "?"  # or a fallback

    # # brand: str = extract(text=line, names_ali=names.BRANDS)
    # # print(brand)

    # try:
    #     brand: str = extract_value(text=line, names_ali=names.BRANDS)
    # except KeyError:
    #     brand = "?"

    # try:
    #     model: str = extract_value(text=line, names_ali=names.MODELS[brand])
    # except KeyError:
    #     model = "?"

    # for n in names.SPOKES:
    #     stud = extract(text=line.upper().replace("_", " "), find=n)
    #     if stud:
    #         break
    # print(f"{brand} {model}")
    # # print(stud)
