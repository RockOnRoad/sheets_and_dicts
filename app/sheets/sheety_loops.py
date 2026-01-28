import logging
import random
import time
from gspread import Worksheet
from gspread.exceptions import APIError


logger = logging.getLogger(__name__)


#  Этот слой нужен в том случае, когда декоратор принимает аргументы
def retryable(
    *,
    # upd: Message | CallbackQuery | None = None,
    # base_text: str | None = None,
    retries=8,
    base_delay=2,
):
    #  Слой декоратора
    def decorator(fn):
        #  Слой логики
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    print(f"Attempt {attempt + 1} for function {fn.__name__}")
                    return fn(*args, **kwargs)
                except APIError as e:
                    logger.warning("APIError encountered. Retrying...", exc_info=e)
                    if attempt == retries - 1:
                        raise
                    time.sleep(base_delay * (2**attempt) + random.random())

        return wrapper

    return decorator


# @retryable_and_animated
# async def get_last_row(ws: Worksheet):
#     return len(ws.col_values(1)) + 2


def make_safe_update(ws: Worksheet):
    @retryable()
    def safe_update(row, col, value):
        return ws.update_cell(row, col, value)

    return safe_update
