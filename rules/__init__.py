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


STAT = ty.Literal["STR", "DEX", "CON", "INT", "WIS", "CHA"]


class STATBLOCK(ty.TypedDict):
   STR: _STAT
   DEX: _STAT
   CON: _STAT
   INT: _STAT
   WIS: _STAT
   CHA: _STAT


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
