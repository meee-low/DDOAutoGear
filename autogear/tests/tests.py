from ddoautogear.gearset import Gearset
from ddoautogear.item import Item
from ddoautogear.gear_slots import GearSlot

def test_weapons_gearset() -> None:
    gearset = Gearset()
    dagger = Item(name="dagger", drop_location="...", effects = [],
                   equipment_slot=[GearSlot.MAIN_HAND, GearSlot.OFF_HAND], minimum_level=1)
    greatsword = Item(name="Greatsword", drop_location="...", effects = [],
                   equipment_slot=[GearSlot.MAIN_HAND], minimum_level=1)

    gearset.add_gear(dagger, GearSlot.MAIN_HAND)
    assert GearSlot.MAIN_HAND in gearset.items
    gearset.add_gear(dagger, GearSlot.OFF_HAND)
    assert GearSlot.OFF_HAND in gearset.items

    gearset.remove_gear(GearSlot.MAIN_HAND)
    assert GearSlot.MAIN_HAND not in gearset.items
    gearset.remove_gear(GearSlot.OFF_HAND)
    assert GearSlot.OFF_HAND not in gearset.items

    gearset.add_gear(greatsword, GearSlot.MAIN_HAND)
    assert GearSlot.MAIN_HAND in gearset.items
    assert GearSlot.OFF_HAND in gearset.items
    gearset.remove_gear(GearSlot.MAIN_HAND)

    assert GearSlot.MAIN_HAND not in gearset.items
    assert GearSlot.OFF_HAND not in gearset.items

    gearset.add_gear(greatsword, GearSlot.MAIN_HAND)

    gearset.remove_gear(GearSlot.OFF_HAND)

    assert GearSlot.MAIN_HAND not in gearset.items
    assert GearSlot.OFF_HAND not in gearset.items

    gearset.add_gear(dagger, GearSlot.OFF_HAND)
    assert GearSlot.OFF_HAND in gearset.items
    gearset.add_gear(greatsword, GearSlot.MAIN_HAND)
    assert GearSlot.MAIN_HAND in gearset.items
