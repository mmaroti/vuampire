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

from typing import Iterator, List
from typeguard import typechecked

from .domain import Domain, Term


class Function:
    @typechecked
    def __init__(self, name: str, domains: List[Domain], codomain: Domain):
        self.name = name
        self.domains = domains
        self.codomain = codomain

    @typechecked
    def __str__(self) -> str:
        return self.name

    @property
    @typechecked
    def arity(self) -> int:
        return len(self.domains)

    @typechecked
    def declare(self) -> Iterator[str]:
        if self.arity == 0:
            yield f"tff(declare_{self}, type, {self}: {self.codomain})."
        elif self.arity == 1:
            yield f"tff(declare_{self}, type, {self}: {self.domains[0]} > {self.codomain})."
        else:
            domains = " * ".join([str(d) for d in self.domains])
            yield f"tff(declare_{self}, type, {self}: ({domains}) > {self.codomain})."

    @typechecked
    def __call__(self, *elems: Term) -> Term:
        assert len(elems) == self.arity
        assert all(e.domain == d for (e, d) in zip(elems, self.domains))

        if self.arity == 0:
            return Term(self.codomain, self.name)
        else:
            return Term(self.codomain, f"{self.name}({','.join(str(e) for e in elems)})")
