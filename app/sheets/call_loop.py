import asyncio
import time
import random
import gspread

MAX_RETRIES = 8
BASE_DELAY = 1  # seconds

# for attempt in range(MAX_RETRIES):
#     try:
#         number_last_row = len(ws.col_values(1)) + 2
#         break

#     except gspread.exceptions.APIError as e:
#         # If it's the last attempt – rethrow
#         if attempt == MAX_RETRIES - 1:
#             raise

#         # Exponential backoff + jitter
#         delay = BASE_DELAY * (2**attempt)
#         delay += random.uniform(0, 0.5)

#         await asyncio.sleep(delay)
