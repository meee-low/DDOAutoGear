
from dataclasses import dataclass, field
import dataclasses

from ddoautogear.gear_slots import GearSlot
from ddoautogear.item import Item

@dataclass
class Gearset:
    gear_slots: list[GearSlot] = field(default_factory=lambda: GearSlot.all_slots())
    items: dict[GearSlot, Item] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(frozenset(self.items.items()))

    def add_gear(self, gear: Item, slot: GearSlot) -> None:
        if slot in self.items:
            raise ValueError(f"Gearset already has an item in slot {slot}")
        if slot == GearSlot.OFF_HAND or slot == GearSlot.MAIN_HAND:
            if self.is_wielding_two_handed_weapon():
                raise ValueError(f"Cannot equip {gear.name} in slot {slot} because you are wielding a two-handed weapon.")
            if gear.is_two_handed_weapon():
                self.items[GearSlot.MAIN_HAND] = gear
                self.items[GearSlot.OFF_HAND] = gear

        self.items[slot] = gear

    def remove_gear(self, slot: GearSlot) -> None:
        if slot not in self.items:
            raise ValueError(f"Gearset does not have an item in slot {slot}")
        item = self.items[slot]
        if item.is_two_handed_weapon():
            del self.items[GearSlot.MAIN_HAND]
            del self.items[GearSlot.OFF_HAND]
        else:
            del self.items[slot]


    def open_slots(self) -> list[GearSlot]:
        slots = [slot for slot in self.gear_slots if slot not in self.items]

        return slots

    def is_wielding_two_handed_weapon(self) -> bool:
        main_hand = self.items.get(GearSlot.MAIN_HAND)
        off_hand = self.items.get(GearSlot.OFF_HAND)

        if main_hand is not None:
            return main_hand.is_two_handed_weapon()
        elif off_hand is not None:
            return off_hand.is_two_handed_weapon()
        return False  # No weapon equipped

    def __str__(self) -> str:
        result = ""
        for slot in self.gear_slots:
            if slot in self.items:
                result += f"{slot}: {self.items[slot].name}\n"
            else:
                result += f"{slot}: None\n"
        return result