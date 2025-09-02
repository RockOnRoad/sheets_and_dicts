from gspread import Worksheet
from gspread.utils import ValueRenderOption
from ..sheets import get_ws


async def move():
    """**Moves columns data from one ws to another by articules**\n
    1 time use function that I used to move user written data from an old sheet to new one
    """

    ws: Worksheet = await get_ws("snow_4tochki")
    ot_data = ws.get(
        range_name="A3:Q", value_render_option=ValueRenderOption.unformatted
    )
    # link = (line[8] if len(line) > 8 else "" for line in ot_data)

    old_data = []
    for c in ot_data:
        old_data.append(
            {
                "art": str(c[0]) if len(c) else "",
                "link": str(c[8]) if len(c) > 8 else "",
                "price": str(c[11]) if len(c) > 11 else "",
                "own": str(c[12]) if len(c) > 12 else "",
                "comm": str(c[14]) if len(c) > 14 else "",
                "upd": str(c[15]) if len(c) > 15 else "",
                "bet": str(c[16]) if len(c) > 16 else "",
            }
        )
    print(len(old_data))
    # print(old_data[280:320])

    ws: Worksheet = await get_ws("Остатки поставщиков (зима)")
    nt_data = (
        item[0] if item else ""
        for item in ws.get("A3:A", value_render_option=ValueRenderOption.unformatted)
    )
    links = []
    prices = []
    owns = []
    comms = []
    upds = []
    bets = []
    for art in nt_data:
        match = next((line for line in old_data if line["art"] == art), None)
        if match:
            links.append([match["link"]])
            prices.append([match["price"]])
            owns.append([match["own"]])
            comms.append([match["comm"]])
            upds.append([match["upd"]])
            bets.append([match["bet"]])
        else:
            links.append([""])
            prices.append([""])
            owns.append([""])
            comms.append([""])
            upds.append([""])
            bets.append([""])

    ws.batch_update(
        data=[
            {
                "range": "M3",
                "values": links,
            },
            {
                "range": "P3",
                "values": prices,
            },
            {
                "range": "Q3",
                "values": owns,
            },
            {
                "range": "R3",
                "values": comms,
            },
            {
                "range": "S3",
                "values": upds,
            },
            {
                "range": "T3",
                "values": bets,
            },
        ],
    )
