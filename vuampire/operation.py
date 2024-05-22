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

from .domain import Domain


class Operation:
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        self.name = name
        self.domain = domain
        self.arity = arity

    def declare(self) -> Iterator[str]:
        if self.arity == 0:
            yield f"tff({self.name}_type, type, {self.name}: {self.domain.type_name})."
        elif self.arity == 1:
            yield f"tff({self.name}_type, type, {self.name}: {self.domain.type_name} > {self.domain.type_name})."
        else:
            elems = " * ".join([self.domain.type_name for _ in range(self.arity)])
            yield f"tff({self.name}_type, type, {self.name}: ({elems}) > {self.domain.type_name})."

    def evaluate(self, elems: List[str]) -> str:
        assert len(elems) == self.arity
        if not elems:
            return self.name
        else:
            return f"{self.name}({','.join(elems)})"

    def is_idempotent(self) -> str:
        assert self.arity >= 1
        return f"![X:{self.domain.type_name}]: {self.evaluate(['X' for _ in range(self.arity)])} = X"

    def is_commutative(self) -> str:
        assert self.arity == 2
        return f"![X:{self.domain.type_name}, Y:{self.domain.type_name}]: " \
            f"{self.evaluate(['X', 'Y'])} = {self.evaluate(['Y', 'X'])}"

    def is_associative(self) -> str:
        assert self.arity == 2
        return f"![X:{self.domain.type_name}, Y:{self.domain.type_name}, Z:{self.domain.type_name}]: " \
            f"{self.evaluate(['X', self.evaluate(['Y', 'Z'])])} = " \
            f"{self.evaluate([self.evaluate(['X', 'Y']), 'Z'])}"


class Constant(Operation):
    def __init__(self, name: str, domain: Domain):
        super().__init__(name, domain, 0)
