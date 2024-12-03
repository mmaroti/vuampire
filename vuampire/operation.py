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

from .domain import Domain, Term
from .relation import Relation


class Operation:
    @typechecked
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        self.name = name
        self.domain = domain
        self.arity = arity

    @typechecked
    def declare(self) -> Iterator[str]:
        if self.arity == 0:
            yield f"tff(declare_{self.name}, type, {self.name}: {self.domain.type_name})."
        elif self.arity == 1:
            yield f"tff(declare_{self.name}, type, {self.name}: {self.domain.type_name} > {self.domain.type_name})."
        else:
            elems = " * ".join([self.domain.type_name for _ in range(self.arity)])
            yield f"tff(declare_{self.name}, type, {self.name}: ({elems}) > {self.domain.type_name})."

    @typechecked
    def __call__(self, *elems: Term) -> Term:
        assert len(elems) == self.arity
        assert all(e.domain == self.domain for e in elems)

        if not elems:
            return Term(self.domain, self.name)
        else:
            return Term(self.domain, f"{self.name}({','.join(str(e) for e in elems)})")

    @typechecked
    def is_idempotent(self) -> Term:
        assert self.arity >= 1
        return self.domain.forall(lambda x: self(*[x for _ in range(self.arity)]) == x)

    @typechecked
    def is_commutative(self) -> Term:
        assert self.arity == 2
        return self.domain.forall(lambda x, y: self(x, y) == self(y, x))

    @typechecked
    def is_associative(self) -> Term:
        assert self.arity == 2
        return self.domain.forall(lambda x, y, z: self(x, self(y, z)) == self(self(x, y), z))

    @typechecked
    def is_compatible_with(self, rel: Relation) -> Term:
        if rel.arity == 0:
            return "$true"
        elif self.arity == 0:
            return rel.contains([self.evaluate([]) for _ in rel.arity])

        def var(i: int, j: int) -> str:
            return chr(ord('A') + i) + str(j)

        vars = []
        for i in range(self.arity):
            for j in range(rel.arity):
                vars.append(var(i, j) + ":" + self.domain.type_name)
        vars = ", ".join(vars)

        pred = []
        for i in range(self.arity):
            pred.append(rel.contains([var(i, j) for j in range(rel.arity)]))

        if len(pred) >= 2:
            pred = "(" + " & ".join(pred) + ")"
        else:
            pred = pred[0]

        conc = []
        for j in range(rel.arity):
            conc.append(self.evaluate([var(i, j) for i in range(self.arity)]))
        conc = rel.contains(conc)

        return f"(![{vars}]: ({pred} => {conc}))"

    @typechecked
    def has_values(self, table: List[Optional[int]], elems: Optional[List[Term]] = None) -> Term:
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
            claims.append(self(*coord) == elems[val])

        return Term.all(claims)


class Constant(Operation):
    @typechecked
    def __init__(self, name: str, domain: Domain):
        super().__init__(name, domain, 0)
