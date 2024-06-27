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

from .domain import FixedDom, NamedDom
from .relation import Relation
from .operation import Operation, Constant
from .problem import Problem


def test1():
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


def test2():
    prob = Problem()

    d = NamedDom("d")
    prob.declare(d)

    d0 = Constant("d0", d)
    prob.declare(d0)

    d1 = Constant("d1", d)
    prob.declare(d1)

    d2 = Constant("d2", d)
    prob.declare(d2)

    prob.require("$distinct(d0, d1, d2)")

    r = Relation("r", d, 2)
    prob.declare(r)
    prob.require("![X:d]: r(X,X)")
    prob.require(
        "r(d0,d1) & r(d1,d0) & r(d1,d2) & ~r(d2,d1) & r(d2,d0) & ~r(d0,d2)")

    f = Operation("f", d, 2)
    prob.declare(f)
    prob.require(f.is_idempotent())
    prob.require(f.is_compatible_with(r))

    s = FixedDom("s", 9)
    prob.declare(s)

    e = Relation("e", s, 2)
    prob.declare(e)
    prob.require(e.is_equivalence())

    for i in range(9):
        x = "s" + str(i)
        x0 = "d" + str(i % 3)
        x1 = "d" + str(i // 3)
        for j in range(i + 1, 9):
            y = "s" + str(j)
            y0 = "d" + str(j % 3)
            y1 = "d" + str(j // 3)

            prob.require(f"e({x},{y}) <=> f({x0},{x1})=f({y0},{y1})")

    # prob.print()
    # print(prob.find_one_model())
    print(prob.find_all_models(["e"]))


def test3():
    prob = Problem()

    d = NamedDom("d")
    prob.declare(d)

    d0 = Constant("d0", d)
    prob.declare(d0)

    d1 = Constant("d1", d)
    prob.declare(d1)

    d2 = Constant("d2", d)
    prob.declare(d2)

    prob.require("$distinct(d0, d1, d2)")

    r = Relation("r", d, 2)
    prob.declare(r)
    prob.require("![X:d]: r(X,X)")
    prob.require(
        "r(d0,d1) & r(d1,d0) & r(d1,d2) & ~r(d2,d1) & r(d2,d0) & ~r(d0,d2)")

    f = Operation("f", d, 2)
    prob.declare(f)
    prob.require(f.is_idempotent())
    prob.require(f.is_compatible_with(r))

    g1 = Relation("g1", d, 1)
    prob.declare(g1)
    prob.require("![X:d]: (g1(X) <=> (X=d0 | X=d1 | X=d2))")

    g2 = Relation("g2", d, 1)
    prob.declare(g2)
    prob.require("![X:d]: (g2(X) <=> (?[Y:d,Z:d]: (g1(Y) & g1(Z) & f(Y,Z)=X)))")

    # g3 = Relation("g3", d, 1)
    # prob.declare(g3)
    # prob.require("![X:d]: (g3(X) <=> (?[Y:d,Z:d]: (g2(Y) & g2(Z) & f(Y,Z)=X)))")

    # prob.require("![X:d]: g3(X)")

    e1 = Relation("e1", d, 2)
    prob.declare(e1)
    prob.require("![X:d,Y:d]: (e1(X,Y) <=> (r(X,Y) & r(Y,X)))")

    e2 = Relation("e2", d, 2)
    prob.declare(e2)
    prob.require("![X:d,Y:d]: (e2(X,Y) <=> (?[Z:d]: (e1(X,Z) & e1(Z,Y))))")

    e3 = Relation("e3", d, 2)
    prob.declare(e3)
    prob.require("![X:d,Y:d]: (e3(X,Y) <=> (?[Z:d]: (e2(X,Z) & e2(Z,Y))))")

    s1 = Relation("s1", d, 1)
    prob.declare(s1)
    prob.require("![X:d]: (s1(X) <=> (g2(X) & r(X,d2) & r(d2,X)))")

    s2 = Relation("s2", d, 1)
    prob.declare(s2)
    prob.require("![X:d]: (s2(X) <=> (g2(X) & ?[Y:d,Z:d]: (s1(Y) & s1(Z) & r(X,Y) & r(Z,X))))")

    # s3 = Relation("s3", d, 1)
    # prob.declare(s3)
    # prob.require("![X:d]: (s3(X) <=> (g2(X) & ?[Y:d,Z:d]: (s2(Y) & s2(Z) & r(X,Y) & r(Z,X))))")

    prob.require("?[X:d]: (s2(X) & ~e3(X,d2))")

    prob.print()
    # print(prob.find_one_model())
    # print(prob.find_all_models(["e"]))

def cli():
    test3()
