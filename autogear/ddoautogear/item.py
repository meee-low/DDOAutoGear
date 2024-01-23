from dataclasses import dataclass
import typing
from enum import Enum, auto
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Callable, Type

from .gear_slots import GearSlot, TitleStrEnum

class AbilityScore(TitleStrEnum):
    STRENGTH = auto()
    DEXTERITY = auto()
    CONSTITUTION = auto()
    INTELLIGENCE = auto()
    WISDOM = auto()
    CHARISMA = auto()
    ALL = auto()  # TODO: make this apply to all of them

class BonusType(TitleStrEnum):
    ALCHEMICAL = auto()
    ARMOR = auto()
    ARTIFACT = auto()
    BASE = auto()
    COMPETENCE = auto()
    DEFLECTION = auto()
    DESTINY = auto()
    DETERMINATION = auto()
    ELEMENTAL_ENERGY = auto()
    ENHANCEMENT = auto()
    EQUIPMENT = auto()
    ETERNAL_FAITH = auto()
    EXCEPTIONAL = auto()
    FEAT = auto()
    GREATER_ELEMENTAL_ENERGY = auto()
    GREATER_ELEMENTAL_SPELL_POWER = auto()
    GREATER_ELEMENTAL_ENERGY2 = "GreaterElementalEnergy"
    HALLOWED = auto()
    IMPLEMENT = auto()
    INHERENT = auto()
    INSIGHTFUL = auto()
    LEGENDARY_ELEMENTAL_ENERGY = "LegendaryElementalEnergy"
    LUCK = auto()
    MORALE = auto()
    ORB = auto()
    PENALTY = auto()
    PRIMAL = auto()
    PROFANE = auto()
    QUALITY = auto()
    RAGE = auto()
    RESISTANCE = auto()
    SACRED = auto()
    SHIELD = auto()
    SILVER_FLAME = "SilverFlame"
    SIZE = auto()
    STACKING = auto()
    VITALITY = auto()

class Spellpower(TitleStrEnum):
    ACID = auto()
    ALL = auto()
    COLD = auto()
    ELECTRIC = auto()
    FIRE = auto()
    FORCE_UNTYPED = "Force/Untyped"
    LIGHT_ALIGNMENT = "Light/Alignment"
    NEGATIVE = auto()
    PHYSICAL = auto()
    POSITIVE = auto()
    REPAIR = auto()
    SONIC = auto()

class Skill(TitleStrEnum):
    ALL = auto()
    BALANCE = auto()
    BLUFF = auto()
    CONCENTRATION = auto()
    DIPLOMACY = auto()
    DISABLE_DEVICE = auto()
    HAGGLE = auto()
    HEAL = auto()
    HIDE = auto()
    INTIMIDATE = auto()
    JUMP = auto()
    LISTEN = auto()
    MOVE_SILENTLY = auto()
    OPEN_LOCK = auto()
    PERFORM = auto()
    REPAIR = auto()
    SEARCH = auto()
    SPELL_CRAFT = auto()
    SPOT = auto()
    SWIM = auto()
    TUMBLE = auto()
    UMD  = "Use Magic Device"

class SpellSchool(TitleStrEnum):
    ABJURATION = auto()
    ALL = auto()
    CONJURATION = auto()
    ENCHANTMENT = auto()
    EVOCATION = auto()
    ILLUSION = auto()
    NECROMANCY = auto()
    TRANSMUTATION = auto()

class TacticalDC(TitleStrEnum):
    ASSASSINATE = auto()
    BREATH_WEAPON = auto()
    RUNE_ARM = auto()
    STUN = auto()
    SUNDER = auto()
    TRIP = auto()

class Expansion(Enum):
    MOTU = "Menace of the Underdark",
    SHADOWFELL = "Shadowfell Conspiracy",
    RAVENLOFT = "Mists of Ravenloft",
    SHARN = "Masterminds of Sharn",
    FEYWILD = "Fables of the Feywild",
    SALTMARSH = "Secrets of Saltmarsh",
    IOD = "Isle of Dread",
    VECNA = "Vecna Unleashed"


KeyStat = typing.Union[AbilityScore, Spellpower, Skill, SpellSchool, TacticalDC, BonusType, str]


def get_content_of_xml_or_none(xml_element: ET.Element, tag: str) -> Optional[str]:
    """Returns the content of the given tag in the given xml element, or None if the tag does not exist."""
    element = xml_element.find(tag)
    if element is not None:
        return element.text
    return None

@dataclass(frozen = True)
class ItemEffect:
    type: str
    bonus: str
    amount: Optional[float]
    ability: Optional[AbilityScore] = None
    spellpower: Optional[Spellpower] = None
    skill: Optional[Skill] = None
    school: Optional[SpellSchool] = None
    tactical: Optional[TacticalDC] = None

    def key_stat(self) -> KeyStat:
        if self.ability is not None:
            return AbilityScore(self.ability)
        elif self.spellpower is not None:
            # TODO: Differentiate between spellpower and spell critical chance
            return Spellpower(self.spellpower)
        elif self.skill is not None:
            return Skill(self.skill)
        elif self.school is not None:
            return SpellSchool(self.school)
        elif self.tactical is not None:
            return TacticalDC(self.tactical)
        return self.type

    @classmethod
    def load_from_xml(cls, xml_element: ET.Element) -> "ItemEffect":
        type = get_content_of_xml_or_none(xml_element, 'Type')
        bonus = get_content_of_xml_or_none(xml_element, 'Bonus')
        amount_str = get_content_of_xml_or_none(xml_element, 'Amount')
        ability = get_content_of_xml_or_none(xml_element, 'Ability')
        spellpower_xml = get_content_of_xml_or_none(xml_element, 'SpellPower')
        skill_xml = get_content_of_xml_or_none(xml_element, 'Skill')
        school_xml = get_content_of_xml_or_none(xml_element, 'School')
        tactical_xml = get_content_of_xml_or_none(xml_element, 'Tactical')

        assert type is not None
        assert bonus is not None
        if amount_str is None:
            amount = None
        else:
            amount = float(amount_str)

        ability = AbilityScore(ability) if ability is not None else None
        spellpower = Spellpower(spellpower_xml) if spellpower_xml is not None else None
        skill = Skill(skill_xml) if skill_xml is not None else None
        school = SpellSchool(school_xml) if school_xml is not None else None
        tactical = TacticalDC(tactical_xml) if tactical_xml is not None else None
        # if only python had monads...

        return cls(type,
                   bonus,
                   amount,
                   ability,
                   spellpower,
                   skill,
                   school,
                   tactical)

    def __str__(self) -> str:
        specific = ""
        if self.ability is not None:
            specific = self.ability
        elif self.spellpower is not None:
            specific = self.spellpower
        elif self.skill is not None:
            specific = self.skill
        elif self.school is not None:
            specific = self.school
        return f"{self.amount} {self.bonus} to {self.type} ({specific})"

    def __lt__(self, other: "ItemEffect") -> bool:
        empty_if_none: Callable[[Optional[str]], str] = lambda x: "" if x is None else x # convert None to empty string
        zero_if_none: Callable[[Optional[float]], float] = lambda x: 0.0 if x is None else x # convert None to 0
        self_tuple = (self.type, self.bonus, zero_if_none(self.amount),
                      empty_if_none(self.ability), empty_if_none(self.spellpower),
                      empty_if_none(self.skill), empty_if_none(self.school), empty_if_none(self.tactical))
        other_tuple = (other.type, other.bonus, zero_if_none(other.amount),
                       empty_if_none(other.ability), empty_if_none(other.spellpower),
                       empty_if_none(other.skill), empty_if_none(other.school), empty_if_none(other.tactical))
        return self_tuple < other_tuple

@dataclass(frozen = True)
class Item:
    name: str
    drop_location: str
    effects: list[ItemEffect]
    equipment_slot: list[GearSlot]
    minimum_level: int

    def __str__(self) -> str:
        result = f"{self.name}"
        slot = self.equipment_slot[0].value if len(self.equipment_slot) == 1 else " or ".join(slot.value for slot in self.equipment_slot)
        result += f"\n  Equips to: {slot}"
        result += f"\n  Drops from: {self.drop_location}"
        result += f"\n  ML: {self.minimum_level}"
        result += f"\n  Effects:"
        result += "\n    " + "\n    ".join(str(effect) for effect in self.effects)
        return result

    def __hash__(self) -> int:
        return hash((self.name, self.drop_location, self.minimum_level, tuple(self.effects), tuple(self.equipment_slot)))

    @classmethod
    def load_from_xml(cls, xml_path: Path) -> "Item":
        xml_path = Path(xml_path)  # Ensure xml_path is a Path object
        tree = ET.parse(xml_path)
        root = tree.getroot()

        root = root.find('Item') # advance to the Item tag
        if root is None:
            raise ValueError(f"Could not find Item tag in {xml_path}")

        name = get_content_of_xml_or_none(root, 'Name')
        if name is None:
            raise ValueError(f"Could not find name in {xml_path}.")
        drop_location = get_content_of_xml_or_none(root, 'DropLocation')
        if drop_location is None:
            drop_location = ""
        effects = [ItemEffect.load_from_xml(effect) for effect in root.findall('Effect')]
        xml_slots = root.find('EquipmentSlot')
        assert xml_slots is not None
        equipment_slot = [GearSlot(slot.tag) for slot in xml_slots]
        xml_ml = get_content_of_xml_or_none(root, 'MinLevel')
        assert xml_ml is not None
        minimum_level = int(xml_ml)

        return cls(name, drop_location, effects, equipment_slot, minimum_level)


    def is_two_handed_weapon(self) -> bool:
        return GearSlot.MAIN_HAND in self.equipment_slot and GearSlot.OFF_HAND not in self.equipment_slot

