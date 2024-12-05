<p align="center"><img width=60% src="docs/header.png"></p>

> Автоматизированная генераци iCloud почт, с помощью HideMyEmail.

_Вам нужно иметь активную подписку iCloud+, чтобы иметь возможность генерировать почты iCloud..._

<p align="center"><img src="docs/example.png"></p>

## Использование

Apple позволяет создавать около 5-10 hidemyemail почт, каждые 30 мин. Однако, по моему опыту, макс. единовременное количество почт iCloud ограничено 750, чтобы создавать еще, потребуют удалить предыдущие.

## Установка
> Требуется Python 3.9+!

1. Клонируйте этот репозиторий командой ниже, либо скачайте архив

```bash
git clone https://github.com/rtunazzz/hidemyemail-generator
```

2. Установите требуемые пакеты

```bash
pip install -r requirements.txt
```

3. [Сохраните свои ICloud cookies в файл](https://github.com/zrxmax/icloud-hidemyemail-generator#Получение-своих-ICloud-cookies)

   > Вам просто нужно сделать только это 🙂

4. Потом можете запустить скрипт:


**на Mac/Windows:**

```bash
python main.py
```

## Получение своих ICloud cookies

> Есть много способов, как получить строку своих cookie сайта, но по моему мнению, это простейший...

1. Скачай Chrome расширение [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

2. Зайди на страницу [настроек EditThisCookie](chrome-extension://fngmhnnpilhplaeedifhccceomclgfbg/options_pages/user_preferences.html) и поменяй "`preferred export format`" на "`Semicolon separated name=value pairs`"

<p align="center"><img src="docs/cookie-settings.png" width=70%></p>

3. Перейди на страницу [настроек iCloud](https://www.icloud.com/settings/) и выполни вход

4. Нажми на расширение EditThisCookie и экспортируй cookie

<p align="center"><img src="docs/export-cookies.png" width=70%></p>

5. Вставь экспортированные cookie в файл под названием `cookie.txt`

# Лицензия

ПО лицензируется по лицензии MIT License - подробности см. в файле [LICENSE](./LICENSE).


P.S. Я не писал скрипт полностью, его сделал **[rtuna](https://twitter.com/rtunazzz)**, за что я благодарен, я лишь его пофиксил, дополнил, и перевел на русский.
