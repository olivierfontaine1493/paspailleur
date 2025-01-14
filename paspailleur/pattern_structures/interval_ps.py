from typing import Iterator, Optional
from bitarray import frozenbitarray as fbarray
from .abstract_ps import AbstractPS


class IntervalPS(AbstractPS):
    PatternType = Optional[tuple[float, float]]
    bottom = None  # Bottom pattern, more specific than any other one

    def join_patterns(self, a: PatternType, b: PatternType) -> PatternType:
        """Return the most precise common pattern, describing both patterns `a` and `b`"""
        if a is self.bottom:
            return b
        if b is self.bottom:
            return a

        return min(a[0], b[0]), max(a[1], b[1])

    def iter_bin_attributes(self, data: list[PatternType]) -> Iterator[tuple[PatternType, fbarray]]:
        """Iterate binary attributes obtained from `data` (from the most general to the most precise ones)

        :parameter
            data: list[PatternType]
             list of object descriptions
        :return
            iterator of (description: PatternType, extent of the description: frozenbitarray)
        """
        lower_bounds, upper_bounds = [sorted(set(bounds)) for bounds in zip(*data)]
        min_, max_ = lower_bounds[0], upper_bounds[-1]
        lower_bounds.pop(0)
        upper_bounds.pop(-1)

        yield (min_, max_), fbarray([True]*len(data))

        for lb in lower_bounds:
            yield (lb, max_), fbarray((lb <= x for x, _ in data))

        for ub in upper_bounds[::-1]:
            yield (min_, ub), fbarray((x <= ub for _, x in data))

        yield None, fbarray([False]*len(data))

    def is_less_precise(self, a: PatternType, b: PatternType) -> bool:
        """Return True if pattern `a` is less precise than pattern `b`"""
        if b is self.bottom:
            return True

        if a is self.bottom:
            return False

        return a[0] <= b[0] <= b[1] <= a[1]

    def n_bin_attributes(self, data: list[PatternType]) -> int:
        """Count the number of attributes in the binary representation of `data`"""
        return len({lb for lb, ub in data}) + len({ub for ub in data})
