#  scotchenko
import pandas as pd  # type: ignore
from pandas import ExcelFile, DataFrame
from gspread import Worksheet


async def harv_scotchenko(xlsx: ExcelFile, ws: Worksheet):
    #  Конвертируем единственный лист в DataFrame
    df: DataFrame = pd.read_excel(xlsx, sheet_name=0)

    # pd.set_option("display.max_columns", None)
    # print(df.columns)

    # print(df.head(20))
