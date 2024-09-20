from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import random
import time

# Кэш для хранения Web3-соединений
web3_cache = {}
CACHE_TTL = 60 * 60  # Время жизни кэша (1 час)

# Список RPC URL для сетей
network_rpc_urls = {
    'Arbitrum': [
        'https://arb1.arbitrum.io/rpc',  # Обновленный RPC URL
        'https://lb.drpc.org/ogrpc?network=arbitrum&dkey=ApebS0e7I0vdmKtIA4siKewRl9RQbqIR773sUh7cII5S'
    ],
    'Avalanche': [
        'https://avax.meowrpc.com',  # Обновленный RPC URL
        'https://lb.drpc.org/ogrpc?network=avalanche&dkey=ApebS0e7I0vdmKtIA4siKewRl9RQbqIR773sUh7cII5S'
    ],
    'Base': [
        'https://base-mainnet.infura.io/v3/b83fade9f8c349ddb549c664c6929fc3',
        'https://lb.drpc.org/ogrpc?network=base&dkey=ApebS0e7I0vdmKtIA4siKewRl9RQbqIR773sUh7cII5S',
        'https://base.llamarpc.com'
    ],
    'Celo': [
        'https://forno.celo.org',  # Обновленный RPC URL
        'https://celo-mainnet.infura.io/v3/b83fade9f8c349ddb549c664c6929fc3'
    ],
    'Moonbeam': [
        'https://rpc.api.moonbeam.network',  # Обновленный RPC URL
        'https://api-moonbeam.moonscan.io/87KIVXU2TAEXPES95K8R7VDENVGVSIQNA7'
    ],
    'Optimism': [
        'https://optimism.llamarpc.com',  # Обновленный RPC URL
        'https://api-optimistic.etherscan.io/api/GFBDEJXEE9PTZC9XD6WNWFJPNYYWMBGWFK'
    ],
    'Polygon': [
        'https://polygon.llamarpc.com',  # Обновленный RPC URL
        'https://polygon-mainnet.infura.io/v3/b83fade9f8c349ddb549c664c6929fc3'
    ],
    'Scroll': [
        'https://1rpc.io/scroll',
        'https://lb.drpc.org/ogrpc?network=scroll&dkey=ApebS0e7I0vdmKtIA4siKewRl9RQbqIR773sUh7cII5S'  # Обновленный RPC URL
    ],
    'Ethereum': [
        'https://mainnet.infura.io/v3/b83fade9f8c349ddb549c664c6929fc3',
        'https://eth-rpc.gateway.pokt.network'
    ]
}

def cleanup_cache():
    """Очистка устаревших записей в кэше."""
    current_time = time.time()
    keys_to_delete = [key for key, (timestamp, _) in web3_cache.items() if current_time - timestamp > CACHE_TTL]
    for key in keys_to_delete:
        del web3_cache[key]

# Функция для получения Web3 с ротацией URL и несколькими попытками подключения
def get_web3_with_rotation(network_name, max_retries=3, retry_delay=5):
    """Получение Web3 соединения с ротацией URL для сети и повторными попытками."""
    urls = network_rpc_urls.get(network_name, [])
    if not urls:
        raise ValueError(f"No RPC URLs available for network {network_name}")

    random.shuffle(urls)  # Перемешиваем список URL для случайной ротации

    for retry in range(max_retries):
        for url in urls:
            try:
                web3 = Web3(Web3.HTTPProvider(url, {"timeout": 30}))  # Увеличен тайм-аут до 30 секунд
                if web3.is_connected():
                    print(f"Successfully connected to {network_name} via {url}")

                    if network_name in ['Scroll', 'Celo', 'Moonbeam', 'Polygon', 'Avalanche']:#  чтобы правильно обрабатывать блоки в РОА
                        web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                        print(f"Injected POA middleware for {network_name}")

                    return web3
                else:
                    print(f"Failed to connect to {network_name} via {url}, trying another URL...")
            except Exception as e:
                print(f"Error connecting to {network_name} via {url}: {e}")
        print(f"Retrying connection to {network_name} in {retry_delay} seconds...")
        time.sleep(retry_delay)

    raise ConnectionError(f"Failed to connect to {network_name} after {max_retries} retries.")

def get_web3_for_network(network_name):
    """Получение Web3 соединения с кэшированием для сети."""
    cleanup_cache()  # Очистка устаревших записей перед новым подключением
    if network_name in web3_cache:
        return web3_cache[network_name][1]

    web3 = get_web3_with_rotation(network_name)

    web3_cache[network_name] = (time.time(), web3)
    return web3
