import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://0.0.0.0:8080/users/",
            json={"name": "g6565h6jk5h", "password": "bfdfbdnfbd44", "email": "g5uuuuuu@gmail.com"}
        )
        json_data = await response.text()
        print(json_data)


if __name__ == '__main__':
    asyncio.run(main())
