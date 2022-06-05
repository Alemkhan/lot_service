import os
from typing import Any

import jwt
import requests
from django.conf import settings
from rest_framework.request import Request

from app.exceptions import AuthenticationRequiredException


class CryptoService:
    def __init__(self, email: str):
        self.email = email

    def get_p2p_wallet(self, crypto_type: str) -> dict[str, Any]:
        response = requests.get(
            f"http://{os.environ.get('WALLET_SERVICE_API', 'host.docker.internal')}/wallets/{crypto_type}/email/{self.email}/p2p",
            verify=False,
        )
        if response.ok:
            return response.json()

    def increase_seller_wallet_balance(
        self, amount: float, blockchain_id: str, crypto_type: str, sell_type: str
    ) -> None:
        balance_increase_url: str = "increaseToSell" if sell_type == "sell" else "increaseToBuy"

        response = requests.put(
            f"http://{os.environ.get('WALLET_SERVICE_API', 'host.docker.internal')}/wallets/{crypto_type}/p2p/{balance_increase_url}",
            verify=False,
            data={"walletId": blockchain_id, "amount": float(amount)},  # type: ignore
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()


def get_current_user_data(request: Request) -> dict[str, Any]:
    unauthorized_exc = AuthenticationRequiredException()
    raw_jwt = request.COOKIES.get("jwt-access")

    if raw_jwt is None:
        raise unauthorized_exc
    try:
        payload = jwt.decode(
            raw_jwt,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as e:
        raise unauthorized_exc from e

    return payload
