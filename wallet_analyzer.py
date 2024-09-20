import asyncio
import pandas as pd
import json
import os
from utils import load_wallets, save_to_excel
from blockchain import analyze_wallet

CACHE_FILE = 'cache.json'

def load_cache():
    """Загружает кэш с диска, если файл существует."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    """Сохраняет кэш на диск в формате JSON."""
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, indent=4) #Добавляем отступы для удобства читать


async def get_wallets_file_from_user():
    """Асинхронно запрашивает путь к файлу с кошельками у пользователя."""
    while True:
        try:
            # Запрашиваем у пользователя путь к файлу
            filename = await asyncio.to_thread(input, "Введите путь к файлу с адресами кошельков: ")

            # Отладочный вывод для проверки пути
           # print(f"Проверяем путь: '{filename}'")

            # Проверяем, существует ли файл
            if not os.path.exists(filename):
                print(f"Файл '{filename}' не найден. Пожалуйста, проверьте путь и повторите.")
                continue

            # Если файл найден, возвращаем имя файла
           # print(f"Файл найден: {filename}")
            return filename

        except Exception as e:
            print(f"Произошла ошибка: {e}. Попробуйте снова.")


async def main():
    filename = await get_wallets_file_from_user()
    wallets = load_wallets(filename)

    if not wallets:
        print("Список кошельков пуст. Завершение работы.")
        return

    cache = load_cache()

    tasks = [analyze_wallet(wallet, cache) for wallet in wallets]
    results = await asyncio.gather(*tasks)

    save_cache(cache)

    df = pd.DataFrame(results, columns=['Address', 'Transactions', 'Networks', 'Total Fees (in WEI)'])
    print(df)

    save_to_excel(df, 'wallet_analysis.xlsx')

if __name__ == '__main__':
    asyncio.run(main())
