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


class Domain:
    @property
    def type_name(self) -> str:
        raise NotImplementedError()


class PrimitiveDom(Domain):
    def __init__(self, name: str):
        self.name = name

    @property
    def type_name(self) -> str:
        return self.name

    def declare(self) -> Iterator[str]:
        if False:
            yield


UNIVERSE = PrimitiveDom("$i")
BOOLEAN = PrimitiveDom("$o")
INTEGER = PrimitiveDom("$int")


class NamedDom(Domain):
    def __init__(self, name: str):
        self.name = name

    @property
    def type_name(self) -> str:
        return self.name

    def declare(self) -> Iterator[str]:
        yield f"tff(declared_{self.name}, type, {self.name}:$tType)."


class FixedDom(NamedDom):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size
        self.elems = [f"{name}{i}" for i in range(size)]

    def declare(self) -> Iterator[str]:
        for line in super().declare():
            yield line

        for i in range(self.size):
            yield f"tff(declare_{self.elems[i]}, type, {self.elems[i]}: {self.type_name})."

        yield f"tff({self.name}_elements, axiom, ![X:{self.type_name}]: " \
            f"({' | '.join([f'X={e}' for e in self.elems])}))."

        yield f"tff({self.name}_distinct, axiom, $distinct({', '.join(self.elems)}))."


class ProductDom(Domain):
    def __init__(self, domain: Domain, arity: int):
        assert arity >= 0
        self.domain = domain
        self.arity = arity
