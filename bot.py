import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Імпортуємо наші функції з rag_logic
from rag_logic import get_answer, save_user_note, delete_note

load_dotenv()
TOKEN = "8176782015:AAHCqv2s8wV8YTeiw7WBd7AbzUOxkNPd660"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class BookForm(StatesGroup):
    name = State()     # Очікуємо назву
    hero = State()     # Очікуємо героя
    events = State()   # Очікуємо події


# Команда /start з кнопками
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="➕ Додати нову книгу", callback_data="help_newbook"))
    builder.row(types.InlineKeyboardButton(text="📚 Моя бібліотека", callback_data="help_library"))
    builder.row(types.InlineKeyboardButton(text="🔍 Пошук по базі", callback_data="help_search"))
    builder.row(types.InlineKeyboardButton(text="❌ Скасувати поточну дію", callback_data="cancel_action"))


    text = (
        "Вітаю у твоїй цифровій бібліотеці! 📖\n"
        "Я допоможу зробити твоє читання комфортнішим 🎀\n\n"
        "✨ **Поради:**\n"
        "📝**Як додавати:** Просто запиши все потрібне\n"
        "🔍 **Як шукати:** Просто напиши назву або ім'я героя.\n"
        "🗑️ **Як видалити:** Напиши `/delete Назва`"
    )
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "help_newbook")
async def newbook_callback(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_action"))
    await callback.message.answer("📖 Введіть назву книги:")
    await state.set_state(BookForm.name)
    await callback.answer()

@dp.message(BookForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.answer(f"👤 Хто головний герой у '{message.text}'?")
    await state.set_state(BookForm.hero)

@dp.message(BookForm.hero)
async def process_hero(message: types.Message, state: FSMContext):
    await state.update_data(hero_name=message.text)
    await message.answer("✨ Опиши ключові події:")
    await state.set_state(BookForm.events)

@dp.message(BookForm.events)
async def process_events(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    full_note = (
        f"# КНИГА: {user_data['book_name']}\n"
        f"👤 ГЕРОЙ: {user_data['hero_name']}\n"
        f"📝 ПОДІЇ: {message.text}"
    )
    
    # ПЕРЕДАЄМО message.from_user.id
    save_user_note(full_note, message.from_user.id)
    
    await message.answer("✅ Збережено у твою приватну базу!")
    await state.clear()

# --- ЛОГІКА ОСОБИСТОГО ПЕРЕГЛЯДУ ТА ПОШУКУ ---

@dp.callback_query(F.data == "help_library")
async def library_callback(callback: types.CallbackQuery):
    try:
        await bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")
        response = get_answer("список", callback.from_user.id)
        await callback.message.answer(response)
    except Exception:
        # Замість Python Traceback виводимо дружній текст 
        await callback.message.answer("Вибачте, сервери тимчасово перевантажені, спробуйте за хвилину. 😊")
    await callback.answer()

@dp.callback_query(F.data == "help_search")
async def search_callback(callback: types.CallbackQuery):
    await callback.message.answer("🔍 Напиши назву або ім'я героя для пошуку у твоїх записах:")
    await callback.answer()

@dp.message(Command("delete"))
async def delete_handler(message: types.Message):
    target = message.text.replace("/delete", "").strip()
    if not target:
        await message.answer("⚠️ Напиши назву. Приклад: `/delete Елла`")
        return
    # ПЕРЕДАЄМО ID користувача
    result = delete_note(target, message.from_user.id)
    await message.answer(result)

@dp.callback_query(F.data == "cancel_action")
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear() # Очищення стану (скидання контексту) 
    await callback.message.edit_text("❌ Дію скасовано. Можете починати спочатку.")
    await callback.answer()

@dp.message()
async def message_handler(message: types.Message):
    # 1. ВАЛІДАЦІЯ: Перевіряємо, чи це текст
    if message.text and len(message.text) > 1000:
        await message.answer("⚠️ Ой! Твій текст занадто довгий. Будь ласка, надішли коротший запит (до 1000 символів), щоб я міг його опрацювати.")
        return
    if not message.text:
        await message.answer("⚠️ Будь ласка, надішліть текстове повідомлення.")
        return

    try:
        # 2. LATENCY: Візуальний зворотний зв'язок "Бот друкує..."
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # 3. ПОШУК: Тільки після того, як увімкнули статус "друкує", викликаємо логіку
        answer = get_answer(message.text, message.from_user.id)
        
        # 4. ВІДПОВІДЬ
        await message.answer(answer)
        
    except Exception as e:
        # 5. GRACEFUL DEGRADATION: Дружня помилка замість коду
        await message.answer("Вибачте, сервери часом перевантажені, спробуйте за хвилину. 😊")

async def main():
    print("🚀 Бот запущено! Тепер бібліотеки приватні.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())