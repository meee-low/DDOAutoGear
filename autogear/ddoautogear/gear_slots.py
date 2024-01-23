from enum import StrEnum, auto

class TitleStrEnum(StrEnum):
    # TODO: move this out of here
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        name = name.replace("_", " ")
        return name.title()

class GearSlot(TitleStrEnum):
    BELT = auto()
    BOOTS = auto()
    BRACERS = auto()
    CLOAK = auto()
    GLOVES = auto()
    GOGGLES = auto()
    HELMET = auto()
    NECKLACE = auto()
    RING = auto()
    TRINKET = auto()
    ARMOR = auto()
    MAIN_HAND = "Weapon1"
    OFF_HAND = "Weapon2"
    ARROW = auto()
    QUIVER = auto()

    @staticmethod
    def all_slots() -> list["GearSlot"]:
        return sorted([slot for slot in GearSlot] + [GearSlot.RING])
