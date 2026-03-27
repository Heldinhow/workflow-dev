"""MiniMax LLM interceptor that converts system messages to user messages.

MiniMax API rejects 'system' role messages, so we convert them to 'user' role.
"""

import json
import httpx
from crewai.llms.hooks.base import BaseInterceptor


class MiniMaxInterceptor(BaseInterceptor[httpx.Request, httpx.Response]):
    """Interceptor that converts system messages to user messages for MiniMax API."""

    def on_outbound(self, message: httpx.Request) -> httpx.Request:
        url_str = str(message.url)
        if "chat" not in url_str or "completions" not in url_str:
            return message

        try:
            body = json.loads(message.content)
            messages = body.get("messages", [])

            new_messages = []
            converted = False
            for m in messages:
                if m.get("role") == "system":
                    new_messages.append(
                        {"role": "user", "content": m.get("content", "")}
                    )
                    converted = True
                else:
                    new_messages.append(m)

            if converted:
                body["messages"] = new_messages
                message._content = json.dumps(body).encode()

        except Exception:
            pass

        return message

    def on_inbound(self, message: httpx.Response) -> httpx.Response:
        return message
