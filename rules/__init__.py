import pprint
import typing as ty
import enum


class CLASSES(enum.IntEnum):
   BARBARIAN = enum.auto()
   BARD = enum.auto()
   CLERIC = enum.auto()
   DRUID = enum.auto()
   FIGHTER = enum.auto()
   MONK = enum.auto()
   PALADIN = enum.auto()
   RANGER = enum.auto()
   ROGUE = enum.auto()
   SORCERER = enum.auto()
   WARLOCK = enum.auto()
   WIZARD = enum.auto()


class _STAT(ty.TypedDict):
   VALUE: int
   PROFICIENT: bool

   @classmethod
   def fromtuple(cls, t: ty.Tuple[int, bool]):
      return cls.__init__(VALUE=t[0], PROFICIENT=t[1])


STAT = ty.Literal["STR", "DEX", "CON", "INT", "WIS", "CHA"]


class STATBLOCK(ty.TypedDict):
   STR: _STAT
   DEX: _STAT
   CON: _STAT
   INT: _STAT
   WIS: _STAT
   CHA: _STAT


def make_statblock(
      STR: ty.Tuple[int, bool],
      DEX: ty.Tuple[int, bool],
      CON: ty.Tuple[int, bool],
      INT: ty.Tuple[int, bool],
      WIS: ty.Tuple[int, bool],
      CHA: ty.Tuple[int, bool],
      ATK: STAT = None
):
   return STATBLOCK(
      STR=_STAT(VALUE=STR[0], PROFICIENT=STR[1]),
      DEX=_STAT(VALUE=DEX[0], PROFICIENT=DEX[1]),
      CON=_STAT(VALUE=CON[0], PROFICIENT=CON[1]),
      INT=_STAT(VALUE=INT[0], PROFICIENT=INT[1]),
      WIS=_STAT(VALUE=WIS[0], PROFICIENT=WIS[1]),
      CHA=_STAT(VALUE=CHA[0], PROFICIENT=CHA[1]),
   )




class CL:
   def __init__(self, class_: CLASSES, level: int):
      self.class_: CLASSES = class_
      self.level = level

   @staticmethod
   def BARBARIAN(level: int):
      return CL(CLASSES.BARBARIAN, level)

   @staticmethod
   def BARD(level: int):
      return CL(CLASSES.BARD, level)

   @staticmethod
   def CLERIC(level: int):
      return CL(CLASSES.CLERIC, level)

   @staticmethod
   def DRUID(level: int):
      return CL(CLASSES.DRUID, level)

   @staticmethod
   def FIGHTER(level: int):
      return CL(CLASSES.FIGHTER, level)

   @staticmethod
   def MONK(level: int):
      return CL(CLASSES.MONK, level)

   @staticmethod
   def PALADIN(level: int):
      return CL(CLASSES.PALADIN, level)

   @staticmethod
   def RANGER(level: int):
      return CL(CLASSES.RANGER, level)

   @staticmethod
   def ROGUE(level: int):
      return CL(CLASSES.ROGUE, level)

   @staticmethod
   def SORCERER(level: int):
      return CL(CLASSES.SORCERER, level)

   @staticmethod
   def WARLOCK(level: int):
      return CL(CLASSES.WARLOCK, level)

   @staticmethod
   def WIZARD(level: int):
      return CL(CLASSES.WIZARD, level)


CLASS_SAVE_PROFS = {  # str  dex con int wis cha
   CLASSES.BARBARIAN: [True, False, True, False, False, False],
   CLASSES.BARD     : [False, True, False, False, False, True],
   CLASSES.CLERIC   : [False, False, False, False, True, True],
   CLASSES.DRUID    : [False, False, False, True, True, False],
   CLASSES.FIGHTER  : [True, False, True, False, False, False],
   CLASSES.MONK     : [True, True, False, False, False, False],
   CLASSES.PALADIN  : [False, False, False, False, True, True],
   CLASSES.RANGER   : [True, True, False, False, False, False],
   CLASSES.ROGUE    : [False, True, False, True, False, False],
   CLASSES.SORCERER : [False, False, True, False, False, True],
   CLASSES.WARLOCK  : [False, False, False, False, True, True],
   CLASSES.WIZARD   : [False, False, False, True, True, False],
}

SPELLSLOTS = [[0]*9] + [[
   int(i >= 1) * 2 + int(i >= 2) * 1 + int(i >= 3) * 1,  # 1st
   int(i >= 3) * 2 + int(i >= 4) * 1,  # 2nd
   int(i >= 5) * 2 + int(i >= 6) * 1,  # 3rd
   int(i >= 7) * 1 + int(i >= 8) * 1 + int(i >= 9) * 1,  # 4th
   int(i >= 9) * 1 + int(i >= 10) * 1,  # 5th
   int(i >= 11) * 1 + int(i >= 19) * 1,  # 6th
   int(i >= 13) * 1 + int(i >= 20) * 1,  # 7th
   int(i >= 15) * 1,  # 8th
   int(i >= 17) * 1,  # 9th

] for i in range(1, 21)]


PROF = lambda level: 2 + max(((level - 1) // 4), 0)