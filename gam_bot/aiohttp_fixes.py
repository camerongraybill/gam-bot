import asyncio
from typing import Any


def patch_gather() -> None:
    original_gather = asyncio.gather
    def gather(*args, **kwargs) -> Any:
        return original_gather(*args, **{k:v for k,v in kwargs.items() if k != 'loop'})

    asyncio.gather = gather
