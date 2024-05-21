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

from .domain import Domain
from .problem import Item


class Relation(Item):
    def __init__(self, name: str, domain: Domain, arity: int):
        assert arity >= 0
        self.name = name
        self.domain = domain
        self.arity = arity

    @property
    def declaration(self) -> List[str]:
        if self.arity == 0:
            return [
                f"tff({self.name}_type, type, {self.name}:$o).",
            ]
        elif self.arity == 1:
            return [
                f"tff({self.name}_type, type, {self.name}:{self.domain.type_name}>$o).",
            ]
        else:
            elems = "*".join([self.domain.type_name for _ in range(self.arity)])
            return [
                f"tff({self.name}_type, type, {self.name}:({elems})>$o).",
            ]
