Хорошо, вот пример серверной реализации на Python с использованием официального MCP Python SDK, который:

* Использует транспорт streamable HTTP (или любой подходящий HTTP‑транспорт, поддерживаемый SDK)
* При инициализации MCP‑сессии извлекает токен из HTTP‑заголовков (например, Authorization: Bearer <token>)
* Валидирует токен через свой TokenVerifier
* Сохраняет токен в сессии и позволяет инструментам обращаться к нему через контекст

Для этого воспользуемся возможностями SDK, в частности mcp.server.fastmcp и модуля mcp.server.auth из Python SDK. В репозитории SDK уже есть поддержка аутентификации через токен — TokenVerifier. ([GitHub][1])

---

## 🛠 Зависимости

Убедись, что установлен MCP SDK:

pip install "mcp[cli]"

(или просто pip install mcp, если SDK уже включает нужные компоненты) ([GitHub][1])

---

## 📁 Структура файлов

Допустим, у нас будет такой минимальный файл:

* server.py — реализация MCP сервера с авторизацией

---

## 📄 server.py — пример

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier, AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.session import ServerSession
from mcp.server.fastmcp import Context

from pydantic import AnyHttpUrl
from typing import Optional

# Реализация верификатора токена
class MyTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """
        Этот метод вызывается при инициализации MCP сессии.
        Если токен валиден — возвращает объект AccessToken,
        иначе — возвращает None (отклонение доступа).
        """
        # Пример: если токен == "secret", считаем его валидным
        # В реальности ты проверишь JWT или БД или внешний Auth сервер
        if token == "secret-token-123":
            # создаём AccessToken
            return AccessToken(
                issuer="my-auth-server",
                subject="user-123",
                scopes=["tool.use"],
                expires_in=3600
            )
        return None

# Настройки аутентификации MCP
auth_settings = AuthSettings(
    issuer_url=AnyHttpUrl("https://my-auth.example.com"),
    resource_server_url=AnyHttpUrl("http://localhost:8000"),
    required_scopes=["tool.use"],
)

# Создаём MCP сервер с авторизацией
mcp = FastMCP(
    name="MyPythonMCP",
    token_verifier=MyTokenVerifier(),
    auth=auth_settings,
    # Используем stateful HTTP (так как нужен state, сохраняем информацию о сессии)  
    # По умолчанию FastMCP использует stateful mode, если stateless_http=False
    # Если требуется — можно явно указать:
    stateless_http=False
)

# Пример инструмента, который возвращает информацию о токене / пользователе
@mcp.tool()
async def whoami(ctx: Context[ServerSession, None]) -> dict:
    """
    Возвращает данные токена (если была авторизация), 
    иначе — сообщает, что нет авторизации.
    """
    access_token = ctx.session.access_token  # это атрибут после успешной верификации
    if access_token is None:
        return {"error": "no_token", "message": "You are unauthorized"}
    return {
        "issuer": access_token.issuer,
        "subject": access_token.subject,
        "scopes": access_token.scopes,
    }

# Пример ещё одного инструмента
@mcp.tool()
async def echo(message: str, ctx: Context[ServerSession, None]) -> str:
    # можно проверять токен внутри инструмента, если нужно
    if ctx.session.access_token is None:
        return "Unauthorized"
    return f"Echo: {message}"

def main():
    # Запускаем сервер с транспортом streamable HTTP
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

---

## 🧠 Объяснение кода и как это работает
