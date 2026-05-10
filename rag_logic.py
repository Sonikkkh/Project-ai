import os

# 1. ФУНКЦІЯ ЗБЕРЕЖЕННЯ (Тепер для кожного свій файл)
def save_user_note(text, user_id):
    filename = f"notes_{user_id}.txt"  # Наприклад: notes_123456.txt
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{text}\n\n---\n\n")
    return "✅ Нотатку збережено у твою ОСОБИСТУ бібліотеку!"

# 2. ФУНКЦІЯ ПОШУКУ ТА СПИСКУ
def get_answer(user_question, user_id):
    filename = f"notes_{user_id}.txt"
    
    if not os.path.exists(filename):
        return "📂 Твоя особиста бібліотека ще порожня."

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        search_term = user_question.lower().strip()

        # Якщо натиснуто "Моя бібліотека"
        if search_term == "список":
            return f"📚 **Твої особисті записи:**\n\n{content}"

        # Пошук конкретного слова/героя
        raw_blocks = content.split("#")
        blocks = ["#" + b.strip() for b in raw_blocks if b.strip()]
        found_blocks = [b for b in blocks if search_term in b.lower()]
        
        if found_blocks:
            result = "\n\n---\n\n".join(found_blocks)
            return f"🔍 **Знайдено у твоїх записах:**\n\n{result}"
        
        return f"🔍 У твоїй бібліотеці нічого не знайдено за запитом '{user_question}'."
    except Exception as e:
        return f"❌ Помилка: {e}"

def delete_note(target, user_id):
    filename = f"notes_{user_id}.txt"
    if not os.path.exists(filename):
        return "❌ Твоя бібліотека порожня."
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Розбиваємо весь текст на окремі блоки (нотатки)
        # Використовуємо наш роздільник "---"
        blocks = content.split("---")
        
        # 2. Фільтруємо блоки: залишаємо тільки ті, де НЕМАЄ назви, яку ми видаляємо
        # strip() прибирає зайві пробіли та порожні рядки
        new_blocks = [b.strip() for b in blocks if target.lower() not in b.lower() and b.strip()]
        
        if len(blocks) - 1 == len(new_blocks): # -1 бо останній елемент після split часто порожній
            return f"❓ Запис '{target}' не знайдено."
        
        # 3. Збираємо блоки назад у текст із роздільниками
        if new_blocks:
            new_content = "\n\n".join(new_blocks) + "\n\n---\n\n"
        else:
            new_content = "" # Якщо видалили останню книгу
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return f"🗑️ Весь запис про '{target}' (назва, герой та події) повністю видалено!"
        
    except Exception as e:
        return f"❌ Помилка при видаленні: {e}"