import os
import time
import threading
import pyfiglet
import requests

from colorama import init, Fore, Style

def calculate_image_size(image_path):
    if os.path.exists(image_path):
        return os.path.getsize(image_path)
    else:
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")

def init_upload(image_path, cookies, headers, session):
    total_bytes = calculate_image_size(image_path)
    data = {
        'command': 'INIT',
        'total_bytes': total_bytes,
        'media_type': 'image/png',
        'media_category': 'tweet_image',
    }

    headers = headers.copy()
    headers.pop('content-type', None)

    response = session.post(
        'https://upload.twitter.com/i/media/upload.json',
        data=data,
        cookies=cookies,
        headers=headers
    )

    if response.status_code == 202:
        media_id = response.json().get("media_id_string")
        return media_id
    else:
        print(f"{Fore.RED}Erro ao inicializar upload")
        raise Exception("Falha ao inicializar o upload.")

def append_upload(image_path, media_id, cookies, headers, session):
    chunk_size = 5 * 1024 * 1024
    segment_index = 0

    headers = headers.copy()
    headers.pop('content-type', None)

    try:
        with open(image_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break

                data = {
                    'command': 'APPEND',
                    'media_id': media_id,
                    'segment_index': str(segment_index),
                }

                files = {
                    'media': chunk,
                }

                response = session.post(
                    'https://upload.twitter.com/i/media/upload.json',
                    data=data,
                    files=files,
                    cookies=cookies,
                    headers=headers
                )

                if response.status_code != 204:
                    print(f"{Fore.RED}Erro no envio do segmento")
                    raise Exception("Falha ao enviar segmento da imagem.")

                segment_index += 1
    except Exception as e:
        print(f"{Fore.RED}Erro no processo de append: {e}")
        raise

def finalize_upload(media_id, cookies, headers, session):
    data = {
        'command': 'FINALIZE',
        'media_id': media_id,
    }

    headers = headers.copy()
    headers.pop('content-type', None)

    response = session.post(
        'https://upload.twitter.com/i/media/upload.json',
        data=data,
        cookies=cookies,
        headers=headers
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"{Fore.RED}Erro ao finalizar o upload")
        raise Exception("Falha ao finalizar o upload.")

def upload_image_to_twitter(image_path, cookies, headers, session):
    try:
        media_id = init_upload(image_path, cookies, headers, session)
        append_upload(image_path, media_id, cookies, headers, session)
        finalize_upload(media_id, cookies, headers, session)
        return media_id
    except Exception as e:
        print(f"{Fore.RED}Erro no processo de upload: {e}")
        raise

def create_tweet(headers, cookies, tweet_text, session, media_id=None, query_id="znq7jUAqRjmPj7IszLem5Q"):
    json_data = {
        'variables': {
            'tweet_text': tweet_text,
            'dark_request': False,
            'media': {
                'media_entities': [
                    {
                        'media_id': media_id,
                        'tagged_users': [],
                    },
                ] if media_id else [],
                'possibly_sensitive': False,
            },
            'semantic_annotation_ids': [],
            'disallowed_reply_options': None,
        },
        'features': {
            'communities_web_enable_tweet_community_results_fetch': True,
            'c9s_tweet_anatomy_moderator_badge_enabled': True,
            'responsive_web_edit_tweet_api_enabled': True,
            'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
            'view_counts_everywhere_api_enabled': True,
            'longform_notetweets_consumption_enabled': True,
            'responsive_web_twitter_article_tweet_consumption_enabled': True,
            'tweet_awards_web_tipping_enabled': False,
            'creator_subscriptions_quote_tweet_preview_enabled': False,
            'longform_notetweets_rich_text_read_enabled': True,
            'longform_notetweets_inline_media_enabled': True,
            'articles_preview_enabled': True,
            'rweb_video_timestamps_enabled': True,
            'rweb_tipjar_consumption_enabled': True,
            'responsive_web_graphql_exclude_directive_enabled': True,
            'verified_phone_label_enabled': False,
            'freedom_of_speech_not_reach_fetch_enabled': True,
            'standardized_nudges_misinfo': True,
            'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
            'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
            'responsive_web_graphql_timeline_navigation_enabled': True,
            'responsive_web_enhance_cards_enabled': False,
        },
        'queryId': query_id,
    }

    response = session.post(
        f'https://twitter.com/i/api/graphql/{query_id}/CreateTweet',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    if response.status_code == 200:
        response_json = response.json()
        if 'errors' in response_json:
            raise Exception(f"Erro ao criar tweet: {response_json['errors']}")
        else:
            return response_json
    else:
        raise Exception(f"Erro ao criar tweet")

def parse_accounts(file_path):
    accounts = []
    with open(file_path, 'r') as f:
        account = {}
        for line in f:
            line = line.strip()
            if not line:
                if account:
                    account['post_count'] = 0
                    accounts.append(account)
                    account = {}
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                account[key.strip()] = value.strip()
        if account:
            account['post_count'] = 0
            accounts.append(account)
    return accounts

def read_tweet_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tweet_text = f.read()
    return tweet_text.strip()

def setup_cookies_and_headers(account):
    base_cookies = {
        'night_mode': '2',
        'gt': '1858043732555149419',
        'd_prefs': 'MToxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw',
        'guest_id_ads': 'v1%3A173182711905967520',
        'guest_id_marketing': 'v1%3A173182711905967520',
        'kdt': 'iO1ufRPqKfYbENI9rlqh6HWgguGCGsogyLCiuYPM',
        'lang': 'en',
        'dnt': '1',
        'guest_id': 'v1%3A173182724725236173',
        'att': '1-lbNfZS9YUlVbacVBY3FdEQuTlKl5hfeI1QrwWNuF',
        'twid': 'u%3D1853385436586246144',
        'personalization_id': '"v1_ossf5umwK3OPp9K9KYHCDA=="',
    }
    base_headers = {
        'accept': '*/*',
        'accept-language': 'pt-BR,pt;q=0.9',
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'content-type': 'application/json',
        'origin': 'https://x.com',
        'priority': 'u=1, i',
        'referer': 'https://x.com/compose/post',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
        'x-client-transaction-id': '9u44LS/6Gvu6l7tPmyuKEi4jFQLiSlLCEXGQOnoXaPHluL/2bp8yPoqVUPQLoZ3SI8bCHPTNBVEBeHND0paQ2Fy7koSW9Q',
        'x-client-uuid': 'f001b4c7-60a0-4579-b94a-fef47d136795',
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en'
    }
    cookies = base_cookies.copy()
    headers = base_headers.copy()
    cookies['ct0'] = account['CT0']
    cookies['auth_token'] = account['AUTH_TOKEN']
    headers['x-csrf-token'] = account['CT0']
    return cookies, headers

def check_accounts(accounts, image_path, proxies_list):
    valid_accounts = []
    proxy_index = [0]
    lock = threading.Lock()
    threads = []
    max_threads = 10
    semaphore = threading.Semaphore(max_threads)

    print(f"{Fore.CYAN}Verificando contas...")

    def process_account(account):
        with semaphore:
            session = requests.Session()

            with lock:
                if proxy_index[0] < len(proxies_list):
                    proxy = proxies_list[proxy_index[0]]
                    proxy_index[0] += 1
                else:
                    proxy = None

            if proxy:
                session.proxies = {'http': proxy, 'https': proxy}

            cookies, headers = setup_cookies_and_headers(account)

            try:

                media_id = init_upload(image_path, cookies, headers, session)
                print(f"{Fore.GREEN}Conta {account.get('login', 'Unknown')} válida.")
                with lock:
                    valid_accounts.append(account)
            except Exception as e:
                print(f"{Fore.RED}Conta {account.get('login', 'Unknown')} inválida: {e}")

    for account in accounts:
        t = threading.Thread(target=process_account, args=(account,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return valid_accounts

def posting_thread(account, accounts, lock, delay, image_path, tweet_text, proxy, post_lock, last_post_time,
                   delay_between_threads, ready_threads_count, ready_threads_lock, start_delay_event, total_threads):
    session = requests.Session()
    if proxy:
        session.proxies = {'http': proxy, 'https': proxy}

    last_own_post_time = None
    first_post_done = False

    while True:
        try:
            if last_own_post_time is not None:
                time_since_last_own_post = time.time() - last_own_post_time
                if time_since_last_own_post < delay:
                    wait_time = delay - time_since_last_own_post
                    print(f"{Fore.BLUE}[{account['login']}] Aguardando {wait_time:.2f}s devido ao delay da thread.")
                    time.sleep(wait_time)

            if start_delay_event.is_set():
                with post_lock:
                    if last_post_time[0] is not None:
                        time_since_last_post = time.time() - last_post_time[0]
                        if time_since_last_post < delay_between_threads:
                            wait_time = delay_between_threads - time_since_last_post
                            print(f"{Fore.BLUE}[{account['login']}] Aguardando {wait_time:.2f}s devido ao delay entre threads.")
                            time.sleep(wait_time)

                    print(f"{Fore.CYAN}[{account['login']}] Tentando postar tweet...")

                    cookies, headers = setup_cookies_and_headers(account)
                    if image_path:
                        media_id = upload_image_to_twitter(image_path, cookies, headers, session)
                    else:
                        media_id = None

                    account['post_count'] += 1
                    tweet_text_with_counter = f"{tweet_text} {account['post_count']}"

                    response = create_tweet(headers, cookies, tweet_text_with_counter, session, media_id)
                    print(f"{Fore.GREEN}[{account['login']}] Tweet número {account['post_count']} postado com sucesso!")
                    current_time = time.time()
                    last_post_time[0] = current_time
                    last_own_post_time = current_time
            else:
                print(f"{Fore.CYAN}[{account['login']}] Tentando postar tweet (sem delay entre threads)...")

                cookies, headers = setup_cookies_and_headers(account)
                if image_path:
                    media_id = upload_image_to_twitter(image_path, cookies, headers, session)
                else:
                    media_id = None

                account['post_count'] += 1
                tweet_text_with_counter = f"{tweet_text} {account['post_count']}"

                response = create_tweet(headers, cookies, tweet_text_with_counter, session, media_id)
                print(f"{Fore.GREEN}[{account['login']}] Tweet número {account['post_count']} postado com sucesso!")
                last_own_post_time = time.time()

                if not first_post_done:
                    first_post_done = True
                    with ready_threads_lock:
                        ready_threads_count[0] += 1
                        if ready_threads_count[0] >= total_threads:
                            start_delay_event.set()

            if account['post_count'] % 5 == 0:
                try:
                    print(f"{Fore.YELLOW}[{account['login']}] Realizando checagem da conta após {account['post_count']} tweets...")
                    test_media_id = init_upload(image_path, cookies, headers, session)
                    print(f"{Fore.GREEN}[{account['login']}] Checagem bem-sucedida.")
                except Exception as e:
                    print(f"{Fore.RED}[{account['login']}] Checagem falhou: {e}")
                    with lock:
                        if accounts:
                            account = accounts.pop(0)
                            print(f"{Fore.YELLOW}Thread pegou uma nova conta: {account['login']}")
                            last_own_post_time = None
                            first_post_done = False
                        else:
                            print(f"{Fore.RED}Sem mais contas disponíveis. Thread encerrando.")
                            break

        except Exception as e:
            print(f"{Fore.RED}[{account['login']}] Erro ao postar tweet: {e}")
            with lock:
                if accounts:
                    account = accounts.pop(0)
                    print(f"{Fore.YELLOW}Thread pegou uma nova conta: {account['login']}")
                    last_own_post_time = None
                    first_post_done = False
                else:
                    print(f"{Fore.RED}Sem mais contas disponíveis. Thread encerrando.")
                    break

def main(accounts_file, tweet_text_file, image_path=None):
    accounts = parse_accounts(accounts_file)
    tweet_text = read_tweet_text(tweet_text_file)

    init(autoreset=True)
    ascii_banner = pyfiglet.figlet_format("HAHAHAHA")
    print(Fore.MAGENTA + ascii_banner)

    proxies_list = [

    ]

    accounts = check_accounts(accounts, image_path, proxies_list)

    if not accounts:
        print(f"{Fore.RED}Nenhuma conta válida encontrada. Encerrando o programa.")
        return

    with open(accounts_file, 'w') as f:
        for account in accounts:
            for key, value in account.items():
                if key != 'post_count':
                    f.write(f"{key}: {value}\n")
            f.write("\n")
    print(f"{Fore.GREEN}Contas válidas salvas em '{accounts_file}'.")

    try:
        quant_contas = int(input("Digite a quantidade de contas: "))
        delay_input = input("Digite os delays entre as postagens para cada thread (em segundos, separados por vírgula): ")
        delays = [float(d.strip()) for d in delay_input.split(',')]
        if len(delays) < quant_contas:
            print(f"Você forneceu menos delays ({len(delays)}) do que o número de contas ({quant_contas}). Usando o último delay para as threads restantes.")
            delays.extend([delays[-1]] * (quant_contas - len(delays)))
        elif len(delays) > quant_contas:
            print(f"Você forneceu mais delays ({len(delays)}) do que o número de contas ({quant_contas}). Ignorando delays extras.")
            delays = delays[:quant_contas]

        delay_between_threads = float(input("Digite o delay entre as threads (em segundos): "))

    except ValueError:
        print("Entrada inválida para delays. Usando atraso padrão de 3 segundos para todas as threads.")
        delays = [3.0] * quant_contas
        delay_between_threads = 1.0

    if quant_contas > len(accounts):
        print(f"Há menos contas ({len(accounts)}) do que o número de contas especificado ({quant_contas}). Usando {len(accounts)} contas.")
        quant_contas = len(accounts)

    if quant_contas > len(proxies_list):
        print(f"Há menos proxies ({len(proxies_list)}) do que o número de contas especificado ({quant_contas}). Algumas threads não usarão proxy.")
        proxies_list.extend([None] * (quant_contas - len(proxies_list)))

    accounts_lock = threading.Lock()
    post_lock = threading.Lock()
    last_post_time = [None]

    ready_threads_count = [0]
    ready_threads_lock = threading.Lock()
    start_delay_event = threading.Event()

    threads = []
    for i in range(quant_contas):
        with accounts_lock:
            account = accounts.pop(0)
        delay = delays[i]
        proxy = proxies_list[i]
        t = threading.Thread(target=posting_thread, args=(
            account, accounts, accounts_lock, delay, image_path, tweet_text, proxy,
            post_lock, last_post_time, delay_between_threads,
            ready_threads_count, ready_threads_lock, start_delay_event, quant_contas))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    accounts_file = 'contas.txt'
    tweet_text_file = 'tweet.txt'
    image_path = 'image.png'

    main(accounts_file, tweet_text_file, image_path)
