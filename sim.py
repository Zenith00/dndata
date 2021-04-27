from entity import Player
from rules import STATBLOCK
from simulator import attack
# STARRY_ARCHER = AttackPlusMod(stat=STAT.WIS, damage=3.5)
# GUIDING_BOLT = Attack(14, start=0, n=2)
# PRODUCE_FLAME = Attack(stat=STAT.WIS, base=4.5, start=2)
#
# SCIMITAR = AttackPlusMod(STAT.DEX, damage=3.5)
# UNLEASH = AttackPlusMod(STAT.DEX, damage=3.5, start=0, n=3)
#
# MAGICMISSLE_1 = Damager(10.5, start=3, n=4)
# MAGICMISSLE_2 = Damager(14, start=0, n=3)
#
# ELDRITCH_BLAST = AttackPlusMod(STAT.DEX, damage=5.5)
# HEX = Damager(3.5)
# HB_CURSE = Damager(2)
#
# TOLLTHEDEAD = SaveOrHalf(STAT.WIS, damage=6.5)

import pathlib
#          "starry_archer": attack.STARRY_ARCHER,
#          "guiding_bolt" : attack.GUIDING_BOLT,
#          "produce_flame": attack.PRODUCE_FLAME
#       }),
#       Player("Dasc", 0, 3, 17, [9,16,16,10,12,12], CLS_SAVE["fighter"],  {
#          "scimL"  : attack.SCIMITAR,
#          "scimR"  : attack.SCIMITAR,
#          "unleash": attack.UNLEASH
#       }),
#       Player("Zeno", 0, 4, 17, [8,14,10,18,12,12], CLS_SAVE["wizard"], {
#          "mm_1": attack.MAGICMISSLE_1,
#          "mm_2": attack.MAGICMISSLE_2
#       }),
#       Player("Ari", 0, 5, 17, [8,12,14,10,12,20], CLS_SAVE["warlock"], {
#          "eb" : attack.ELDRITCH_BLAST,
#          "hex": attack.HEX,
#          "hbc": attack.HB_CURSE.delay(1)
#       }),
#       Player("Izera", 0, 4, 17, [7, 14, 14, 13, 18, 8], CLS_SAVE["cleric"], {
#          "eb" : attack.TOLLTHEDEAD,


BERTILAK = Player.fromJSON(pathlib.Path("./data/characters/fvtt-Actor-Bertilak.json").read_text(),
                        attacks={"starry_archer": attack.AttackPlusMod("SPELL",base=4.5),
                                 "guiding_bolt":attack.Attack("SPELL", base=14, start=0, n=-2),
                                 "quarterstaff":attack.Attack("STR", base=4.5, start=2)})
