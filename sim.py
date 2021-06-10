import abc
import collections as clc
import random
import typing as ty
from decimal import Decimal

import numpy as np

from entity import Monster, Player
from rules import make_statblock
from simulator import attack

AC = [
   # 0  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19, 20
   -1, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 17, 17, 17, 17, 19, 19, 19, 19, 19, 25
]


class D:
   def __init__(self, n):
      self.n = n

   def __call__(self: bool, average: bool = False):  # type hint muckery to suppress pycharm bug
      if average:
         return Decimal(self.n / 2 + 0.5)
      return Decimal(random.randint(1, self.n))


class OnePerTurn(D):
   def __init__(self, n):
      super(OnePerTurn, self).__init__(n)
      self.used = False

   def __call__(self, average: bool = False):
      if self.used:
         return 0
      self.used = True
      return super(OnePerTurn, self).__call__(average)


A = False


class DPR:
   def __init__(self):

      self.damage_sims: ty.Dict[str, ty.Callable[[], float]] = {}
      pass

   @abc.abstractmethod
   def register(self):
      ...

   def simulate(self, n=10000):
      self.register()
      data = clc.defaultdict(lambda: np.zeros(shape=n))

      for name, (p, t, sim) in self.damage_sims.items():
         for i in range(n):
            data[name][i] = sim(p, t)
         # data[k] = v()

      return data

   def sim(self, name: str, level: int = None, player: Player = None, target: Monster = None):
      if player is None:
         player = Player(level=level, stats=STATBLOCKS[level])
      if target is None:
         target = MONSTERS[level]

      def sim_decorator(f: ty.Callable[[], float]):
         self.damage_sims[name] = player, target, f
         return f

      return sim_decorator


STATBLOCKS = (
      [make_statblock((8, True), (18, True), (15, False), (8, False), (15, False), (8, False))] * 4 +
      [make_statblock((8, True), (20, True), (15, False), (8, False), (15, False), (8, False))] * 6 +
      [make_statblock((8, True), (20, True), (15, False), (8, False), (15, False), (8, False))] * 11)

MONSTERS = [
   Monster(
      ac=ac,
      stats=make_statblock((20, True), (20, False), (20, True), (8, False), (8, False), (8, False)),
   )
   for ac in AC]


# noinspection DuplicatedCode,PyPep8Naming
class Gunk(DPR):
   def musket_attack(self, ARCHERY, DEX, P, t, OWTB, advantage=False, dread_ambusher=False, precision=0, superiority_dmg=0, emboldening_bond=False) -> ty.Tuple[int, int]:
      """

      :param ARCHERY: Archery To-Hit Bonus
      :param DEX:  Dex Modifier
      :param P: Proficiency Modifier
      :param t: target
      :param OWTB: True if use OWTB on first non-focused hit, False if use OWTB only if final hit lands without ki expenditure
      :param advantage:
      :param dread_ambusher:
      :return:
      """

      FF = OnePerTurn(4)  # Favored Foe once per turn

      OWTB = D(6)

      SUPERIORITY = D(8)
      EMBOLDENING_BOND = D(4)
      superiority_used = 0
      MUSKET = D(12)
      SS_DMG = 10
      DREAD_AMBUSH = D(8)
      damage = 0
      ki_used = False

      ATTACK_NUM = 2 if not dread_ambusher else 3
      for i in range(ATTACK_NUM):
         rawroll = [D(20)(A) + DEX + P - 5 + ARCHERY, D(20)(A) + DEX + P - 5 + ARCHERY]
         attack_roll = max(rawroll) if advantage else rawroll[0]
         additional_damage = 0
         # Hit Normally
         if attack_roll >= t.ac:
            additional_damage = MUSKET(A) + DEX + SS_DMG + (OWTB(A) if not ki_used else 0) + FF(A)  # Use OWTB aggressively



         # Missed by <= 2, use Focused Aim
         elif attack_roll + 2 >= t.ac:
            additional_damage = MUSKET(A) + DEX + SS_DMG + FF(A)
            ki_used = True



         # 50% chance to hit with Focused + Emboldening
         elif (attack_roll + 2 + Decimal(2.5)) >= t.ac and emboldening_bond:
            emboldening_bond = False

            if attack_roll +2 + EMBOLDENING_BOND(A) >= t.ac:
               additional_damage = MUSKET(A) + DEX + SS_DMG + FF(A)

         # 50% chance to hit if we use Focused + Superiority
         elif precision > 0 and ((t.ac - (attack_roll + 2 )) < 4.5):
            precision -= 1
            if attack_roll + SUPERIORITY(A) >= t.ac:
               additional_damage = MUSKET(A) + DEX + SS_DMG + FF(A)

         # 50% chance to hit if we used Focused + Emboldening + Superiority
         elif precision > 0 and ((t.ac - attack_roll) < (4.5+2.5)) and emboldening_bond:
            precision -= 1
            emboldening_bond = False

            if attack_roll + SUPERIORITY(A) + EMBOLDENING_BOND(A) >= t.ac:
               additional_damage = MUSKET(A) + DEX + SS_DMG + FF(A)

         if i == 2 and additional_damage:
            additional_damage += DREAD_AMBUSH(A)

         damage += additional_damage

      return damage, precision

   def register(self):
      @self.sim("L1", level=1)
      def L1(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         punch = attack.factor_ac(DEX + P, t.ac, D(4)(A) + p.modifiers["DEX"])
         ba_punch = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)
         return punch + ba_punch

      @self.sim("L2", level=2)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket = attack.factor_ac(DEX + P, t.ac, D(12)(A) + DEX)
         ba_punch = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)
         return musket + ba_punch

      @self.sim("L2-Flurry", level=2)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket = attack.factor_ac(DEX + P, t.ac, D(12)(A) + DEX)
         ba_flurry = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX) + attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)

         return musket + ba_flurry

      @self.sim("L3", level=3)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket = attack.factor_ac(DEX + P, t.ac, D(12)(A) + DEX)
         ba_punch = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)
         return musket + ba_punch

      @self.sim("L3-Flurry", level=3)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket = attack.factor_ac(DEX + P, t.ac, D(12)(A) + DEX)
         ba_flurry = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX) + attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)

         return musket + ba_flurry

      @self.sim("L4", level=4)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket_SS = attack.factor_ac(DEX + P - 5, t.ac, D(12)(A) + DEX + 10)
         ba_punch = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)
         return musket_SS + ba_punch

      @self.sim("L4-Flurry", level=4)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         musket_SS = attack.factor_ac(DEX + P - 5, t.ac, D(12)(A) + DEX + 10)

         ba_flurry = attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX) + attack.factor_ac(DEX + P, t.ac, D(4)(A) + DEX)
         return musket_SS + ba_flurry

      @self.sim("L5", level=5)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof

         musket_SS_1_atkroll = D(20)(A) + DEX + P - 5

         musket_SS_1_damage = 0
         musket_SS_2_atkroll = D(20)(A) + DEX + P - 5

         musket_SS_2_damage = 0
         ki_used = False

         if musket_SS_1_atkroll >= t.ac:
            musket_SS_1_damage = D(12)(A) + DEX + 10
         # Use Focused Aim to boost attack roll by 2
         elif musket_SS_1_atkroll + 2 >= t.ac:
            musket_SS_1_damage = D(12)(A) + DEX + 10
            ki_used = True

         if musket_SS_2_atkroll >= t.ac:
            musket_SS_2_damage = D(12)(A) + DEX + 10
         # If Focused Aim would let us hit & we didn't already use ki
         elif musket_SS_2_atkroll + 2 >= t.ac and not ki_used:
            musket_SS_2_damage = D(12)(A) + DEX + 10

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5, t.ac, D(12)(A) + DEX + 10)

         return musket_SS_1_damage + musket_SS_2_damage + musket_SS_ba_damage

      @self.sim("L6", level=6)
      def L2(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof

         musket_damage, _ = self.musket_attack(0, DEX, P, t, False)
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L6-OWTB", level=6)
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof

         musket_damage, _ = self.musket_attack(0, DEX, P, t, True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L7", level=7)
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(0, DEX, P, t, False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L7-OWTB", level=7)
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L8", level=8)
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L8-OWTB", level=8)
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L9 T1", level=9)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L9 T2+", level=9)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L9 T1 Adv", level=9)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L9 T2+ Adv", level=9)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L10 T1", level=10)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L10 T2+", level=10)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L10 T1 Adv", level=10)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L10 T2+ Adv", level=10)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L11 T1", level=11)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L11 T2+", level=11)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L11 T1 Adv", level=11)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L11 T2+ Adv", level=11)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage + musket_SS_ba_damage

      @self.sim("L12 T1", level=12)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L12 T2+", level=12)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L12 T1 Adv", level=12)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L12 T2+ Adv", level=12)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T1", level=13)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T2+", level=13)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T1 Adv", level=13)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T2+ Adv", level=13)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T1 Precision Only", level=13)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T2+ Precision Only", level=13)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T1 Adv Precision Only", level=13)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, precision=sd_left)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L13 T2+ Adv Precision Only", level=13)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage


      @self.sim("L20 T1", level=20)  # Dread Ambusher Turn 1
      @self.sim("L19 T1", level=19)  # Dread Ambusher Turn 1
      @self.sim("L18 T1", level=18)  # Dread Ambusher Turn 1
      @self.sim("L17 T1", level=17)  # Dread Ambusher Turn 1
      @self.sim("L16 T1", level=16)  # Dread Ambusher Turn 1
      @self.sim("L15 T1", level=15)  # Dread Ambusher Turn 1
      @self.sim("L14 T1", level=14)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, emboldening_bond=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, emboldening_bond=True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T2+", level=20)  # Dread Ambusher Turn 2+
      @self.sim("L19 T2+", level=19)  # Dread Ambusher Turn 2+
      @self.sim("L18 T2+", level=18)  # Dread Ambusher Turn 2+
      @self.sim("L17 T2+", level=17)  # Dread Ambusher Turn 2+
      @self.sim("L16 T2+", level=16)  # Dread Ambusher Turn 2+
      @self.sim("L15 T2+", level=15)  # Dread Ambusher Turn 2+
      @self.sim("L14 T2+", level=14)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, emboldening_bond=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, emboldening_bond=True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T1 Adv", level=20)  # Dread Ambusher Turn 1
      @self.sim("L19 T1 Adv", level=19)  # Dread Ambusher Turn 1
      @self.sim("L18 T1 Adv", level=18)  # Dread Ambusher Turn 1
      @self.sim("L17 T1 Adv", level=17)  # Dread Ambusher Turn 1
      @self.sim("L16 T1 Adv", level=16)  # Dread Ambusher Turn 1
      @self.sim("L15 T1 Adv", level=15)  # Dread Ambusher Turn 1
      @self.sim("L14 T1 Adv", level=14)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, emboldening_bond=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, emboldening_bond=True)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T2+ Adv", level=20)  # Dread Ambusher Turn 2+
      @self.sim("L19 T2+ Adv", level=19)  # Dread Ambusher Turn 2+
      @self.sim("L18 T2+ Adv", level=18)  # Dread Ambusher Turn 2+
      @self.sim("L17 T2+ Adv", level=17)  # Dread Ambusher Turn 2+
      @self.sim("L16 T2+ Adv", level=16)  # Dread Ambusher Turn 2+
      @self.sim("L15 T2+ Adv", level=15)  # Dread Ambusher Turn 2+
      @self.sim("L14 T2+ Adv", level=14)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage_1, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, emboldening_bond=True)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, emboldening_bond=True)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T1 Precision Only", level=20)  # Dread Ambusher Turn 1
      @self.sim("L19 T1 Precision Only", level=19)  # Dread Ambusher Turn 1
      @self.sim("L18 T1 Precision Only", level=18)  # Dread Ambusher Turn 1
      @self.sim("L17 T1 Precision Only", level=17)  # Dread Ambusher Turn 1
      @self.sim("L16 T1 Precision Only", level=16)  # Dread Ambusher Turn 1
      @self.sim("L15 T1 Precision Only", level=15)  # Dread Ambusher Turn 1
      @self.sim("L14 T1 Precision Only", level=14)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         # OWTB Damage Bonus is negligible here, so ignoring from now on
         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, emboldening_bond=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=True, emboldening_bond=True, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T2+ Precision Only", level=20)  # Dread Ambusher Turn 2+
      @self.sim("L19 T2+ Precision Only", level=19)  # Dread Ambusher Turn 2+
      @self.sim("L18 T2+ Precision Only", level=18)  # Dread Ambusher Turn 2+
      @self.sim("L17 T2+ Precision Only", level=17)  # Dread Ambusher Turn 2+
      @self.sim("L16 T2+ Precision Only", level=16)  # Dread Ambusher Turn 2+
      @self.sim("L15 T2+ Precision Only", level=15)  # Dread Ambusher Turn 2+
      @self.sim("L14 T2+ Precision Only", level=14)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, emboldening_bond=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, dread_ambusher=False, emboldening_bond=True, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T1 Adv Precision Only", level=20)  # Dread Ambusher Turn 1
      @self.sim("L19 T1 Adv Precision Only", level=19)  # Dread Ambusher Turn 1
      @self.sim("L18 T1 Adv Precision Only", level=18)  # Dread Ambusher Turn 1
      @self.sim("L17 T1 Adv Precision Only", level=17)  # Dread Ambusher Turn 1
      @self.sim("L16 T1 Adv Precision Only", level=16)  # Dread Ambusher Turn 1
      @self.sim("L15 T1 Adv Precision Only", level=15)  # Dread Ambusher Turn 1
      @self.sim("L14 T1 Adv Precision Only", level=14)  # Dread Ambusher Turn 1
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2

         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, emboldening_bond=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=True, emboldening_bond=True, precision=sd_left)
         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage

      @self.sim("L20 T2+ Adv Precision Only", level=20)  # Dread Ambusher Turn 2+
      @self.sim("L19 T2+ Adv Precision Only", level=19)  # Dread Ambusher Turn 2+
      @self.sim("L18 T2+ Adv Precision Only", level=18)  # Dread Ambusher Turn 2+
      @self.sim("L17 T2+ Adv Precision Only", level=17)  # Dread Ambusher Turn 2+
      @self.sim("L16 T2+ Adv Precision Only", level=16)  # Dread Ambusher Turn 2+
      @self.sim("L15 T2+ Adv Precision Only", level=15)  # Dread Ambusher Turn 2+
      @self.sim("L14 T2+ Adv Precision Only", level=14)  # Dread Ambusher Turn 2+
      def _(p: Player, t: Monster):
         DEX = p.modifiers["DEX"]
         P = p.prof
         ARCHERY = 2
         musket_damage_1, sd_left = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, emboldening_bond=True, precision=4)
         musket_damage_2, _ = self.musket_attack(ARCHERY, DEX, P, t, False, advantage=True, dread_ambusher=False, emboldening_bond=True, precision=sd_left)

         # Ki-Fueled Attack
         musket_SS_ba_damage = attack.factor_ac(DEX + P - 5 + ARCHERY, t.ac, D(12)(A) + DEX + 10, adv=1)

         return musket_damage_1 + musket_damage_2 + musket_SS_ba_damage


import tabulate

GunkSim = Gunk()

print(tabulate.tabulate([(n, data.mean()) for n, data in GunkSim.simulate(10000).items()]))