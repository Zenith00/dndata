from . import Party, Player
from ..rules import CL



PURPLE_CORP = Party([
Player("Aqwig",[CL.DRUID(5)])
])



# PURPLE_CORP = Party(
#    [
#
#       Player("Aqwig", [16,12,13,14,10,10], rules.CLASS_SAVE_PROFS["druid"], {
#
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
#       })
#    ]
#    , 4)
