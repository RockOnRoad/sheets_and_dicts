__all__ = ("router",)

from aiogram import Router

from .base import rtr as base_rtr

router = Router()
router.include_router(base_rtr)
