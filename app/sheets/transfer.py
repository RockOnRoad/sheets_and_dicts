from gspread import Worksheet
from gspread.utils import ValueRenderOption
from ..sheets import get_ws


async def move():
    """**Moves columns data from one ws to another by articules**\n
    1 time use function that I used to move data from an old sheet to new one
    """

    ws: Worksheet = await get_ws("snow_4tochki")
    ot_data = ws.get(
        range_name="A3:W", value_render_option=ValueRenderOption.unformatted
    )
    # link = (line[8] if len(line) > 8 else "" for line in ot_data)

    old_data = []
    for c in ot_data:
        old_data.append(
            {
                "art": str(c[0]) if len(c) else "",
                "amo": str(c[21]) if len(c) > 21 else "",
                "price": str(c[22]) if len(c) > 22 else "",
            }
        )
    print(len(old_data))
    # print(old_data[280:320])

    ws: Worksheet = await get_ws("4tochki")
    nt_data = (
        item[0] if item else ""
        for item in ws.get("A3:A", value_render_option=ValueRenderOption.unformatted)
    )
    amos = []
    prices = []
    for art in nt_data:
        match = next((line for line in old_data if line["art"] == art), None)
        if match:
            amos.append([match["amo"]])
            prices.append([match["price"]])
        else:
            amos.append([""])
            prices.append([""])

    ws.batch_update(
        data=[
            {
                "range": "X3",
                "values": amos,
            },
            {
                "range": "V3",
                "values": prices,
            },
        ],
    )
