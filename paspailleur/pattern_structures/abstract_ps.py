from dataclasses import dataclass
from typing import TypeVar, Iterator
from bitarray import frozenbitarray as fbarray
from bitarray.util import zeros as bazeros


@dataclass
class ProjectionNotFoundError(ValueError):
    projection_number: int

    def __str__(self):
        return f"Projection #{self.projection_number} could not be computed"


class AbstractPS:
    PatternType = TypeVar('PatternType')
    bottom: PatternType  # Bottom pattern, more specific than any other one

    def join_patterns(self, a: PatternType, b: PatternType) -> PatternType:
        """Return the most precise common pattern, describing both patterns `a` and `b`"""
        raise NotImplementedError

    def iter_bin_attributes(self, data: list[PatternType]) -> Iterator[tuple[PatternType, fbarray]]:
        """Iterate binary attributes obtained from `data` (from the most general to the most precise ones)

        :parameter
            data: list[PatternType]
             list of object descriptions
        :return
            iterator of (description: PatternType, extent of the description: frozenbitarray)
        """
        raise NotImplementedError

    def is_less_precise(self, a: PatternType, b: PatternType) -> bool:
        """Return True if pattern `a` is less precise than pattern `b`"""
        return self.join_patterns(a, b) == a

    def extent(self, pattern: PatternType, data: list[PatternType]) -> Iterator[int]:
        """Return indices of rows in `data` whose description contains `pattern`"""
        return (i for i, obj_description in enumerate(data) if self.is_less_precise(pattern, obj_description))

    def intent(self, data: list[PatternType]) -> PatternType:
        """Return common pattern of all rows in `data`"""
        intent = None
        for obj_description in data:
            if intent is None:
                intent = obj_description
                continue

            intent = self.join_patterns(intent, obj_description)
        return intent

    def n_bin_attributes(self, data: list[PatternType]) -> int:
        """Count the number of attributes in the binary representation of `data`"""
        return sum(1 for _ in self.iter_bin_attributes(data))

    def binarize(self, data: list[PatternType]) -> tuple[list[PatternType], list[fbarray]]:
        """Binarize the data into Formal Context

        :parameter
            data: list[PatternType]
                List of row descriptions
        :return
            patterns: list[PatternType]
                Patterns corresponding to the attributes in the binarised data (aka binary attribute names)
            itemsets_ba: list[frozenbitarray]
                List of itemsets for every row in `data`.
                `itemsets_ba[i][j]` shows whether `data[i]` contains`patterns[j]`
        """
        patterns, flags = list(zip(*list(self.iter_bin_attributes(data))))

        n_rows, n_cols = len(flags[0]), len(flags)
        itemsets_ba = [bazeros(n_cols) for _ in range(n_rows)]
        for j, flag in enumerate(flags):
            for i in flag.itersearch(True):
                itemsets_ba[i][j] = True
        itemsets_ba = [fbarray(ba) for ba in itemsets_ba]
        return list(patterns), itemsets_ba
