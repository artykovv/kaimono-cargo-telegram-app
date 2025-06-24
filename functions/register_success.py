from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
import redis.asyncio as redis
import logging

from functions.func import get_address, get_profile_user
from conf.config import ADMIN_CHAT_ID, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME, TOKEN

# Configure logging
logger = logging.getLogger(__name__)

router = Router()
bot = Bot(token=TOKEN)


# Redis configuration
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

async def safe_redis_operation(operation, *args, **kwargs):
    """Wrapper for Redis operations with error handling."""
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

async def forward_content_to_admin(message: Message, chat_id: int, thread_id: int, user_id: str, caption_prefix: str = ""):
    """Helper function to forward user content to admin thread."""
    try:
        caption = f"{caption_prefix}{message.caption or ''}".strip()
        if message.text:
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text=message.text
            )
        elif message.photo:
            await bot.send_photo(
                chat_id=chat_id,
                message_thread_id=thread_id,
                photo=message.photo[-1].file_id,
                caption=caption
            )
        elif message.document:
            await bot.send_document(
                chat_id=chat_id,
                message_thread_id=thread_id,
                document=message.document.file_id,
                caption=caption
            )
        elif message.video:
            await bot.send_video(
                chat_id=chat_id,
                message_thread_id=thread_id,
                video=message.video.file_id,
                caption=caption
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=chat_id,
                message_thread_id=thread_id,
                voice=message.voice.file_id,
                caption=caption
            )
        elif message.sticker:
            await bot.send_sticker(
                chat_id=chat_id,
                message_thread_id=thread_id,
                sticker=message.sticker.file_id
            )
        elif message.animation:
            await bot.send_animation(
                chat_id=chat_id,
                message_thread_id=thread_id,
                animation=message.animation.file_id,
                caption=caption
            )
        else:
            logger.info(f"Unsupported content type {message.content_type} from user {user_id}")
            await message.reply("⚠️ Этот тип сообщения не поддерживается для отправки поддержке.")
            return False
        logger.info(f"User {user_id} message sent to thread {thread_id}")
        return True
    except TelegramBadRequest as e:
        logger.error(f"Error forwarding user {user_id} message to thread {thread_id}: {e}")
        await message.reply("❌ Ошибка при отправке контента поддержке. Возможно, Диалог закрыт.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error forwarding user {user_id} message to thread {thread_id}: {e}")
        await message.reply("❌ Ошибка при отправке контента поддержке.")
        return False

class AddressCheckState(StatesGroup):
    waiting_for_screenshot = State()
    in_dialogue = State()


@router.callback_query(F.data == "get_instruction")
async def get_instruction(cb: CallbackQuery):
    """Handle instruction button callback."""
    try:
        instruction_message = (
            "📋 Инструкция по отправке адреса:\n\n"
            "1. Заполните ваш адрес в профиле.\n"
            "2. Сделайте скриншот или подготовьте любой контент (фото, видео, документ и т.д.), подтверждающий адрес.\n"
            "3. Нажмите 'Проверка через Telegram' и отправьте контент.\n"
            "4. Дождитесь подтверждения от администратора.\n\n"
            "Если возникнут вопросы, свяжитесь через WhatsApp или Telegram."
        )
        await cb.message.answer(instruction_message, parse_mode="HTML")
        await cb.answer()
    except TelegramBadRequest as e:
        logger.error(f"Error sending instruction: {e}")
        await cb.message.answer("❌ Ошибка при отправке инструкции. Попробуйте снова.")
        await cb.answer()

@router.callback_query(F.data == "start_screenshot_check")
async def start_screenshot_check(cb: CallbackQuery, state: FSMContext):
    """Initiate screenshot submission for address verification."""
    try:
        await cb.message.answer("📸 Пожалуйста, отправьте скриншот или любой контент для проверки адреса.")
        await state.set_state(AddressCheckState.waiting_for_screenshot)
        await state.update_data(user_name=cb.from_user.full_name, user_id=str(cb.from_user.id))
        await cb.answer()
    except TelegramBadRequest as e:
        logger.error(f"Error in start_screenshot_check: {e}")
        await cb.message.answer("❌ Ошибка при запросе контента. Попробуйте снова.")
        await cb.answer()

@router.message(AddressCheckState.waiting_for_screenshot)
async def process_screenshot(message: Message, state: FSMContext):
    """Process user-submitted content and create admin ticket."""
    try:
        user_data = await state.get_data()
        user_name = user_data.get("user_name")
        user_id = user_data.get("user_id")

        response = await get_profile_user(telegram_chat_id=user_id)
        if not response:
            await message.reply("❌ Ошибка: профиль не найден.")
            await state.clear()
            return
        user_profile = response[0]

        address = await get_address(telegram_chat_id=user_id)
        if not address:
            await message.reply("❌ Ошибка: адрес не найден.")
            await state.clear()
            return

        topic = await bot.create_forum_topic(
            chat_id=ADMIN_CHAT_ID,
            name=f"AddressCheck[{user_id}]: {user_name}"
        )
        thread_id = topic.message_thread_id

        ticket_info = (
            f"📍 Проверка адреса пользователя:\n\n"
            f"👤 ФИО: {user_profile['name']}\n"
            f"🌍 Город: {user_profile['city']}\n"
            f"📞 Номер: {user_profile['number']}\n\n"
            f"🪪 Код: KBK{user_profile['numeric_code']}\n\n"
            f"🏠 Адрес: {address}\n\n"
            f"💬 Напишите в этот Диалог для общения с пользователем или закройте его."
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=thread_id,
            text=ticket_info,
            parse_mode="HTML"
        )

        # Forward the user's content to the admin thread
        success = await forward_content_to_admin(
            message=message,
            chat_id=ADMIN_CHAT_ID,
            thread_id=thread_id,
            user_id=user_id,
            caption_prefix="📸 Скриншот или контент от пользователя: "
        )
        if not success:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                message_thread_id=thread_id,
                text="❌ Ошибка при отправке контента пользователя."
            )
            await state.clear()
            return

        # Add closure button only if content was forwarded successfully
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=thread_id,
            text="🔘 Выберите действие:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Закрыть Диалог", callback_data=f"admin_close_{thread_id}")]
            ])
        )

        result = await safe_redis_operation(
            redis_client.set, f"ticket:{thread_id}", user_id, ex=86400
        )
        if result is None:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                message_thread_id=thread_id,
                text="❌ Ошибка при сохранении Диалога в Redis."
            )
            await message.reply("❌ Ошибка при создании Диалога. Попробуйте позже.")
            await state.clear()
            return

        await message.reply(
            "✅ Контент отправлен на проверку."
        )
        await state.set_state(AddressCheckState.in_dialogue)
        await state.update_data(thread_id=thread_id)

    except Exception as e:
        logger.error(f"Error processing content for user {message.from_user.id}: {e}")
        await message.reply("❌ Ошибка при обработке контента. Попробуйте позже.")
        await state.clear()

@router.message(AddressCheckState.in_dialogue, F.chat.type == "private", F.text != "/close")
async def user_reply_to_admin(message: Message, state: FSMContext):
    """Handle user messages in the dialogue state."""
    user_data = await state.get_data()
    thread_id = user_data.get("thread_id")
    
    if not thread_id:
        await message.reply("❌ Диалог не найден. Начните процесс заново.")
        await state.clear()
        return

    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    if not user_id:
        await message.reply("❌ Диалог не найден или закрыт.")
        await state.clear()
        return

    await forward_content_to_admin(
        message=message,
        chat_id=ADMIN_CHAT_ID,
        thread_id=thread_id,
        user_id=user_id
    )

@router.message(AddressCheckState.in_dialogue, F.chat.type == "private", F.text == "/close")
async def user_close_ticket(message: Message, state: FSMContext):
    """Handle user-initiated ticket closure."""
    user_data = await state.get_data()
    thread_id = user_data.get("thread_id")
    
    if not thread_id:
        await message.reply("❌ Диалог не найден. Начните процесс заново.")
        await state.clear()
        return

    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    if not user_id:
        await message.reply("❌ Диалог не найден или закрыт.")
        await state.clear()
        return

    try:
        try:
            await bot.close_forum_topic(chat_id=ADMIN_CHAT_ID, message_thread_id=thread_id)
        except TelegramBadRequest as e:
            if "TOPIC_DELETED" in str(e):
                logger.warning(f"Topic {thread_id} already deleted or closed.")
            else:
                raise e

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=thread_id,
            text=f"❌ Пользователь {message.from_user.full_name} (ID: {user_id}) закрыл Диалог."
        )
        await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
        await message.reply("✅ Диалог закрыт.")
        await state.clear()
    except TelegramBadRequest as e:
        logger.error(f"Error closing ticket {thread_id} by user {user_id}: {e}")
        await message.reply("❌ Ошибка при закрытии Диалога.")
        await state.clear()
    except Exception as e:
        logger.error(f"Unexpected error closing ticket {thread_id} by user {user_id}: {e}")
        await message.reply("❌ Ошибка при закрытии Диалога.")
        await state.clear()

@router.callback_query(F.data.startswith("admin_close_"))
async def admin_close_ticket_button(cb: CallbackQuery, state: FSMContext):
    """Handle ticket closure via button."""
    thread_id = int(cb.data.split("_")[2])
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    
    if not user_id:
        await cb.message.reply("❌ Диалог не найден или истёк.")
        await cb.answer()
        return

    try:
        try:
            topic_info = await bot.get_forum_topic_icon_stickers(chat_id=ADMIN_CHAT_ID)
            await bot.close_forum_topic(chat_id=ADMIN_CHAT_ID, message_thread_id=thread_id)
        except TelegramBadRequest as e:
            if "TOPIC_DELETED" in str(e):
                logger.warning(f"Topic {thread_id} already deleted or closed.")
            else:
                raise e

        await bot.send_message(user_id, "✅ Проверка адреса прошла успешно.")
        await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
        await cb.message.reply("✅ Диалог закрыт администратором.")
        # Clear user's FSM state
        await state.clear()
        await cb.answer()
    except TelegramBadRequest as e:
        logger.error(f"Error closing ticket {thread_id}: {e}")
        await cb.message.reply("❌ Ошибка при закрытии Диалога.")
        await cb.answer()
    except Exception as e:
        logger.error(f"Unexpected error closing ticket {thread_id}: {e}")
        await cb.message.reply("❌ Ошибка при закрытии Диалога.")
        await cb.answer()

@router.message(F.chat.id == ADMIN_CHAT_ID, F.message_thread_id)
async def admin_reply_in_topic(message: Message):
    """Handle admin replies in ticket threads."""
    logger.info(
        f"Admin message received: chat_id={message.chat.id}, "
        f"thread_id={message.message_thread_id}, content_type={message.content_type}, "
        f"text={message.text if message.text else 'None'}"
    )
    
    if message.text and message.text.startswith(("/close", "/approve")):
        return

    user_id = await safe_redis_operation(redis_client.get, f"ticket:{message.message_thread_id}")
    if not user_id:
        logger.warning(f"No user_id found for thread_id {message.message_thread_id}")
        await message.reply("❌ Диалог не найден или истёк.")
        return

    try:
        if message.text:
            await bot.send_message(user_id, message.text)
        elif message.photo:
            await bot.send_photo(user_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.document:
            await bot.send_document(user_id, document=message.document.file_id, caption=message.caption)
        elif message.video:
            await bot.send_video(user_id, video=message.video.file_id, caption=message.caption)
        elif message.voice:
            await bot.send_voice(user_id, voice=message.voice.file_id, caption=message.caption)
        elif message.sticker:
            await bot.send_sticker(user_id, sticker=message.sticker.file_id)
        elif message.animation:
            await bot.send_animation(user_id, animation=message.animation.file_id, caption=message.caption)
        else:
            logger.info(f"Unsupported content type {message.content_type} in thread {message.message_thread_id}")
            await message.reply("⚠️ Этот тип сообщения не поддерживается для отправки пользователю.")
            return
        logger.info(f"Message sent to user {user_id} from thread {message.message_thread_id}")
    except TelegramBadRequest as e:
        logger.error(f"Error sending message to user {user_id}: {e}")
        await message.reply("❌ Ошибка при отправке сообщения пользователю. Возможно, Диалог закрыт.")
    except Exception as e:
        logger.error(f"Unexpected error sending message to user {user_id}: {e}")
        await message.reply("❌ Ошибка при отправке сообщения пользователю.")

@router.message(F.chat.id == ADMIN_CHAT_ID, F.text.startswith("/close"))
async def admin_close_ticket_command(message: Message, state: FSMContext):
    """Handle ticket closure via /close command."""
    thread_id = message.message_thread_id
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    
    if not user_id:
        await message.reply("❌ Диалог не найден или истёк.")
        return

    try:
        try:
            topic_info = await bot.get_forum_topic_icon_stickers(chat_id=ADMIN_CHAT_ID)
            await bot.close_forum_topic(chat_id=ADMIN_CHAT_ID, message_thread_id=thread_id)
        except TelegramBadRequest as e:
            if "TOPIC_DELETED" in str(e):
                logger.warning(f"Topic {thread_id} already deleted or closed.")
            else:
                raise e

        await bot.send_message(user_id, "✅ Проверка адреса прошла успешно.")
        await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
        await message.reply("✅ Диалог закрыт администратором.")
        # Clear user's FSM state
        await state.clear()
    except TelegramBadRequest as e:
        logger.error(f"Error closing ticket {thread_id}: {e}")
        await message.reply("❌ Ошибка при закрытии Диалога.")
    except Exception as e:
        logger.error(f"Unexpected error closing ticket {thread_id}: {e}")
        await message.reply("❌ Ошибка при закрытии Диалога.")

@router.message(F.chat.id == ADMIN_CHAT_ID, F.text.startswith("/approve"))
async def approve_address(message: Message, state: FSMContext):
    """Handle address approval via /approve command."""
    thread_id = message.message_thread_id
    user_id = await safe_redis_operation(redis_client.get, f"ticket:{thread_id}")
    
    if not user_id:
        await message.reply("❌ Диалог не найден или истёк.")
        return

    try:
        try:
            topic_info = await bot.get_forum_topic_icon_stickers(chat_id=ADMIN_CHAT_ID)
            await bot.close_forum_topic(chat_id=ADMIN_CHAT_ID, message_thread_id=thread_id)
        except TelegramBadRequest as e:
            if "TOPIC_DELETED" in str(e):
                logger.warning(f"Topic {thread_id} already deleted or closed.")
            else:
                raise e

        await bot.send_message(user_id, "✅ Проверка адреса прошла успешно.")
        await safe_redis_operation(redis_client.delete, f"ticket:{thread_id}")
        await message.reply("✅ Адрес подтверждён и Диалог закрыт администратором.")
        # Clear user's FSM state
        await state.clear()
    except TelegramBadRequest as e:
        logger.error(f"Error approving ticket {thread_id}: {e}")
        await message.reply("❌ Ошибка при подтверждении адреса.")
    except Exception as e:
        logger.error(f"Unexpected error approving ticket {thread_id}: {e}")
        await message.reply("❌ Ошибка при подтверждении адреса.")

@router.message(F.chat.id == ADMIN_CHAT_ID)
async def admin_non_thread_message(message: Message):
    """Handle admin messages sent outside forum threads."""
    logger.warning(
        f"Admin message outside thread: chat_id={message.chat.id}, "
        f"content_type={message.content_type}, text={message.text if message.text else 'None'}"
    )
    await message.reply("⚠️ Пожалуйста, отправляйте сообщения в соответствующий Диалог.")

@router.message()
async def catch_all(message: Message):
    """Catch unhandled messages for debugging."""
    logger.warning(
        f"Unhandled message: chat_id={message.chat.id}, "
        f"thread_id={message.message_thread_id}, "
        f"content_type={message.content_type}, "
        f"text={message.text if message.text else 'None'}"
    )

@router.callback_query()
async def catch_all_callback(cb: CallbackQuery):
    """Catch unhandled callbacks for debugging."""
    logger.warning(
        f"Unhandled callback: chat_id={cb.message.chat.id}, "
        f"thread_id={cb.message.message_thread_id}, "
        f"data={cb.data}"
    )
    try:
        await cb.answer("⚠️ Неизвестное действие.")
    except TelegramBadRequest as e:
        logger.error(f"Error answering unhandled callback: {e}")