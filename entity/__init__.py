from __future__ import annotations

import pathlib
import typing as ty

import rules
from simulator.attack import Attack
import itertools as itt
import json


class Entity:
   def __init__(
         self,

         ac: int,
         stats: rules.STATBLOCK,
         prof: int,

         attacks: ty.Dict[str, Attack] = None,
         name: str = "",
         hp: int = None,
         spellcasting: rules.STAT = None,
   ):
      self.name = name
      self.stats = stats
      self.ac = ac
      self.saves = {k: stat["VALUE"] + (stat["PROFICIENT"] * prof) for k, stat in stats.items()}
      # self.saves = [stat + (self.prof * save) for stat in self.stats.items()]
      self.modifiers = {k: (stat["VALUE"] - 10) // 2 for k, stat in stats.items()}
      self.attacks = attacks
      self.prof = prof
      self.spellcasting: rules.STAT = spellcasting
      self.spellcasting_dc: int = 8 + self.modifiers[spellcasting] + self.prof if spellcasting else -1
      # self.attack_bonus = 10 + self.modifiers[attack_stat] + self.prof

   def damage_to(self, n: int, target: Entity):
      # noinspection PyTypeChecker
      if isinstance(self, Player):
         self.spellslots = list(self.spellslots_base)
      attack_gen: ty.Iterable[ty.Tuple[int]] = zip(*[a.gen(source=self, target=target) for a in self.attacks.values()])
      attack_sum = (sum(round) for round in attack_gen)
      return sum(itt.islice(attack_sum, 1,n+1))


class Monster(Entity):
   def __init__(
         self,
         cr: int =0 ,
         **kwargs
   ):
      prof = 2 + max(((cr - 1) // 4), 0)
      super(Monster, self).__init__(prof=prof, **kwargs)
      self.cr = cr


class Player(Entity):
   def __init__(
         self,
         level: int,
         stats: rules.STATBLOCK,
         name: str = None,

         ac: ty.Callable[[], int] = None,
         hp: int = None,
         spellslots: ty.List[int] = None,
         attacks: ty.Dict[str, Attack] = None,
         spellcasting: rules.STAT = None,
   ):
      self.level = level
      self.spellslots = spellslots
      self.spellslots_base = tuple(spellslots) if spellslots else ()
      super().__init__(name=name, ac=ac, stats=stats, attacks=attacks, spellcasting=spellcasting, hp=hp, prof=2 + max(((level - 1) // 4), 0))

   @staticmethod
   def fromJSON(raw_data: str, attacks: ty.Dict[str, Attack]):
      f = json.loads(raw_data)
      name = f["name"]
      data: ty.Dict = f["data"]
      # noinspection Mypy
      stats = rules.STATBLOCK(**{k.upper(): {"VALUE": v["value"], "PROFICIENT": v["proficient"]} for k, v in data["abilities"].items()})
      ac = data["attributes"]["ac"]["value"]
      hp = data["attributes"]["hp"]["max"]
      spellcasting = data["attributes"]["spellcasting"].upper()
      level = data["attributes"]["details"]["level"]
      spellslots = [data["spells"][f"spell{n}"]["max"] for n in range(1,10)]
      spellslots[data["spells"]["pact"]["level"]] += data["spells"]["pact"]["max"]

      return Player(name=name, ac=ac, stats=stats, attacks=attacks, spellcasting=spellcasting, spellslots=spellslots, level=level, hp=hp)

   # def damage(self, n, target_ac=10, target_save=10):
   #    attack_gen: ty.Iterable[ty.Tuple[int]] = zip(*[a.ctx(target_ac, target_save, self.mod + self.prof, self.prof).gen() for a in self.attacks.values()])
   #    attack_sum = (sum(round) for round in attack_gen)
   #
   #    return sum(itt.islice(attack_sum, n))

   # def damage_to(self, target: Monster):
   #    attack_gen: ty.Iterable[ty.Tuple[int]] = zip(*[a.ctx(target_ac, target_save, self.bonus + self.prof, self.prof).gen() for a in self.attacks.values()])
   #    attack_sum = (sum(round) for round in attack_gen)
   #
   #    return sum(itt.islice(attack_sum, n))

   # def dmgs(self, n):
   #    return f"{self.damage(n):05.2f}"
   #
   # def output(self, n):
   #    print(f"{self.__class__.__name__}:\t{self.damage(n)}\tover {n} turns")


class Party:
   def __init__(self, players, level):
      self.players: ty.List[Player] = players
      for player in players:
         player.level = level

   def damage_to(self, n, target: Entity):
      return sum([p.damage_to(n, target) for p in self.players])

   def output_dps(self, n, target):
      print("\t".join((p.name for p in self.players)))
      for i in range(1, n + 1):
         print("\t".join(str(p.damage_to(i, target)) for p in self.players))


class Encounter:
   def __init__(self, party: Party, monsters: ty.List[Monster]):
      pass