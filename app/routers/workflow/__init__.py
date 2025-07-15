__all__ = ("router",)

from aiogram import Router

from .upload import rtr as upload_rtr

router = Router()
router.include_router(upload_rtr)
