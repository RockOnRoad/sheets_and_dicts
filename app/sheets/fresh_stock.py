from typing import Any

from gspread import Worksheet

from . import BASE_LAYOUT, STC


async def prepare_table_data(data: list[dict[str, Any]]) -> dict[str, list[Any]]:
    """**Returns table-ready grid of SKUs (stock keeping units)**

    This function prepares data for new stock units to be added to the worksheet.\n
    It processes the input data and formats it into a dictionary containing two lists:
    - `hidden`: Contains parameters for columns that will be hidden.
    - `visible`: Contains attributes that will be shown.\n


    :param data: `list[dict[str, Any]]` - List of stock objects to be processed.\n
    :return: `dict[list[list[Any]]]` - 2 lists of lists with data for new stock units.\n
    - `{'hidden': [[],[]], 'visible': [[],[]]}`
    - Outer list represents the whole block, inner lists are rows of parameters for each SKU.
    """

    table_data: dict[str, list[Any]] = {"hidden": [], "visible": []}
    for line in data:

        hidden_row = [
            line["art"],
            line["width"],
            line["hei"],
            line["diam"],
            line["siz"],
            line["lt"],
            line["seas"],
            line["stud"],
            line["supp"],
            line.get("code_w_prefix", ""),
        ]
        visible_row = [line["name"], line["full_size"], line.get("age", "")]

        table_data["hidden"].append(hidden_row)
        table_data["visible"].append(visible_row)

    return table_data


async def sort_stock(data: list[dict[str, Any]]):

    sorted_data: list[dict[str, Any]] = list()
    if len(data) > 0:
        sorted_data = sorted(
            data,
            key=lambda x: (
                x["lt"],
                x["name"],
                x["diam"],
                x["width"],
                x["hei"],
                x.get("full_code", ""),
            ),
        )
    return sorted_data


# async def fresh(
#     data: list[dict[str, Any]], table: str, supp: str
# ) -> list[dict[str, Any]]:
#     ws = await sheets_conn(table)

#     if table == supp == list(STC)[3]:  # olta
#         key: str = "code_w_prefix"
#     else:
#         key: str = "art"
#     letter: str = STC[table][key]["l"]
#     col: str = f"{letter}3:{letter}"

#     ex_arts: list[str] = [item[0] if item else "" for item in ws.get(col)]
#     fresh_stock: list[dict[str, Any]] = []
#     for obj in data:
#         if obj[key] not in ex_arts:
#             if obj[key] not in fresh_stock:
#                 fresh_stock.append(obj)

#     return fresh_stock


async def add_fresh_items(
    stock: list[dict[str, Any]], ws: Worksheet, supp: str
) -> list:
    """**Adds new stock items to the supplier worksheet.**

    :param stock: `list[dict[str, Any]]` - List of stock objects.
    :param ws: `gspread.Worksheet` - Worksheet instance where the stock will be added.
    :param table: `str` - Name of the worksheet to which the stock will be added.

    :return: `list` - List of hidden parameters.
    """
    # fresh_stock: list[dict[str, Any]] = await fresh(stock, table=supp, supp=supp)
    if stock:
        sorted_stock: list[dict[str, Any]] = await sort_stock(stock)
        prepared_stock: dict[str, list[Any]] = await prepare_table_data(sorted_stock)

        ws.add_rows(len(prepared_stock["hidden"]) + 1)

        number_last_row: int = len(ws.get("A3:A")) + 4

        letter_art: str = BASE_LAYOUT["art"]["l"]
        letter_name: str = STC[supp]["name"]["l"]

        ws.batch_update(
            data=[
                {
                    "range": f"{letter_art}{number_last_row}",
                    "values": prepared_stock["hidden"],
                },
                {
                    "range": f"{letter_name}{number_last_row}",
                    "values": prepared_stock["visible"],
                },
            ],
        )
    return prepared_stock["hidden"]
