__all__ = ("router",)

from aiogram import Router

from .commands import router as commands_rtr

router = Router(name=__name__)
router.include_router(commands_rtr)
