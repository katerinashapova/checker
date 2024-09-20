import asyncio
import time
import random
import logging
from web3 import Web3

from networktest import get_web3_for_network

# Конфигурация логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Максимальное количество попыток подключения
MAX_RETRIES = 5
CACHE_TTL = 60 * 60  # Время жизни кэша в секундах (например, 1 час)
# Кэш с временем жизни
cache = {}


# Функция для проверки актуальности данных в кэше
def is_cache_valid(cache_entry):
    if not cache_entry:
        return False
    timestamp, _ = cache_entry
    return time.time() - timestamp < CACHE_TTL


async def analyze_network(address, network):
    web3 = get_web3_for_network(network)
    total_transactions = 0
    total_gas_fees = 0
    interacted = False

    if web3.is_connected():
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Проверяем, что адрес не является None
                if not address:
                    logging.error(f"Invalid address: {address}")
                    return total_transactions, interacted, total_gas_fees

                # Получаем количество транзакций для кошелька
                transaction_count = await asyncio.to_thread(web3.eth.get_transaction_count, address)
                total_transactions += transaction_count

                if transaction_count > 0:
                    interacted = True
                    latest_block = await asyncio.to_thread(web3.eth.get_block, 'latest', full_transactions=True)

                    for tx in latest_block['transactions']:
                        # Проверяем, что 'from' и 'to' существуют и не None, прежде чем вызывать .lower()
                        if tx.get('from') and address and tx['from'].lower() == address.lower() or \
                           tx.get('to') and address and tx['to'].lower() == address.lower():
                            try:
                                # Получаем саму транзакцию для получения gasPrice
                                transaction = await asyncio.to_thread(web3.eth.get_transaction, tx['hash'])
                                gas_price = transaction.get('gasPrice', 0)

                                # Получаем квитанцию транзакции для получения gasUsed
                                receipt = await asyncio.to_thread(web3.eth.get_transaction_receipt, tx['hash'])
                                gas_used = receipt.get('gasUsed', 0)

                                # Рассчитываем общую стоимость газа
                                if gas_price and gas_used:
                                    total_gas_fees += gas_used * gas_price
                            except Exception as e:
                                logging.error(f"Error processing transaction {tx['hash']} in {network}: {e}")

                break  # Прерываем цикл, если успешно обработали сеть
            except Exception as e:
                retries += 1
                wait_time = random.uniform(1, 3)
                logging.error(f"Error in {network} for {address}: {e}, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

    return total_transactions, interacted, total_gas_fees


# Функция для анализа транзакций кошелька
async def analyze_wallet(wallet_address, cache):

    if wallet_address in cache and is_cache_valid(cache[wallet_address]):
        logging.info(f"Returning cached result for {wallet_address}")
        return cache[wallet_address][1]

    total_transactions = 0
    total_gas_fees = 0
    interacted_networks = set()

    networks = ['Arbitrum', 'Avalanche', 'Base', 'Celo', 'Moonbeam', 'Optimism', 'Polygon', 'Scroll', 'Ethereum']

    # Проверяем, что имена сетей валидны (не пустые)
    valid_networks = [network for network in networks if network and len(network.strip()) > 0]

    # Параллельная обработка сетей
    results = await asyncio.gather(*(analyze_network(wallet_address, network) for network in valid_networks))

    # Обработка результатов
    for network, (transactions, interacted, gas_fees) in zip(valid_networks, results):
        total_transactions += transactions
        total_gas_fees += gas_fees
        if interacted:
            interacted_networks.add(network)

    # Кэшируем результат с текущим временем
    cache[wallet_address] = (time.time(), (wallet_address, total_transactions, len(interacted_networks), total_gas_fees))

    logging.info(f"Wallet {wallet_address} - Total Transactions: {total_transactions}, "
                 f"Networks: {len(interacted_networks)}, Total Gas Fees (Wei): {total_gas_fees}")
    return cache[wallet_address][1]
