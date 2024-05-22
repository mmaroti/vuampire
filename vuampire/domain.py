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
        yield f"tff({self.name}_type, type, {self.name}:$tType)."


class FixedDom(Domain):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

        self.elems = [f"{name}_{i}" for i in range(size)]

    @property
    def type_name(self) -> str:
        return self.name

    def declare(self) -> Iterator[str]:
        yield f"tff({self.name}_type, type, {self.name}: $tType)."

        for i in range(self.size):
            yield f"tff({self.elems[i]}_elem, type, {self.elems[i]}: {self.type_name})."

        yield f"tff({self.name}_elements, axiom, ![X:{self.type_name}]: " \
            f"({' | '.join([f'X={e}' for e in self.elems])}))."

        yield f"tff({self.name}_distinct, axiom, $distinct({', '.join(self.elems)}))."
