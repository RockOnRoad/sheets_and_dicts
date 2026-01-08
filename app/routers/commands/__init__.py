__all__ = ("router",)

from aiogram import Router

from .base import rtr as base_rtr
from .maintenance import rtr as m_rtr

router = Router()
router.include_routers(base_rtr, m_rtr)
