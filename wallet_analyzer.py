import asyncio
import pandas as pd
import json
import os
from utils import load_wallets, save_to_excel
from blockchain import analyze_wallet

CACHE_FILE = 'cache.json'
WALLETS_FILE = 'wallets.txt'

def load_cache():
    """Загружает кэш с диска, если файл существует."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    """Сохраняет кэш на диск в формате JSON."""
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, indent=4)

def input_wallets():
    """Позволяет пользователю ввести кошельки вручную и сохраняет их в текстовый файл."""
    print("Введите кошельки, по одному на строке. Для завершения ввода оставьте строку пустой и нажмите Enter.")

    wallets = []

    while True:
        wallet = input("Введите адрес кошелька: ")
        if not wallet:
            break
        wallets.append(wallet)

    if wallets:
        with open(WALLETS_FILE, 'w') as f:
            f.write('\n'.join(wallets))
        print(f"{len(wallets)} кошельков сохранено в {WALLETS_FILE}.")
    else:
        print("Кошельки не введены.")

async def main():
    # Ввод кошельков вручную
    input_wallets()

    # Загрузка кошельков из файла
    wallets = load_wallets(WALLETS_FILE)

    if not wallets:
        print("Список кошельков пуст. Завершение работы.")
        return

    cache = load_cache()

    # Параллельный анализ кошельков
    tasks = [analyze_wallet(wallet, cache) for wallet in wallets]
    results = await asyncio.gather(*tasks)

    # Сохранение результатов в кэш
    save_cache(cache)

    # Создание DataFrame для результатов
    df = pd.DataFrame(results, columns=['Address', 'Transactions', 'Networks', 'Total Fees (in WEI)'])
    print(df)

    # Сохранение результатов в Excel
    save_to_excel(df, 'wallet_analysis.xlsx')

if __name__ == '__main__':
    asyncio.run(main())

