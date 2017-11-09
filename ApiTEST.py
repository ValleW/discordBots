"API KEY: RGAPI-ea14755a-b28d-4894-a77f-38210452c0ab"
import asyncio
import aiohttp
from pprint import pprint

API_KEY = "RGAPI-ea14755a-b28d-4894-a77f-38210452c0ab"
testLink = "https://%s.api.pvp.net/api/lol/%s/v1.4/summoner/by-name/%s?api_key=%s"

@asyncio.coroutine
async def apitest():
    async with aiohttp.get(testLink % ("euw", "euw", "quackers", API_KEY)) as req:
        data = await req.json()
        print(data)
