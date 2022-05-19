import requests


class CryptoService:

    def __init__(self, email: str):
        self.email = email

    def get_p2p_wallet(self):
        response = requests.get(f'http://localhost:6227/api/v1/wallets/ethereum/email/{self.email}/p2p')
        if response.ok:
            return response.json()