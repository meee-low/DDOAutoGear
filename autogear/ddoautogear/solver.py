import heapq
from typing import Callable, Optional
import typing
import copy
from functools import lru_cache, reduce

from ddoautogear.gear_slots import GearSlot
from ddoautogear.gearset import Gearset
from ddoautogear.all_items import ALL_ITEMS
from ddoautogear.item import Item, KeyStat
from ddoautogear import item


SlotItemDict: typing.TypeAlias = dict[GearSlot, list[Item]]

class ItemLibrary(dict[GearSlot, list[Item]]):
    def flatten(self) -> typing.Generator[Item, None, None]:
        return (item for items in self.values() for item in items)

WeightDict: typing.TypeAlias = dict[KeyStat, float]

class Evaluator:
    def __init__(self, weights: WeightDict):
        self.weights = weights
        self.filters: list[Callable[[Item], bool]] = []

    @lru_cache(maxsize=1000)
    def evaluate_item(self, item: Item) -> float:
        score = 0.0
        for effect in item.effects:
            if effect.key_stat() in self.weights and effect.amount is not None:
                score += effect.amount * self.weights[effect.key_stat()]
        return score

    @lru_cache(maxsize=1000)
    def evaluate_gearset(self, gearset: Gearset) -> float:
        # TODO: not actually how this works since duplicate effects don't stack
        return sum(self.evaluate_item(item) for item in gearset.items.values())

    def add_filter(self, fn: Callable[[Item], bool]) -> None:
        self.filters.append(fn)

    def apply_filters(self, items: SlotItemDict) -> SlotItemDict:
        """Applies all filters to the given item library. Modifications are made in-place."""
        for slot in items:
            all_filters = lambda item: all(fn(item) for fn in self.filters)
            items[slot] = list(filter(all_filters, items[slot]))
        return items

    def sort_by_score(self, item_library: SlotItemDict) -> SlotItemDict:
        """Sorts each list of items in the given item library by score. Modifications are made in-place."""
        for slot in item_library:
            item_library[slot].sort(key=self.evaluate_item, reverse=True)
        return item_library

    def adjust_weights_by_max(self, item_library: SlotItemDict) -> None:
        """Adjusts the weights of each key stat by the maximum value of that key stat in the given item library."""
        maxes: dict[KeyStat, float] = {}
        for slot in item_library:
            for item in item_library[slot]:
                for effect in item.effects:
                    if effect.key_stat() in self.weights and effect.amount is not None:
                        if effect.key_stat() not in maxes:
                            maxes[effect.key_stat()] = effect.amount
                        else:
                            maxes[effect.key_stat()] = max(maxes[effect.key_stat()], effect.amount)
        for key_stat in maxes:
            if key_stat in self.weights:
                self.weights[key_stat] /= maxes[key_stat]


class DFSSolver:
    def __init__(self, evaluator: Evaluator, possible_items: SlotItemDict):
        self.evaluator = evaluator
        self.possible_items = ItemLibrary(possible_items)
        self.memo: dict[Gearset, tuple[Optional[Gearset], float]] = {}

    def solve(self,
              depth_limit: int,
              gearset: Gearset =  Gearset(),
              best_score: float = float('-inf'),
              best_gearset: Optional[Gearset] = None
              ) -> tuple[Optional[Gearset], float]:
        """A recursive function that uses a depth-first search to find the best gearset."""
        # check if we've already solved this gearset
        if gearset in self.memo:
            return self.memo[gearset]

        open_slots = gearset.open_slots()

        # Base case: if there are no open slots, evaluate the gearset and update the best score/gearset if necessary
        if not open_slots or depth_limit == 0:
            score = self.evaluator.evaluate_gearset(gearset)
            if score > best_score:
                return gearset, score
            if best_gearset is None:
                raise ValueError("No open slots and no best gearset")
            return best_gearset, best_score

        # Recursive case: try each item in each open slot
        for slot in open_slots:
            for item in self.possible_items[slot]:
                gearset.add_gear(item, slot)
                gearset_copy = copy.deepcopy(gearset)
                best_gearset, best_score = self.solve(depth_limit-1, gearset_copy, best_score, best_gearset)
                best_gearset = copy.deepcopy(best_gearset)
                gearset.remove_gear(slot)

        return best_gearset, best_score


class FrontierSolver:
    def __init__(self, evaluator: Evaluator, possible_items: SlotItemDict):
        self.evaluator = evaluator
        self.possible_items = ItemLibrary(possible_items)

        self.frontier_size = 3

    def _calculate_best_items(self, gearset: Gearset) -> None:
        cur_score = self.evaluator.evaluate_gearset(gearset)
        def score_item(item: Item, gearset: Gearset, cur_score: float) -> float:
            gearset_copy = copy.deepcopy(gearset)
            possible_slots = [slot for slot in gearset_copy.open_slots() if slot in item.equipment_slot]
            for slot in possible_slots:
                gearset_copy.add_gear(item, slot)
            score = self.evaluator.evaluate_gearset(gearset_copy)
            return score - cur_score

        open_slots = gearset.open_slots()

        possible_items = [item for slot in open_slots for item in self.possible_items[slot]]

        self.best_items = heapq.nlargest(self.frontier_size,
                                         possible_items,
                                         key=lambda item: score_item(item, gearset, cur_score))

    def solve(self, gearset: Gearset =  Gearset(), best_score: float = float('-inf'), best_gearset: Optional[Gearset] = None) -> tuple[Optional[Gearset], float]:
        """A recursive function that uses a depth-first search to find the best gearset."""
        open_slots = gearset.open_slots()

        # Base case: if there are no open slots, evaluate the gearset and update the best score/gearset if necessary
        if not open_slots:
            score = self.evaluator.evaluate_gearset(gearset)
            if score > best_score:
                return gearset, score
            if best_gearset is None:
                raise ValueError("No open slots and no best gearset")
            return best_gearset, best_score

        # Second base case occurs when there are no more items to try
        if not any(self.possible_items[slot] for slot in open_slots):
            score = self.evaluator.evaluate_gearset(gearset)
            if score > best_score:
                return gearset, score
            if best_gearset is None:
                raise ValueError("No open slots and no best gearset")
            return best_gearset, best_score

        # Recursive case: Find the top 3 items and try them
        self._calculate_best_items(gearset)
        for item in self.best_items:
            possible_slots = [slot for slot in open_slots if slot in item.equipment_slot]
            for slot in possible_slots:
                gearset.add_gear(item, slot)
                gearset_copy = copy.deepcopy(gearset)
                best_gearset, best_score = self.solve(gearset_copy, best_score, best_gearset)
                best_gearset = copy.deepcopy(best_gearset)
                gearset.remove_gear(slot)

        return best_gearset, best_score


def main() -> None:
    possible_items = ALL_ITEMS.copy()
    weights: WeightDict = {
        item.AbilityScore.INTELLIGENCE: 100.0,
        "Doublestrike": 100.0,
        item.AbilityScore.CONSTITUTION: 90.0,
        item.Spellpower.ACID: 80.0,
        item.Spellpower.NEGATIVE: 80.0,
        item.SpellSchool.ENCHANTMENT: 90.0,
        item.SpellSchool.NECROMANCY: 70.0,
        "Magical Sheltering": 80.0,
        "Physical Sheltering": 80.0,
        "Alacrity": 30.0,
        "DodgeBonus": 50.0,
        "MovementSpeec": 30.0,
    }
    weights = {item.AbilityScore.CONSTITUTION: 100.0,}

    # slots = [GearSlot.CLOAK, GearSlot.NECKLACE, GearSlot.GOGGLES]
    slots = [GearSlot(gs) for gs in list(GearSlot)]
    # slots = GearSlot.all_slots()
    evaluator = Evaluator(weights)
    evaluator.add_filter(lambda item: item.minimum_level >= 28)
    evaluator.add_filter(lambda item: any(slot in slots for slot in item.equipment_slot))
    evaluator.add_filter(lambda item: evaluator.evaluate_item(item) > 0)

    test_gearset = Gearset(slots)

    evaluator.apply_filters(possible_items)
    evaluator.adjust_weights_by_max(possible_items)
    evaluator.sort_by_score(possible_items)

    print("Number of possible items: ", sum(len(items) for items in possible_items.values()))
    prod = reduce(lambda x, y: x * y, (len(items) for items in possible_items.values() if len(items) > 0))
    print(f"Possible gearsets: {prod}")
    for slot in possible_items:
        print(slot, len(possible_items[slot]))
        for item_ in possible_items[slot]:
            item_str = str(item_)
            item_str = "\n    ".join(item_str.split("\n"))
            print("   ", item_str)
            print()

    print("======")
    solver = DFSSolver(evaluator, possible_items)
    gearset, score = solver.solve(1, test_gearset)
    # solver = FrontierSolver(evaluator, possible_items)
    # solver.frontier_size = 2
    # gearset, score = solver.solve(test_gearset)
    print(gearset)
    print("======")

if __name__ == "__main__":
    main()
