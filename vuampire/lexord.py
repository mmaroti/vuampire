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

from typing import Iterator
from typeguard import typechecked

from .domain import FixedDom, Term
from .operation import Operation
from .function import Function


class OrdDom(FixedDom):
    def __init__(self):
        super().__init__("ord", 3)

    @property
    def LT(self) -> Term:
        return self.elems[0]

    @property
    def EQ(self) -> Term:
        return self.elems[1]

    @property
    def GT(self) -> Term:
        return self.elems[2]


class OrdLex(Operation):
    def __init__(self):
        super().__init__("lex", ORDDOM, 2)

    @typechecked
    def declare(self) -> Iterator[str]:
        for line in super().declare():
            yield line

        idx = 0
        for a in ORDDOM.elems:
            for b in ORDDOM.elems:
                c = a if a.value != ORDDOM.EQ.value else b
                yield f"tff(lex_table_{idx}, axiom, {self(a, b) == c})."
                idx += 1


class OrdCmp(Function):
    def __init__(self, domain: FixedDom):
        super().__init__(f"{domain}_cmp", [domain, domain], ORDDOM)
        self.domain = domain

    @typechecked
    def declare(self) -> Iterator[str]:
        for line in super().declare():
            yield line

        idx = 0
        for i, a in enumerate(self.domain.elems):
            for j, b in enumerate(self.domain.elems):
                c = ORDDOM.LT if i < j else ORDDOM.EQ if i == j else ORDDOM.GT
                yield f"tff({self.domain}_cmp_{idx}, axiom, {self(a, b) == c})."
                idx += 1


ORDDOM = OrdDom()
ORDLEX = OrdLex()
