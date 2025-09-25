1. Мы делаем класс MyTokenVerifier, который наследует TokenVerifier из модуля mcp.server.auth.provider. Этот класс отвечает за проверку поступившего токена. В методе verify_token(self, token) ты реализуешь свою логику (JWT, БД, вызов внешнего идентификационного сервера) и возвращаешь AccessToken или None. ([GitHub][1])
2. При инициализации FastMCP мы передаём token_verifier=MyTokenVerifier() и конфигурацию auth=auth_settings (нужен AuthSettings). ([GitHub][1])
3. Когда клиент подключается через HTTP (streamable HTTP транспорт), MCP SDK автоматически ожидает, что в HTTP-запросе будет заголовок Authorization: Bearer <token> (либо другой заголовок, как определено в спецификации MCP auth). SDK вызывает твой verify_token для проверки. Если verify_token возвращает None, сессия считается неавторизованной, и ты не сможешь получить ctx.session.access_token. ([GitHub][1])
4. Внутри инструментов (@mcp.tool()) ты можешь принять парамет ctx: Context[...] и оттуда получить ctx.session.access_token (если авторизация прошла). Если токен отсутствует, ты можешь отклонить вызов или вернуть ошибку.
5. mcp.run(transport="streamable-http") запускает сервер с HTTP-транспортом, подходящим для веб-клиентов и SCP-клиентов, поддерживающим потоковые соединения. ([GitHub][1])

Вот пример клиента на Python, который подключается к твоему MCP серверу с авторизацией по токену и вызывает инструменты, передавая токен в заголовке Authorization: Bearer <token>.

---

## ✅ Что ты получишь:

* Подключение к MCP серверу через http+stream транспорт.
* Авторизация с передачей токена в заголовке.
* Вызов инструмента (whoami, echo).
* Обработка ответа.

---

## 🐍 Установка MCP SDK клиента

pip install "mcp[client]"

---

## 📄 client.py — Пример клиента MCP с токеном

import asyncio
from mcp import McpClient, Context

async def main():
    # Токен, который будет отправлен в Authorization заголовке
    token = "secret-token-123"  # должен совпадать с тем, что принимает сервер

    # Создаем клиента
    client = McpClient(
        url="http://localhost:8000",  # адрес твоего сервера
        access_token=token,  # MCP SDK сам добавит заголовок Authorization: Bearer ...
        transport="http+stream"
    )

    # Устанавливаем соединение
    async with client as session:
        # Вызов инструмента "whoami"
        whoami_response = await session.call_tool("whoami", {})
        print("Ответ от whoami:", whoami_response)

        # Вызов инструмента "echo"
        echo_response = await session.call_tool("echo", {"message": "Привет!"})
        print("Ответ от echo:", echo_response)

if __name__ == "__main__":
    asyncio.run(main())

---

## 🔐 Что делает access_token?

Когда ты передаёшь access_token в McpClient, SDK автоматически добавляет:

Authorization: Bearer <твой_токен>

в заголовки при инициализации MCP-сессии.

---

## 📦 Что будет, если токен невалидный?

Если сервер не вернёт AccessToken (или verify_token вернёт None), тогда:

* MCP-сессия создастся, но ctx.session.access_token будет None.
* Сервер может отказать в вызове инструментов (вручную или через scopes).

---

## 🧪 Тест

Запусти сначала сервер (см. предыдущий ответ), потом клиент:

python server.py

Отдельно:

python client.py

---

## Хочешь:

* Пример клиента с JWT?
* Пример с токенами из OAuth2?
* Или клиент в браузере (JavaScript)?

Скажи, и я сделаю.
