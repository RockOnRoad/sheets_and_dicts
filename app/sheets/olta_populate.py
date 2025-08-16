from datetime import datetime
from random import randint

from gspread import Worksheet

async def update_olta_amounts(data, sheet):
    r: int = float(randint(0, 40))
    g: int = float(randint(0, 20))
    b: int = float(randint(0, 40))

    today = datetime.today().strftime("%d.%m")
    sheet.insert_cols([[f"Наличие\n{today}"], [f"Стоимость\n{today}"]], col=25)
    sheet.update(data, "Y3")
    sheet.format("Y3:Z", {"backgroundColor": {"red": r, "green": g, "blue": b}})
    sheet.update(
        values=[[f"Стоимость\nx4 ({today})", f"Цена x4\n({today})"]],
        range_name="V1:W1",
        value_input_option="USER_ENTERED",
    )
    sheet.update(
        values=[
            [
                "=ARRAYFORMULA($Y$2:$Y)",
                '=ARRAYFORMULA(IF($Y$2:$Y>0,$Z$2:$Z-$AB$2:$AB,""))',
            ]
        ],
        range_name="J2:K2",
        value_input_option="USER_ENTERED",
    )
    sheet.update_cell(2, 24, "=ARRAYFORMULA($Y$2:$Y-$AA$2:$AA)")


async def prepare_amounts_olta(data: list[dict], sheet):
    wanted_keys: tuple = ("full_code", "amount", "price")
    ex_codes: list = [item[0] if item else "" for item in sheet.get("A3:A")]

    amounts_data: list = [{k: d.get(k, "") for k in wanted_keys} for d in data]

    stock_lookup = {line["full_code"]: line for line in amounts_data}

    amounts: list = []
    for code in ex_codes:
        if code in stock_lookup:
            line = stock_lookup[code]
            #  {'full_code': 'F7640', 'amount': 1, 'price': 9266}
            amounts.append([line["amount"], line["price"]])
        else:
            amounts.append([0, 0])
    #  amounts -> [[1, 53000], [14, 57000], [4, 7700], [20, 3250], ...]
    # print(f"Количество строк наличия - {len(amounts)}")
    return amounts

async def upload_to_sheet_olta(data: list[dict], sheet):
    """Вносим данные в таблицу.\n
    - Сначала добавляем необходимое количество пустых строк\n
    - Затем при помощи метода `sheet.batch_update()` заносим скрытые параметры в начало таблицы\n
    - И информативные параметры начиная со столбца `M`
    """


    if any(data.values()):
        sheet.add_rows(len(data["hidden"]) + 1)

        last_row: int = len(sheet.get("A3:A")) + 4

        sheet.batch_update(
            data=[
                {"range": f"A{last_row}", "values": data["hidden"]},
                {"range": f"M{last_row}", "values": data["visible"]},
            ],
        )


async def prepare_data_olta(data: list[dict]):
    """Оставляем только те значения, которые попадут в таблицу\n
    - В список "hidden" попадут *9* столбцов: "full_code", "art", "width", "height", "diameter", 
    "lt", "season", "spikes" и "siz".
    - В список "visible" попадут *3* столбца: "marking", "full_size" и "age"
    """

    table_data: dict = {}
    hidden_columns = []
    visible_columns = []
    
    for line in data:
        hidden_row = [line["full_code"], line["art"], line["width"], line["height"], line["diameter"], line["lt"], line["season"], line["spikes"], line["siz"]]
        visible_row = [line["marking"], line["full_size"], line["age"]]

        hidden_columns.append(hidden_row)
        visible_columns.append(visible_row)

    table_data["hidden"] = hidden_columns
    table_data["visible"] = visible_columns

    return table_data


async def add_rows(data: list[dict], sheet):
    """- Выгружаем уже имеющиеся позиции\n
    - Создаём **НОВЫЙ СПИСОК** с теми позициями, которых ещё не было\n
    <Если в новом списке более 1 позиции>\n
    - Приводим новые данные в table ready формат (: list[list])\n
    - Загружаем новые позиции в таблицу `olta`
    """

    ex_codes: list = [item[0] if item else "" for item in sheet.get("A3:A")]
    fresh_stock: list = [line for line in data if line["full_code"] not in ex_codes]

    if len(fresh_stock) > 0:

        table_ready_stock = await prepare_data_olta(data=fresh_stock)
        await upload_to_sheet_olta(data=table_ready_stock, sheet=sheet)

    # for i in range(50):
    # print(f"{fresh_stock["amount"]}шт. - {fresh_stock["price"]}р.")
    print(f"{data[0]}")

    current_amounts: list[list] = await prepare_amounts_olta(data=data, sheet=sheet)
    # for i in range(50):
    #     print(current_amounts[i])
    await update_olta_amounts(data=current_amounts, sheet=sheet)