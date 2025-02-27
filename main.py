from asyncio import sleep, run, gather
from aiohttp import ClientSession, ClientResponse

from colorama import Fore
from logging import getLogger, basicConfig, INFO

from random import choice
from typing import Optional

from json import load

API_VERSION = "v10"
CONFIGURATION = load(open("data/configuration.json"))

basicConfig(level=INFO)
log = getLogger(__name__)


class Spammer:
    BASE_URL = f"https://discord.com/api/{API_VERSION}"
    session: Optional[ClientSession]

    def __init__(self):
        self.session = None

    async def _handle_response(self, response: ClientResponse, token: str) -> None:
        match response.status:
            case 200:
                log.info(
                    f"{Fore.GREEN}[SUCCESS]{Fore.WHITE} Successfully created message object. ({token.split('.')[0]}***)"
                )
            case 429:
                header = float(response.headers.get("X-RateLimit-Reset-After", 0))
                log.info(f"{Fore.YELLOW}[LIMITED]{Fore.WHITE} Ratelimit: {header}")

                await sleep(header)
            case _:
                log.info(
                    f"{Fore.RED}[FAILURE]{Fore.WHITE} Failed to send request: {response.status}"
                )

    async def send_request(self, token: str) -> None:
        while self.session:
            channel_id = choice(CONFIGURATION.get("channels", []))
            message = choice(CONFIGURATION.get("messages", []))

            try:
                response = await self.session.post(
                    f"{self.BASE_URL}/channels/{channel_id}/messages",
                    json={"content": message},
                    headers={"Authorization": token},
                )

                await self._handle_response(response=response, token=token)
            finally:
                await sleep(0.25)

    async def start_instance(self, tokens: list[str]):
        self.session = ClientSession()
        await gather(*[self.send_request(token=token) for token in tokens])


async def main():
    tokens = open(CONFIGURATION.get("token_file", ""), "r").read().splitlines()

    instance = Spammer()
    await instance.start_instance(tokens=tokens)


if __name__ == "__main__":
    run(main())
