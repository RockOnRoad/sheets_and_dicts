from enum import Enum
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat


class VehicleType(str, Enum):
    LIGHT = "l"
    LIGHTTRUCK = "lt"
    MOTORCYCLE = "m"
    TRUCK = "t"
    SPECIAL = "z"  # 'z' so it stays last alphabetically


class SeasonType(str, Enum):
    WINTER = "w"
    SUMMER = "s"
    ALLSEASON = "as"


class TireSKU(BaseModel):
    art: str = ...
    width: int | float = ""
    hei: int | float = ""
    diam: int | float = ""
    siz: str = ""
    lt: VehicleType = ""  # l: light, lt: light-truck, m: moto, t: truck, z: special
    seas: SeasonType = ""  # w: winter, s: summer, as: all-season
    stud: bool = False
    supp: str = ""
    name: str = ""
    full_size: str = ""
    # price: PositiveInt | PositiveFloat | None = None


class TireStock(BaseModel):
    price: PositiveInt | PositiveFloat | None = None
