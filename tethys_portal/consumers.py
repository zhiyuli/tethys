import datetime
import json
import asyncio
import threading
from channels.generic.http import AsyncHttpConsumer


class BasicHttpConsumer(AsyncHttpConsumer):

    # How to test this async endpoint
    # Open 2 blank browser tabs, run the two urls at the same time
    # See: https://www.tornadoweb.org/en/stable/faq.html#my-code-is-asynchronous-but-it-s-not-running-in-parallel-in-two-browser-tabs
    # http://127.0.0.1:8000/asynchttp?x=1
    # http://127.0.0.1:8000/asynchttp?a=2
    # check the 2 "t_start" values, the difference of which should be less than 1 second
    # check the 2 "t_end" values, each of which should be +5 second from "t_start"
    # check the 2 "thread_name" values that should be identical
    async def handle(self, body):
        t_start = datetime.datetime.utcnow().strftime("%H:%M:%S")
        await asyncio.sleep(5)
        t_end = datetime.datetime.utcnow().strftime("%H:%M:%S")
        resp = dict(status="OK",
                    t_start=t_start,
                    t_end=t_end,
                    thread_name=threading.current_thread().name)

        await self.send_response(200, json.dumps(resp).encode(),
                                 headers=[(b"Content-Type", b"application/json"),])
