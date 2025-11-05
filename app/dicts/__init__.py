from enum import Enum
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat


class VehicleType(str, Enum):
    LIGHT = "l"  # light
    LIGHTTRUCK = "lt"  # light-truck
    MOTORCYCLE = "m"  # moto
    TRUCK = "t"  # truck
    SPECIAL = "z"  # 'z' so it stays last alphabetically


class SeasonType(str, Enum):
    WINTER = "w"
    SUMMER = "s"
    ALLSEASON = "as"


class TireSKU(BaseModel):
    art: str = ...
    width: int | float = ""
    hei: int | float | str = ""
    diam: int | float = ""
    siz: str = ""
    lt: VehicleType = ""
    seas: SeasonType = ""
    stud: bool = False
    supp: str = ""
    name: str = ""
    full_size: str = ""


class TireStock(BaseModel):
    price: PositiveInt | PositiveFloat | None = None
