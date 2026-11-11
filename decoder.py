import charset_normalizer
import os
import sys
import json


def get_program_folder():
    """Возвращает папку, где находится программа (.exe или .py)"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def find_txt_file(folder_path):
    """Ищет первый .txt файл в указанной папке"""
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]

    # Исключаем служебные файлы
    txt_files = [
        f
        for f in txt_files
        if f.lower() != "requirements.txt"
        and "_readable" not in f
        and "_original_encoding" not in f
    ]

    if not txt_files:
        return None
    return os.path.join(folder_path, txt_files[0])


def detect_and_convert_to_readable(input_path, output_path, encoding_info_path):
    """Определяет кодировку и создаёт читаемую версию файла"""
    with open(input_path, "rb") as f:
        raw_data = f.read()

    detected = charset_normalizer.detect(raw_data)
    original_encoding = detected["encoding"]

    if original_encoding is None:
        print("⚠️ Не удалось определить кодировку, пробуем Windows-1251...")
        original_encoding = "windows-1251"

    print(
        f"📊 Исходная кодировка: {original_encoding} (уверенность: {detected['confidence']:.2%})"
    )

    with open(encoding_info_path, "w", encoding="utf-8") as f:
        json.dump({"encoding": original_encoding}, f, ensure_ascii=False)

    try:
        text_data = raw_data.decode(original_encoding, errors="replace")
    except Exception as e:
        print(f"❌ Ошибка декодирования: {e}")
        return False

    with open(output_path, "w", encoding="utf-8", errors="replace") as f:
        f.write(text_data)

    return True


def convert_back_from_readable(readable_path, original_path, encoding_info_path):
    """Конвертирует отредактированный файл обратно в исходную кодировку"""
    if not os.path.exists(encoding_info_path):
        print("❌ Не найден файл с информацией о кодировке")
        return False

    with open(encoding_info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    original_encoding = info["encoding"]

    with open(readable_path, "r", encoding="utf-8") as f:
        text_data = f.read()

    try:
        raw_data = text_data.encode(original_encoding, errors="replace")
    except Exception as e:
        print(f"❌ Ошибка кодирования: {e}")
        return False

    with open(original_path, "wb") as f:
        f.write(raw_data)

    return True


def main():
    program_folder = get_program_folder()
    print(f"📁 Рабочая папка: {program_folder}")

    encoding_info_path = os.path.join(program_folder, "_original_encoding.json")

    # Режим 1: Поиск и конвертация в читаемый формат
    if not os.path.exists(encoding_info_path):
        print("\n🔍 Режим: Поиск файла для конвертации...")

        original_file = find_txt_file(program_folder)

        if not original_file:
            print("❌ Не найден .txt файл для обработки!")
            print(f"💡 Поместите файл в папку: {program_folder}")
            input("\nНажмите Enter для выхода...")
            return

        print(f"📄 Найден файл: {os.path.basename(original_file)}")

        base_name = os.path.splitext(original_file)[0]
        readable_file = f"{base_name}_readable.txt"

        print("🔄 Конвертирую в читаемый формат...")
        if detect_and_convert_to_readable(
            original_file, readable_file, encoding_info_path
        ):
            print(f"✅ Готово! Создан файл: {os.path.basename(readable_file)}")
            print("\n📝 Отредактируйте файл _readable.txt в Блокноте")
            print("🔄 Затем запустите программу ещё раз для обратной конвертации")
        else:
            print("❌ Ошибка конвертации")

    # Режим 2: Обратная конвертация
    else:
        print("\n🔄 Режим: Обратная конвертация...")

        readable_files = [
            f for f in os.listdir(program_folder) if f.endswith("_readable.txt")
        ]

        if not readable_files:
            print("❌ Не найден файл *_readable.txt для обратной конвертации!")
            os.remove(encoding_info_path)
            input("\nНажмите Enter для выхода...")
            return

        readable_path = os.path.join(program_folder, readable_files[0])
        original_filename = readable_files[0].replace("_readable.txt", ".txt")
        original_path = os.path.join(program_folder, original_filename)

        if not os.path.exists(original_path):
            print(f"❌ Не найден исходный файл: {original_filename}")
            input("\nНажмите Enter для выхода...")
            return

        print(f"📄 Обрабатываю: {readable_files[0]}")

        if convert_back_from_readable(readable_path, original_path, encoding_info_path):
            print(f"✅ Готово! Файл {original_filename} обновлён")
            os.remove(readable_path)
            os.remove(encoding_info_path)
            print("✨ Всё готово!")
        else:
            print("❌ Ошибка обратной конвертации")

    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
