# Copyright (C) 2024, Miklos Maroti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Iterator, List, Optional

from .domain import Domain
from .formula import logical_and


class Relation:
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        self.domain = domain
        self.arity = arity
        self.name = name

    def declare(self) -> Iterator[str]:
        if self.arity == 0:
            yield f"tff(declare_{self.name}, type, {self.name}: $o)."
        elif self.arity == 1:
            yield f"tff(declare_{self.name}, type, {self.name}: {self.domain.type_name} > $o)."
        else:
            elems = " * ".join([self.domain.type_name for _ in range(self.arity)])
            yield f"tff(declare_{self.name}, type, {self.name}: ({elems}) > $o)."

    def contains(self, elems: List[str]) -> str:
        assert len(elems) == self.arity
        if self.arity == 0:
            return self.name
        else:
            return f"{self.name}({','.join(elems)})"

    def is_reflexive(self) -> str:
        if self.arity == 0:
            return self.contains([])
        else:
            return f"(![X:{self.domain.type_name}]: {self.contains(['X' for _ in range(self.arity)])})"

    def is_symmetric(self) -> str:
        assert self.arity == 2
        return f"(![X:{self.domain.type_name}, Y:{self.domain.type_name}]: " \
            f"({self.contains(['X', 'Y'])} => {self.contains(['Y', 'X'])}))"

    def is_antisymmetric(self) -> str:
        assert self.arity == 2
        return f"(![X:{self.domain.type_name}, Y:{self.domain.type_name}]: " \
            f"(({self.contains(['X', 'Y'])} & {
            self.contains(['Y', 'X'])}) => X=Y))"

    def is_transitive(self) -> str:
        assert self.arity == 2
        return f"(![X:{self.domain.type_name}, Y:{self.domain.type_name}, Z:{self.domain.type_name}]: " \
            f"(({self.contains(['X', 'Y'])} & {self.contains(['Y', 'Z'])}) => {
            self.contains(['X', 'Z'])}))"

    def is_quasiorder(self) -> str:
        assert self.arity == 2
        return logical_and([self.is_reflexive(), self.is_transitive()])

    def is_partialorder(self) -> str:
        assert self.arity == 2
        return logical_and([self.is_reflexive(), self.is_antisymmetric(), self.is_transitive()])

    def is_equivalence(self) -> str:
        assert self.arity == 2
        return logical_and([self.is_reflexive(), self.is_symmetric(), self.is_transitive()])

    def has_values(self, table: List[Optional[bool]], elems: Optional[List[str]] = None) -> str:
        if elems is None:
            elems = self.domain.elems
        assert len(table) == len(elems) ** self.arity

        claims = []
        for idx, val in enumerate(table):
            if val is None:
                continue

            coord = []
            for _ in range(self.arity):
                coord.append(elems[idx % len(elems)])
                idx //= len(elems)
            coord.reverse()
            claims.append(("" if val else "~") + self.contains(coord))

        return logical_and(claims)
