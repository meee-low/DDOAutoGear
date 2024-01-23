import pickle
from ddoautogear.gear_slots import GearSlot
from ddoautogear.item import Item, ItemEffect




def categorize_effects(items: list[Item]) -> set[ItemEffect]:
    """Returns a set of ItemEffects that are present in the given list of items."""
    effects: set[ItemEffect] = set()
    for item in items:
        for effect in item.effects:
            # create new effect with amount = None so that we can compare effects
            new_effect = ItemEffect(effect.type, effect.bonus, None, effect.ability, effect.spellpower, effect.skill, effect.school, effect.tactical)
            effects.add(new_effect)
    return effects

def categorize_items_by_slot(items: list[Item]) -> dict[GearSlot, list[Item]]:
    """Returns a dictionary mapping GearSlots to lists of items that can go in that slot."""
    items_by_slot: dict[GearSlot, list[Item]] = {}
    for item in items:
        for slot in item.equipment_slot:
            if slot not in items_by_slot:
                items_by_slot[slot] = []
            items_by_slot[slot].append(item)
    return items_by_slot


_items_list = pickle.load(open('all_items.pickle', 'rb'))
ALL_ITEMS: dict[GearSlot, list[Item]] = categorize_items_by_slot(_items_list)

def main() -> None:
    import pickle
    import csv
    import dataclasses
    with open('all_items.pickle', 'rb') as f:
        all_items = pickle.load(f)

    effects = sorted(categorize_effects(all_items))
    # write the csv header:
    with open('all_effects.csv', 'w', newline='') as csvfile:
        fieldnames = dataclasses.asdict(effects[0]).keys()
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        # write the csv data:
        for effect in effects:
            csv_writer.writerow(dataclasses.asdict(effect))

if __name__ == "__main__":
    main()