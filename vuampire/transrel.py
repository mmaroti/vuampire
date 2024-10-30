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
from .problem import Problem
from .formula import logical_not

from typing import List


def advance(dom_size: int, table: List[bool]) -> bool:
    for i in range(dom_size):
        for j in range(dom_size):
            if j == i:
                continue

            k = i * dom_size + j
            if table[k]:
                table[k] = False
            else:
                table[k] = True
                return True

    return False


def test1():
    dom_size = 4

    table = [False] * (dom_size ** 2)
    for i in range(dom_size):
        table[i * (dom_size + 1)] = True

    while True:
        prob = Problem()

        dom = FixedDom("dom", dom_size)
        prob.declare(dom)

        rel = Relation("rel", dom, 2)
        prob.declare(rel)

        prob.require(rel.has_values(table))
        prob.require(logical_not(rel.is_transitive()))

        print()
        prob.print()
        solution = prob.find_one_model()
        print(solution, table)
        if solution is None:
            if advance(dom_size, table):
                continue
            else:
                break

        print("hihi")
        op = Operation("op", dom, 2)
        prob.declare(op)
        prob.require(logical_not(op.is_compatible_with(rel)))

        prob.require(
            "(![A:dom, B0:dom, B1:dom]: (rel(B0,B1) => rel(op(A,B0),op(A,B1))))")
        prob.require(
            "(![A:dom, B0:dom, B1:dom]: (rel(B0,B1) => rel(op(B0,A),op(B1,A))))")

        solution = prob.find_one_model()
        if solution is None:
            print(table)

        if not advance(dom_size, table):
            break


def transrel():
    test1()
