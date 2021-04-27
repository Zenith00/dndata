from __future__ import annotations

import itertools as itt
import typing as ty

import rules

if ty.TYPE_CHECKING:
   from entity import Entity
from rules import STATBLOCK, STAT

Z = itt.repeat(0)
Z_G = itt.repeat([0])


def to_hit(mod, ac):
   return min(1, max(0, 1 - (ac - mod - 1) / 20))


def to_save(dc, save_mod):
   return to_hit(save_mod, dc)


SAVE_TYPE = ty.Literal["half", "none"]


def factor_ac(bonus, target_ac, damage, adv=0):
   if adv == 0:
      hit_chance = to_hit(bonus, target_ac)
   elif adv < 0:
      hit_chance = (to_hit(bonus, target_ac)) ** (-1 + -adv)
   else:
      hit_chance = 1 - ((1 - (to_hit(bonus, target_ac))) ** (1 + adv))
   return hit_chance * damage


def factor_save(dc: int, save_mod: int, damage: float, save_type: SAVE_TYPE = "none"):
   save = to_save(dc, save_mod)

   if save_type == "half":
      return (save * damage * 0.5) + ((1 - save) * damage)
   elif save_type == "none":
      return ((1 - save) * damage)


class Damager:
   def __init__(self, base: float = 0, start: int = 0, n=None, gen=None):
      self.base = base
      self.start = start
      self.n = n
      self._gen: ty.Iterable[int] = gen

   # def ctx(self, source: Entity, target: Entity) -> Damager:
   #    self.source = source
   #    self.target = target
   #    return self

   def damage_raw(self, source: Entity = None, target: Entity = None):
      return self.base

   def damage(self, source: Entity = None, target: Entity = None):
      return self.damage_raw()

   def gen(self):
      return self._gen or itt.chain(itt.islice(Z, self.start), itt.islice(itt.repeat(self.damage()), self.n), Z)

   def delay(self, n: int):
      self.start += n
      return self


class Attack(Damager):
   def __init__(self, stat: ty.Union[rules.STAT, ty.Literal["SPELL"]], **kwargs):
      super(Attack, self).__init__(**kwargs)
      self.stat = stat

   def damage(self, source: Entity = None, target: Entity = None, adv=0):
      _stat: rules.STAT = self.stat if self.stat != "SPELL" else source.spellcasting
      return factor_ac(source.stats[_stat], target.ac, self.damage_raw(), adv=adv)

   def gen(self,  source: Entity = None, target: Entity = None, adv=0) -> ty.Iterable[int]:
      return self._gen or itt.chain(itt.islice(Z, self.start), itt.islice(itt.repeat(self.damage(source=source, target=target, adv=adv)), self.n), Z)


class SaveOrHalf(Damager):
   def __init__(self, target_stat: int, **kwargs):
      super(SaveOrHalf, self).__init__(**kwargs)
      self.target_stat = target_stat

   def damage(self, save_type: ty.Literal["half", "none"] = "none", source: Entity = None, target: Entity = None, adv=0):
      assert source and target
      return factor_save(target.saves[self.target_stat], source.stats[source.spellcasting], self.base, save_type)


class AttackPlusMod(Attack):
   def __init__(self, stat: ty.Union[rules.STAT, ty.Literal["SPELL"]], **kwargs):
      super(AttackPlusMod, self).__init__(stat, **kwargs)

   def damage_raw(self, source: Entity = None, target: Entity = None, adv=0):
      if not source:
         raise RuntimeError()
      _stat: rules.STAT = self.stat if self.stat != "SPELL" else source.spellcasting
      return self.base + source.stats[_stat]