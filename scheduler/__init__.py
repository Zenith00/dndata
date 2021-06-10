from __future__ import annotations

import datetime

import aurflux.context
import discord
from aurflux.command import Response
from aurflux import FluxCog
import typing as ty
import dateparser
import enum
import pendulum


class Scheduler(FluxCog):
   name = "scheduler"

   def load(self) -> None:
      @self._commandeer(name="schedule")
      async def schedule(ctx: aurflux.context.GuildMessageCtx, args: str, **_):
         """
         schedule party datetime
         ==
         ==
         :param ctx:
         :param args:
         :return:
         """

         party, session, timeslot_raw, *_ = *args.split(" ", 2), None, None
         print(party)
         print(session)
         print(timeslot_raw)
         print(_)

         PARTIES: ty.Dict[str, ty.Dict[str, ty.Callable[..., pendulum.DateTime]]] = {
            "purple": {"name": "Party 2", "default": lambda: pendulum.now().next(pendulum.SATURDAY).at(hour=18, minute=15),
                       "late": lambda: pendulum.now().next(pendulum.SATURDAY).at(hour=20)}
         }

         if party not in PARTIES:
            raise aurflux.CommandError(f"Party not recognized: `{party}`")

         if timeslot_raw is None:
            timeslot: ty.Optional[datetime.datetime] = PARTIES[party]["default"]()
         elif timeslot_func := PARTIES[party].get(timeslot_raw):
            timeslot = timeslot_func()
         else:
            timeslot = eval(timeslot_raw)

         embed = discord.Embed(
            title=PARTIES[party]["name"],
            description=(f"[{timeslot.strftime('%A, %B %d at %#I:%M %p PT')}]"
                         f"(https://www.timeanddate.com/worldclock/fixedtime.html?" +
                         (f"msg={PARTIES[party]['name']}+Session+14&iso={timeslot.strftime('%Y%m%dT%H%M')}&p1=283&ah=4)".replace(" ", "+"))),

         )

         yield Response(embed=embed)