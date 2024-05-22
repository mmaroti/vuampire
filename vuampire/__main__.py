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

from .domain import FixedDom
from .relation import Relation
from .operation import Operation


def cli():
    dom = FixedDom("dom", 3)
    for line in dom.declare():
        print(line)

    rel = Relation("rel", dom, 2)
    for line in rel.declare():
        print(line)
    print(f"tff(reflexive, axiom, {rel.is_reflexive()}).")
    print(f"tff(symmetric, axiom, {rel.is_symmetric()}).")
    print(f"tff(transitive, axiom, {rel.is_transitive()}).")

    op = Operation("op", dom, 2)
    for line in op.declare():
        print(line)
    print(f"tff(idempotent, axiom, {op.is_idempotent()}).")
    print(f"tff(commutative, axiom, {op.is_commutative()}).")
    print(f"tff(associative, axiom, {op.is_associative()}).")
