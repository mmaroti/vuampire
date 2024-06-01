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

    rel0 = Relation("rel0", dom, 0)
    prob.declare(rel0)
    prob.require("hihi", rel0.is_reflexive())

    rel1 = Relation("rel1", dom, 1)
    prob.declare(rel1)

    rel2 = Relation("rel2", dom, 2)
    prob.declare(rel2)

    table = [True, True, False, True, True, True, True, False, True]
    prob.require("rel_table", rel2.has_values(table))

    op0 = Operation("op0", dom, 0)
    prob.declare(op0)

    op1 = Operation("op1", dom, 1)
    prob.declare(op1)
    prob.require("haha", op1.is_idempotent())
    prob.require("hehe", "op0=op1(dom_0)")

    op2 = Operation("op2", dom, 2)
    prob.declare(op2)

    prob.require("idempotent", op2.is_idempotent())
    prob.require("compatible", op2.is_compatible_with(rel2))
    table = [None, 'dom_1', 'dom_1', None]
    prob.require("op_table", op2.has_values(table, ['dom_0', 'dom_1']))

    # prob.print()
    print(json.dumps(prob.find_one_model(), indent=2))
    # print(prob.find_one_model())
