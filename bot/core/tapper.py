import asyncio
from datetime import datetime
from time import time
from urllib.parse import unquote, quote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw import functions
from pyrogram.raw.functions.messages import RequestWebView
from bot.core.agents import generate_random_user_agent
from bot.config import settings

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers

from random import randint


class Tapper:
    def __init__(self, tg_client: Client):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.user_id = 0
        self.country = 'US'
        self.locale = 'en'
        self.headers = ''

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                    if settings.USE_REF:
                        peer = await self.tg_client.resolve_peer('trust_empire_bot')
                        await self.tg_client.invoke(
                            functions.messages.StartBot(
                                bot=peer,
                                peer=peer,
                                start_param=get_link_code(),
                                random_id=randint(1, 9999999),
                            )
                        )

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('trust_empire_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | FloodWait {fl}")
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url="https://trstempire.com/",
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = tg_web_data.split('query_id=')[1].split('&user=')[0]
            user = quote(tg_web_data.split("&user=")[1].split('&auth_date=')[0])
            auth_date = tg_web_data.split('&auth_date=')[1].split('&hash=')[0]
            user_name = tg_web_data.split('"username":"')[1].split('","')[0] if "username" in tg_web_data else ''
            first_name = tg_web_data.split('"first_name":"')[1].split('","')[0]
            hash_ = tg_web_data.split('&hash=')[1]
            self.locale = tg_web_data.split('"language_code":"')[1][:2]
            self.user_id = int(tg_web_data.split('"id":')[1].split(',"')[0])
            self.headers = f'query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}'

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return (f"query_id={query_id}&hash={hash_}&language_code={self.locale}&locale={self.locale}&"
                    f"user_id={self.user_id }&username={user_name}&first_name={first_name}")

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: "
                         f"{error}")
            await asyncio.sleep(delay=3)

    async def get_info_data(self, http_client: aiohttp.ClientSession, init_params: str):
        try:
            response = await http_client.get(f'https://new.trstempire.com/api/v1/join?{init_params}')
            response.raise_for_status()

            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting user data: {error}")
            await asyncio.sleep(delay=randint(3, 7))

    async def get_rewards(self, http_client: aiohttp.ClientSession):
        try:
            params = 'user_id=' + str(self.user_id) + '&locale=' + self.locale
            response = await http_client.get(f'https://new.trstempire.com/api/v1/rewards?{params}')
            response.raise_for_status()

            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting rewards data: {error}")
            await asyncio.sleep(delay=randint(3, 7))

    async def get_level_reward(self, http_client: aiohttp.ClientSession, level: int):
        try:
            json_data = {
                'user_id': self.user_id,
                'level': level
            }
            response = await http_client.post(f'https://new.trstempire.com/api/v1/tasks/complete-level-up',
                                              json=json_data)
            response.raise_for_status()
            return True

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting level reward: {error}")
            await asyncio.sleep(delay=randint(3, 7))
            return False

    async def get_notifications(self, http_client: aiohttp.ClientSession):
        try:
            params = 'user_id=' + str(self.user_id)
            response = await http_client.get(f'https://new.trstempire.com/api/v1/notifications/get-pending?{params}')
            response.raise_for_status()

            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting notifications: {error}")
            await asyncio.sleep(delay=randint(3, 7))

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://ipinfo.io/ip', timeout=aiohttp.ClientTimeout(10))
            ip = (await response.text())
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def join_tg_channel(self, link: str):
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"{self.session_name} | Error while TG connecting: {error}")

        try:
            parsedLink = link if 'https://t.me/+' in link else link[13:]
            chat = await self.tg_client.get_chat(parsedLink)
            logger.info(f"{self.session_name} | Get channel: <y>{chat.username}</y>")
            try:
                await self.tg_client.get_chat_member(chat.username, "me")
            except Exception as error:
                if error.ID == 'USER_NOT_PARTICIPANT':
                    logger.info(f"{self.session_name} | User not participant of the TG group: <y>{chat.username}</y>")
                    await asyncio.sleep(delay=3)
                    response = await self.tg_client.join_chat(parsedLink)
                    logger.info(f"{self.session_name} | Joined to channel: <y>{response.username}</y>")
                else:
                    logger.error(f"{self.session_name} | Error while checking TG group: <y>{chat.username}</y>")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
        except Exception as error:
            logger.error(f"{self.session_name} | Error while join tg channel: {error}")

    async def set_country_code(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url='https://ipinfo.io/json', timeout=aiohttp.ClientTimeout(5))
            response_json = await response.json()
            self.country = response_json['country']

            payload = {
                'user_id': self.user_id,
                'country': self.country
            }
            http_client.headers['X-Requested-With'] = 'XMLHttpRequest'
            response = await http_client.post(url='https://new.trstempire.com/api/set_country', json=payload)
            response_json = await response.json()
            if response_json.get('success'):
                logger.success(f"{self.session_name} | Country is set | Current country: {self.country}")
        except Exception as error:
            logger.error(f"{self.session_name} | Error while setting country code: {error}")

    async def claim_daily(self, http_client: aiohttp.ClientSession, tasks: list[dict[str, str]]):
        try:
            current_task = None
            for task in tasks:
                if task['isCurrentDay']:
                    current_task = task

            if not current_task.get('isCompleted'):
                json_data = {
                    'user_id': self.user_id,
                    'task_id': current_task['_id']
                }
                response = await http_client.post(f'https://new.trstempire.com/api/v1/tasks/complete', json=json_data)
                response.raise_for_status()
                response_json = await response.json()

                if response_json.get('active'):
                    logger.success(
                        f"{self.session_name} | Daily Claimed! | Reward: <e>{response_json['reward']}</e> |"
                        f" Day count: <g>{response_json['day']}</g>")

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when Daily Claiming: {error}")
            await asyncio.sleep(delay=3)

    async def processing_tasks(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get('https://new.trstempire.com/api/v1/tasks/grouped')
            response.raise_for_status()
            tasks_json = await response.json()

            daily_tasks = tasks_json['dailyTasks']['tasks']
            fortune_task = tasks_json['fortuneSpinTask']
            tasks = tasks_json['trustTasks'] + tasks_json['partnerTasks']

            await self.claim_daily(http_client=http_client, tasks=daily_tasks)
            await asyncio.sleep(delay=3)
            fortune_claim_time = fortune_task['nextSpin']
            parsed_time = datetime.strptime(fortune_claim_time, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
            delta_time = parsed_time - datetime.utcnow().timestamp()
            if delta_time < 0:
                await self.claim_fortune_reward(http_client=http_client, task_id=fortune_task['_id'])
                await asyncio.sleep(delay=3)

            if settings.AUTO_TASK:
                for task in tasks:
                    title = task['task_data']['title'].split('<br>')[0]
                    if task['type'] == 'boost_tg_channel':
                        continue
                    if task['type'] != "internal" and task['active'] and not task['completed']:
                        if task['type'] != 'tg_subscription':
                            logger.info(f"{self.session_name} | Performing task <lc>{title}</lc>...")
                            response_data = await self.perform_task(http_client=http_client, task_id=task['_id'])
                            if response_data:
                                logger.success(f"{self.session_name} | Task <lc>{title}</lc>"
                                               f" completed! | Reward: <e>+{task['reward']}</e> points")

                            await asyncio.sleep(delay=randint(5, 10))
                        elif settings.JOIN_CHANNELS:
                            logger.info(f"{self.session_name} | Performing TG <lc>{title}</lc>...")
                            await self.join_tg_channel(task['url'])
                            response_data = await self.perform_tg_task(http_client=http_client, task_id=task['_id'])
                            if response_data:
                                logger.success(f"{self.session_name} | Task <lc>{title}</lc>"
                                               f" completed! | Reward: <e>+{task['reward']}</e> points")

                            await asyncio.sleep(delay=randint(5, 10))

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when completing tasks: {error}")
            await asyncio.sleep(delay=3)

    async def claim_fortune_reward(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            reward = settings.FORTUNE_REWARDS[randint(0, len(settings.FORTUNE_REWARDS) - 1)]
            json_data = {
                'user_id': self.user_id,
                'task_id': task_id,
                'reward': reward
            }
            response = await http_client.post(f'https://new.trstempire.com/api/v1/tasks/complete', json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            if response_json.get('active'):
                logger.success(f"{self.session_name} | Fortune reward claimed! | Got: <e>{reward}</e>")

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming fortune reward: {error}")
            await asyncio.sleep(delay=3)

    async def perform_task(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            payload = {
                "user_id": self.user_id,
                "task_id": task_id
            }
            response = await http_client.post(url='https://new.trstempire.com/api/v1/tasks/complete', json=payload)
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while check in task {task_id} | Error: {e}")
            await asyncio.sleep(delay=3)

    async def perform_tg_task(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            payload = {
                "user_id": self.user_id,
                "task_id": task_id
            }
            response = await http_client.post(url='https://new.trstempire.com/api/v1/tasks/complete',
                                              json=payload)
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while check tg subscription for {task_id} | Error: {e}")
            await asyncio.sleep(delay=3)

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        token_live_time = randint(3500, 3600)
        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    init_params = tg_web_data + '&start_param=' + get_link_code()
                    http_client.headers['Authorization'] = f'tma {self.headers}'
                    user_info = await self.get_info_data(http_client=http_client, init_params=init_params)

                    if user_info.get('country') is None:
                        await self.set_country_code(http_client=http_client)

                    access_token_created_time = time()
                    token_live_time = randint(3500, 3600)

                    balance = user_info['balance']
                    level_data = user_info['level']
                    level = level_data['level']
                    to_next_level = level_data['to_next_level']

                    await self.get_rewards(http_client=http_client)
                    notifications = await self.get_notifications(http_client=http_client)
                    for notify in notifications:
                        if notify['name'] == "next_level_reached" and notify['state'] == 'pending':
                            level = notify['data']['level']
                            reward = notify['data']['reward']
                            logger.info(f"{self.session_name} | Next Level Reached! | Getting rewards..")
                            await asyncio.sleep(delay=3)
                            result = await self.get_level_reward(http_client=http_client, level=level)
                            if result:
                                logger.success(f"{self.session_name} | | Got level reward: <e>{reward}</e> points")
                            await asyncio.sleep(delay=randint(3, 8))

                    logger.info(f"{self.session_name} | Balance: <e>{balance}</e> | User level: <y>{level}</y> | "
                                f"<c>{to_next_level}</c> points to the next level")

                    await self.processing_tasks(http_client=http_client)

                    sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                    logger.info(f"{self.session_name} | All tasks completed | Sleep <y>{sleep_time}</y> seconds")
                    await asyncio.sleep(delay=sleep_time)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))


def get_link_code() -> str:
    return bytes([106, 119, 71, 86, 102, 118, 122, 115, 83, 77, 85, 100, 85, 100,
                  112, 65, 84, 86, 81, 72]).decode("utf-8") if settings.USE_REF else ''


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
