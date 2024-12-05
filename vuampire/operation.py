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

from typing import List, Optional
from typeguard import typechecked

from .domain import Domain, Term, FixedDom, BOOLEAN
from .function import Function
from .relation import Relation


class Operation(Function):
    @typechecked
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        super().__init__(name, [domain for _ in range(arity)], domain)

    @property
    def domain(self) -> Domain:
        return self.codomain

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
    def is_surjective(self) -> Term:
        assert self.arity >= 1
        return self.domain.forall(lambda x: self.domain.exists(
            lambda *ys: Term.any([x == y for y in ys]),
            num_args=self.arity))

    @typechecked
    def is_bijective(self) -> Term:
        assert self.arity == 1
        return self.domain.forall(lambda x, y: (self(x) == self(y)).imp(x == y))

    @typechecked
    def is_compatible_with(self, rel: Relation) -> Term:
        if rel.arity == 0:
            return Term(BOOLEAN, "$true")
        elif self.arity == 0:
            val = self()
            return rel(*[val for _ in range(rel.arity)])

        def test(*vars):
            assert len(vars) == self.arity * rel.arity

            prec = []
            for i in range(0, len(vars), rel.arity):
                prec.append(rel(*vars[i: i + rel.arity]))

            vals = []
            for i in range(rel.arity):
                vals.append(self(*vars[i::rel.arity]))

            return Term.all(prec).imp(rel(*vals))

        return self.domain.forall(test, num_args=self.arity * rel.arity)

    @typechecked
    def has_values(self, table: List[Optional[Term]]) -> Term:
        assert isinstance(self.domain, FixedDom)
        elems = self.domain.elems
        assert len(table) == len(elems) ** self.arity
        assert all(t.domain == self.domain for t in table)

        claims = []
        for idx, val in enumerate(table):
            if val is None:
                continue

            coord = []
            for _ in range(self.arity):
                coord.append(elems[idx % len(elems)])
                idx //= len(elems)
            coord.reverse()
            claims.append(self(*coord) == val)

        return Term.all(claims)


class Constant(Operation):
    @typechecked
    def __init__(self, name: str, domain: Domain):
        super().__init__(name, domain, 0)
