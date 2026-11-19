
import hashlib
import hmac
import json
import logging
import time

from urllib.parse import parse_qsl

logger = logging.getLogger(__name__)


def verify_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age: int = 3600,
) -> dict | None:

    try:
        if not init_data or not bot_token:
            logger.warning("Telegram Auth: missing initData or bot token")
            return None

        pairs = parse_qsl(
            init_data,
            keep_blank_values=True,
            strict_parsing=True,
        )

        data = dict(pairs)

        if len(data) != len(pairs):
            logger.warning("Telegram Auth: duplicate parameters")
            return None

        received_hash = data.pop("hash", None)

        if not received_hash:
            logger.warning("Telegram Auth: hash missing")
            return None

        auth_date = int(data["auth_date"])
        now = int(time.time())

        if auth_date > now + 60:
            logger.warning("Telegram Auth: future auth_date")
            return None

        if now - auth_date > max_age:
            logger.warning("Telegram Auth: initData expired")
            return None

        data_check_string = "\n".join(
            f"{key}={value}"
            for key, value in sorted(data.items())
        )

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            calculated_hash,
            received_hash,
        ):
            logger.warning("Telegram Auth: invalid signature")
            return None

        user = json.loads(data["user"])

        if not isinstance(user, dict):
            logger.warning("Telegram Auth: invalid user object")
            return None

        if type(user.get("id")) is not int:
            logger.warning("Telegram Auth: invalid user ID")
            return None

        logger.info("Telegram Auth: verification successful")

        return user

    except (ValueError, KeyError, TypeError, UnicodeError) as error:
        logger.warning(
            "Telegram Auth: invalid data (%s)",
            type(error).__name__,
        )
        return None
