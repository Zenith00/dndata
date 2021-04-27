from __future__ import annotations

import typing as ty

import TOKENS
import aurcore
import aurflux
import discord
import ssl
import asyncio
from scheduler import Scheduler
if ty.TYPE_CHECKING:
    from aurflux.command import *


class ExtinctBot:
    def __init__(self):
        self.event_router = aurcore.event.EventRouterHost(name=self.__class__.__name__)
        self.flux = aurflux.FluxClient(self.__class__.__name__, admin_id=TOKENS.ADMIN_ID, parent_router=self.event_router, intents=discord.Intents.all())

    async def startup(self, token: str):
        await self.flux.startup(token)

    async def shutdown(self):
        await self.flux.logout()

#
# async def startup():
#   ssl_context = ssl.create_default_context()
#   print(ssl.get_default_verify_paths())
#   # ssl_context.load_verify_locations(certifi.where())
#   pool: asyncpg.pool.Pool = await asyncpg.create_pool(TOKENS.PSQL_STRING, ssl=ssl_context)


extinctBot = ExtinctBot()
extinctBot.flux.register_cog(Scheduler)
aurcore.aiorun(extinctBot.startup(token=TOKENS.EXTINCT), extinctBot.shutdown())
# asyncio.run(startup())