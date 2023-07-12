import aiohttp
import asyncio


class APIManager:
    """
    Реализация с использованием паттерна "Синглтон" и класса.

    Этот подход создает один экземпляр aiohttp.ClientSession для всех запросов
    и оптимизирует повторения и задержки в методе make_request.

    Во избежании утечки памяти, после серии запросов необходимо закрывать сессию - await APIManager.close_session()
    """
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session is not None:
            await cls._session.close()

    @staticmethod
    async def make_request(
            method,
            url,
            headers=None,
            params=None,
            data=None,
            json=None,
            retries=3,
            delay=5,
            timeout=10
    ):
        """
        Отправляет запрос по указанному url.
            Returns:
                dict or None: возвращает ответ сервера или None.
        """
        for _ in range(retries):
            try:
                async with getattr(APIManager.get_session(), method)(
                        url,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json,
                        timeout=timeout
                ) as response:
                    if response.status in {200, 201, 203, 204, 307}:
                        try:
                            response_data = await response.json()
                            return response_data
                        except ValueError:
                            pass
                        except Exception:
                            break
            except aiohttp.ClientError:
                pass

            await asyncio.sleep(delay)
        return None