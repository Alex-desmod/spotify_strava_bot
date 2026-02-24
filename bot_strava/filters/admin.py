from aiogram.filters import BaseFilter
from aiogram.types import Message

class AdminFilter(BaseFilter):

    async def __call__(self, message: Message, admin_id: int) -> bool:
        return message.from_user.id == admin_id

