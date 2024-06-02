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

import json

from .domain import FixedDom
from .relation import Relation
from .operation import Operation
from .problem import Problem


def cli():
    prob = Problem()

    dom = FixedDom("dom", 3)
    prob.declare(dom)

    rel = Relation("rel", dom, 2)
    prob.declare(rel)

    table = [True, True, False, True, True, True, True, False, True]
    prob.require(rel.has_values(table))

    op = Operation("op", dom, 2)
    prob.declare(op)
    prob.require(op.is_idempotent())
    prob.require(op.is_compatible_with(rel))

    elem = Operation("elem", dom, 0)
    prob.declare(elem)

    proj = Operation("proj", dom, 1)
    prob.declare(proj)
    prob.require("![X:dom]: proj(X)=op(elem, X)")

    # prob.print()
    # print(json.dumps(prob.find_one_model(), indent=2))
    print(prob.find_all_models(["proj"]))
