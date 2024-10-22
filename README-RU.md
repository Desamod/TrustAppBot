[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/trust_empire_bot/trust_app?startapp=73c7b00d-2b0d-4337-a0ed-9d630c31d957)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON 3.10 🔥🔥

> 🇪🇳 README in english available [here](README.md)

## Функционал  
| Функционал                                              | Поддерживается |
|---------------------------------------------------------|:------------:|
| Многопоточность                                         |       ✅      |
| Поддержка tdata / pyrogram .session / telethon .session |       ✅      |
| Привязка прокси к сессии                                |       ✅      |
| Авто таски                                              |       ✅      |
| Сбор ежедневных наград                                  |       ✅      |
| Колесо фортуны                                          |       ✅      |



## [Настройки](https://github.com/Desamod/OkxRacerBot/blob/master/.env-example/)
| Настройка               |                                Описание                                 |
|-------------------------|:-----------------------------------------------------------------------:|
| **API_ID / API_HASH**   | Данные платформы, с которой запускать сессию Telegram (сток - Android)  | 
| **SLEEP_TIME**          |          Время сна между циклами (по умолчанию - [3000, 3600])          |
| **AUTO_TASK**           |               Автовыполнение тасок (по умолчанию - True)                |
| **JOIN_CHANNELS**       |        Авто-подписка на ТГ каналы из тасок (по умолчанию - True)        |
| **FORTUNE_REWARDS**     |            Награды из колеса фортуны ([200, 250,..., 2000])             |
| **USE_REF**             |             Использование реф. ссылки (по умолчанию - True)             |
| **USE_PROXY_FROM_FILE** | Использовать-ли прокси из файла `bot/config/proxies.txt` (True / False) |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/Desamod/TrustAppBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/Desamod/TrustAppBot
cd TrustAppBot
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/TrustAppBot >>> python3 main.py --action (1/2)
# Or
~/TrustAppBot >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/TrustAppBot >>> python main.py --action (1/2)
# Или
~/TrustAppBot >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


### Контакты

Для поддержки или вопросов, вы можете связаться со мной

[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/desforge_cryptwo)
