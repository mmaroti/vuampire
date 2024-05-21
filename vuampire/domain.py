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

from typing import List

from .problem import Item


class Domain(Item):
    def __init__(self, name: str):
        self.name = name

    @property
    def declaration(self) -> List[str]:
        return [
            f"tff({self.name}_type, type, {self.name}:$tType).",
        ]

    @property
    def type_name(self) -> str:
        return self.name


class FixedDomain(Domain):
    def __init__(self, name: str, size: int):
        assert size >= 1
        super().__init__(name)
        self.size = size

    def elem_name(self, index: int) -> str:
        assert 0 <= index < self.size
        return f"{self.name}_{index}"

    @property
    def declaration(self) -> List[str]:
        result: List[str] = super().declaration
        for i in range(self.size):
            result.append(
                f"tff({self.elem_name(i)}_elem, type, {self.elem_name(i)}:{self.type_name})."
            )
        elems = " | ".join(
            [f"X={self.elem_name(i)}" for i in range(self.size)])
        result.append(
            f"tff({self.name}_finite, axiom, ![X:{self.type_name}]: ({elems}))."
        )
        elems = ", ".join([self.elem_name(i) for i in range(self.size)])
        result.append(
            f"tff({self.name}_distinct, axiom, $distinct({elems}))."
        )
        return result
