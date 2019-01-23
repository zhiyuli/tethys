import datetime
import json
import asyncio
import threading
from channels.generic.http import AsyncHttpConsumer


class BasicHttpConsumer(AsyncHttpConsumer):

    async def handle(self, body):
        t_start = datetime.datetime.utcnow().strftime("%H:%M:%S")
        await asyncio.sleep(5)
        t_end = datetime.datetime.utcnow().strftime("%H:%M:%S")
        resp = dict(status="OK",
                    t_start=t_start,
                    t_end=t_end,
                    thead_name=threading.current_thread().name)

        await self.send_response(200, json.dumps(resp).encode(),
                                 headers=[(b"Content-Type", b"application/json"),])
