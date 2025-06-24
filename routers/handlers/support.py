from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import redis.asyncio as redis
import logging

from conf.config import ADMIN_CHAT_ID, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME, TOKEN
from functions.func import get_text

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
bot = Bot(token=TOKEN)


# Подключение к Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

class SupportState(StatesGroup):
    waiting_for_message = State()
    in_dialogue = State()

async def safe_redis_operation(operation, *args, **kwargs):
    """Обёртка для операций с Redis с обработкой ошибок."""
    try:
        result = await operation(*args, **kwargs)
        logger.info(f"Redis operation {operation.__name__} with args {args} returned {result}")
        return result
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected Redis error: {e}")
        return None

@router.message(F.text == "⚙️ Поддержка")
async def support_message(message: Message, state: FSMContext):
    whatsapp = await get_text(key="whatsapp")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="WhatsApp", url=f"{whatsapp}")],
        [InlineKeyboardButton(text="Написать через Telegram", callback_data="start_support")]
    ])
    await message.answer("📩 Связь с поддержкой:", reply_markup=kb)
    await state.set_state(SupportState.waiting_for_message)

@router.callback_query(F.data == "start_support")
async def support_start_support(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("📝 Опишите вашу проблему.")
    await state.set_state(SupportState.waiting_for_message)
    await cb.answer()

@router.message(SupportState.waiting_for_message, F.chat.type == "private")
async def message_forward_to_admin_topic(message: Message, state: FSMContext):
    try:
        topic = await bot.create_forum_topic(
            chat_id=ADMIN_CHAT_ID,
            name=f"Ticket[{message.from_user.id}]: {message.from_user.full_name}"
        )
        thread_id = topic.message_thread_id

        forwarded = await bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            message_thread_id=thread_id
        )

        # Сохраняем маппинг в Redis
        result = await safe_redis_operation(
            redis_client.set, f"ticket:{thread_id}", message.from_user.id
        )
        if result is None:
            await message.reply("❌ Ошибка сервера. Попробуйте позже.")
            return

        await state.update_data(thread_id=thread_id)
        await state.set_state(SupportState.in_dialogue)

        await message.reply("✅ Тикет создан. Напишите для общения или /close для закрытия.")

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=thread_id,
            text="📩 Новый тикет открыт.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Закрыть тикет", callback_data=f"admin_close_{thread_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in message_forward_to_admin_topic: {e}")
        await message.reply("❌ Ошибка при создании тикета. Попробуйте позже.")

@router.message(SupportState.in_dialogue, F.chat.type == "private", F.text != "/close")
async def reply_to_admin(message: Message, state: FSMContext):
    user_data = await state.get_data()
    thread_id = user_data.get('thread_id')
    
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    if not user_id:
        await message.reply("❌ Тикет не найден или закрыт.")
        await state.clear()
        return

    await bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        message_thread_id=thread_id
    )

@router.message(SupportState.in_dialogue, F.chat.type == "private", F.text == "/close")
async def user_close_ticket(message: Message, state: FSMContext):
    user_data = await state.get_data()
    thread_id = user_data.get('thread_id')
    
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    if not user_id:
        await message.reply("❌ Тикет не найден или закрыт.")
        await state.clear()
        return

    await bot.close_forum_topic(
        chat_id=ADMIN_CHAT_ID,
        message_thread_id=thread_id
    )
    
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        message_thread_id=thread_id,
        text=f"❌ Пользователь {message.from_user.full_name} (ID: {message.from_user.id}) закрыл тикет."
    )
    
    await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
    
    await message.reply("✅ Тикет закрыт.")
    await state.clear()

@router.callback_query(F.data.startswith("admin_close_"))
async def admin_close_ticket_button(cb: CallbackQuery):
    thread_id = int(cb.data.split("_")[2])
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    
    if not user_id:
        await cb.message.reply("❌ Тикет не найден.")
        await cb.answer()
        return

    await bot.close_forum_topic(
        chat_id=ADMIN_CHAT_ID,
        message_thread_id=thread_id
    )
    
    await bot.send_message(
        user_id,
        "✅ Тикет закрыт администратором."
    )
    
    await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
    
    await cb.message.reply("✅ Тикет закрыт.")
    await cb.answer()

@router.message(F.chat.id == ADMIN_CHAT_ID, F.message_thread_id, ~F.text.startswith("/close"))
async def admin_reply_in_topic(message: Message, state: FSMContext):
    thread_id = message.message_thread_id
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    if not user_id:
        logger.info(f"No user_id found for thread_id {thread_id}")
        return

    logger.info(f"Processing admin message in thread {thread_id}, content_type={message.content_type}")
    if message.text:
        await bot.send_message(
            user_id,
            message.text
        )
    elif message.photo:
        await bot.send_photo(
            user_id,
            photo=message.photo[-1].file_id,
            caption=message.caption
        )
    elif message.document:
        await bot.send_document(
            user_id,
            document=message.document.file_id,
            caption=message.caption
        )
    else:
        logger.info(f"Unsupported content type {message.content_type} in thread {thread_id}")

@router.message(F.chat.id == ADMIN_CHAT_ID, F.text.startswith("/close"))
async def admin_close_ticket_command(message: Message):
    thread_id = message.message_thread_id
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    
    if not user_id:
        await message.reply("❌ Тикет не найден.")
        return

    await bot.close_forum_topic(
        chat_id=ADMIN_CHAT_ID,
        message_thread_id=thread_id
    )
    
    await bot.send_message(
        user_id,
        "✅ Тикет закрыт администратором."
    )
    
    await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
    
    await message.reply("✅ Тикет закрыт.")