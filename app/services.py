import requests


class CryptoService:

    def __init__(self, email: str):
        self.email = email

    def get_p2p_wallet(self):
        response = requests.get(f'http://host.docker.internal:6227/api/v1/wallets/ethereum/email/{self.email}/p2p', verify=False)
        if response.ok:
            return response.json()