from __future__ import annotations

import datetime

import aurflux.context
from aurflux.command import Response
from aurflux import FluxCog
import typing as ty
import dateparser
import enum


class Scheduler(FluxCog):

   def load(self) -> None:
      @self._commandeer(name="schedule")
      async def schedule(ctx: aurflux.context.GuildMessageCtx, args: str):
         """
         schedule party datetime
         ==
         ==
         :param ctx:
         :param args:
         :return:
         """
         party, timeslot_raw, *_ = *args.split(" ", 1), None

         PARTIES: ty.Dict[str, ty.Dict[str, str]] = {
            "purple": {"default": "next saturday at 6:15 PM PST", "late": "next saturday at 8:00 PM PST"}
         }

         if party not in PARTIES:
            raise aurflux.CommandError(f"Party not recognized: `{party}`")


         if timeslot_raw is None:
            timeslot : ty.Optional[datetime.datetime] = dateparser.parse(PARTIES[party]["default"])

         elif (timeslot_expanded := PARTIES[party].get(timeslot_raw)):
            timeslot : ty.Optional[datetime.datetime] = dateparser.parse(timeslot_expanded)
         else:
            timeslot : ty.Optional[datetime.datetime] = dateparser.parse(timeslot_raw)
         if not timeslot:
            raise aurflux.CommandError(f"Did not recognize time string: `{timeslot_raw}`")

         return Response(timeslot.isoformat())