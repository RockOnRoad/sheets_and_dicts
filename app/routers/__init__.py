__all__ = ("router",)

from aiogram import Router

from .commands import router as commands_rtr
from .workflow import router as workflow_rtr

router = Router(name=__name__)
router.include_routers(commands_rtr, workflow_rtr)
