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
         name: str,
         ac: int,
         hp: int,
         stats: rules.STATBLOCK,
         # saves: ty.List[int],
         # save_profs: ty.List[int],
         attacks: ty.Dict[str, Attack],
         prof: int,
         spellcasting: rules.STAT,
   ):
      self.name = name
      self.stats = stats
      self.ac = ac
      self.saves = {k: stat["VALUE"] + (stat["PROFICIENT"] * prof) for k, stat in stats.items()}
      print(self.saves)
      # self.saves = [stat + (self.prof * save) for stat in self.stats.items()]
      self.modifiers = {k: (stat["VALUE"] - 10) // 2 for k, stat in stats.items()}
      self.attacks = attacks
      self.prof = prof
      self.spellcasting: rules.STAT = spellcasting
      self.spellcasting_dc: int = 8 + self.modifiers[spellcasting] + self.prof
      # self.attack_bonus = 10 + self.modifiers[attack_stat] + self.prof

   def damage_to(self, n: int, target: Entity):
      # noinspection PyTypeChecker
      attack_gen: ty.Iterable[ty.Tuple[int]] = zip(*[a.gen(source=self, target=target) for a in self.attacks.values()])
      attack_sum = (sum(round) for round in attack_gen)

      return sum(itt.islice(attack_sum, n))


class Monster(Entity):
   def __init__(
         self,
         cr: int,
         **kwargs
   ):
      prof = 2 + max(((cr - 1) // 4), 0)
      super(Monster, self).__init__(prof=prof, **kwargs)
      self.cr = cr


class Player(Entity):
   def __init__(
         self,
         name: str,
         ac: int,
         hp: int,
         prof: int,
         stats: rules.STATBLOCK,
         # saves: ty.List[int],
         # save_profs: ty.List[int],
         attacks: ty.Dict[str, Attack],
         spellcasting: rules.STAT,
   ):
      super().__init__(name=name, ac=ac, stats=stats, attacks=attacks, spellcasting=spellcasting, hp=hp, prof=prof)

   @staticmethod
   def fromJSON(raw_data: str, attacks: ty.Dict[str, Attack]):
      f = json.loads(raw_data)
      name = f["name"]
      data: ty.Dict = f["data"]
      # noinspection Mypy
      stats = rules.STATBLOCK(**{k.upper(): {"VALUE": v["value"], "PROFICIENT": v["proficient"]} for k, v in data["abilities"].items()})
      print(stats)
      ac = data["attributes"]["ac"]["value"]
      hp = data["attributes"]["hp"]["max"]
      spellcasting = data["attributes"]["spellcasting"].upper()
      prof = data["attributes"]["prof"]

      return Player(name=name, ac=ac, stats=stats, attacks=attacks, spellcasting=spellcasting, prof=prof, hp=hp)

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
