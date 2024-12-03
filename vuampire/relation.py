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
from typeguard import typechecked

from .domain import Domain, Term, BOOLEAN


class Relation:
    @typechecked
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        self.domain = domain
        self.arity = arity
        self.name = name

    @typechecked
    def declare(self) -> Iterator[str]:
        if self.arity == 0:
            yield f"tff(declare_{self.name}, type, {self.name}: $o)."
        elif self.arity == 1:
            yield f"tff(declare_{self.name}, type, {self.name}: {self.domain.type_name} > $o)."
        else:
            elems = " * ".join([self.domain.type_name for _ in range(self.arity)])
            yield f"tff(declare_{self.name}, type, {self.name}: ({elems}) > $o)."

    @typechecked
    def __call__(self, *elems: Term) -> Term:
        assert len(elems) == self.arity
        assert all(e.domain == self.domain for e in elems)

        if self.arity == 0:
            return Term(BOOLEAN, self.name)
        else:
            return Term(BOOLEAN, f"{self.name}({','.join(str(e) for e in elems)})")

    @typechecked
    def is_reflexive(self) -> Term:
        if self.arity == 0:
            return Term(BOOLEAN, self.name)
        else:
            return self.domain.forall(lambda x: self(*[x for _ in range(self.arity)]))

    @typechecked
    def is_symmetric(self) -> Term:
        assert self.arity == 2
        return self.domain.forall(lambda x, y: self(x, y).imp(self(y, x)))

    @typechecked
    def is_antisymmetric(self) -> Term:
        assert self.arity == 2
        return self.domain.forall(lambda x, y: (self(x, y) & self(y, x)).imp(x == y))

    @typechecked
    def is_transitive(self) -> Term:
        assert self.arity == 2
        return self.domain.forall(lambda x, y, z: (self(x, y) & self(y, z)).imp(self(x, z)))

    @typechecked
    def is_quasiorder(self) -> Term:
        assert self.arity == 2
        return self.is_reflexive() & self.is_transitive()

    @typechecked
    def is_partialorder(self) -> Term:
        assert self.arity == 2
        return self.is_quasiorder() & self.is_antisymmetric()

    @typechecked
    def is_equivalence(self) -> Term:
        assert self.arity == 2
        return self.is_quasiorder() & self.is_symmetric()

    @typechecked
    def has_values(self,
                   table: List[Optional[bool]],
                   elems: Optional[List[Term]] = None) -> Term:
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
            claim = self(*coord)
            if not val:
                claim = ~claim
            claims.append(claim)

        return Term.all(claims)
