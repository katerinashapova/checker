import pandas as pd
import os

# Функция для чтения файла с кошельками
def load_wallets(filename):
    """Читает файл с кошельками, возвращает список адресов."""
    try:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден.")

        with open(filename, 'r') as file:
            wallets = file.read().splitlines()

        # Проверяем, что список кошельков не пустой
        if not wallets:
            raise ValueError("Файл не содержит кошельков или пуст.")

        return wallets

    except Exception as e:
        print(f"Ошибка при загрузке файла с кошельками: {e}")
        return []

# Функция для сохранения данных в Excel файл
def save_to_excel(df, filename):
    """Сохраняет DataFrame в Excel файл."""
    try:
        # Сохраняем DataFrame в Excel файл
        df.to_excel(filename, index=False)
        print(f"Данные успешно сохранены в {filename}.")

    except PermissionError:
        print(f"Ошибка доступа: возможно файл {filename} уже открыт. Закройте файл и попробуйте снова.")

    except Exception as e:
        print(f"Произошла ошибка при сохранении в Excel: {e}")