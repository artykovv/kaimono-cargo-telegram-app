from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage

from conf.limit import AntiFloodMiddleware

from conf.config import TOKEN

from routers.start import router as start
from routers.menus import router as menu

from routers.handlers.products import router as products
from routers.handlers.searcher import router as searcher
from routers.handlers.profile import router as profile
from routers.handlers.support import router as support
from routers.handlers.helper import router as helper
from routers.handlers.address import router as address
from routers.handlers.instruction import router as instruction
from routers.handlers.info import router as info


from routers.handlers.main_products.productsBishkek import router as productsBishkek
from routers.handlers.main_products.productsChina import router as productsChina
from routers.handlers.main_products.productsTransit import router as productsTransit


from functions.register_success import router as register_success


bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Добавляем middleware для ограничения частоты сообщений (например, 1 секунды)
dp.message.middleware(AntiFloodMiddleware(limit=1))

dp.include_router(start)
dp.include_router(menu)

dp.include_router(products)
dp.include_router(searcher)
dp.include_router(profile)
dp.include_router(helper)
dp.include_router(address)
dp.include_router(instruction)
dp.include_router(info)


dp.include_router(productsBishkek)
dp.include_router(productsChina)
dp.include_router(productsTransit)

dp.include_router(support)
dp.include_router(register_success)



