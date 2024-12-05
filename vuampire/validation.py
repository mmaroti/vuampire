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

import click

from .problem import Problem
from .domain import FixedDom
from .relation import Relation
from .operation import Operation


def check_equivalence_relations(size: int, expected: int):
    print(f"Number of {size}-element equivalence relations is: ",
          end="", flush=True)

    prob = Problem()

    dom = FixedDom("dom", size)
    prob.declare(dom)

    rel = Relation("rel", dom, 2)
    prob.declare(rel)

    prob.require(rel.is_equivalence())

    count = prob.find_num_models(["rel"])

    print(count)
    assert count == expected


def check_partial_orders(size: int, expected: int):
    print(f"Number of {size}-element partial orders is: ", end="", flush=True)

    prob = Problem()

    dom = FixedDom("dom", size)
    prob.declare(dom)

    rel = Relation("rel", dom, 2)
    prob.declare(rel)

    prob.require(rel.is_partialorder())

    count = prob.find_num_models(["rel"])

    print(count)
    assert count == expected


def check_semigroups(size: int, expected: int):
    print(f"Number of {size}-element semigroups is: ", end="", flush=True)

    prob = Problem()

    dom = FixedDom("dom", size)
    prob.declare(dom)

    op = Operation("op", dom, 2)
    prob.declare(op)

    prob.require(op.is_associative())

    count = prob.find_num_models(["op"])

    print(count)
    assert count == expected


def check_semilattices(size: int, expected: int):
    print(f"Number of {size}-element semilattices is: ", end="", flush=True)

    prob = Problem()

    dom = FixedDom("dom", size)
    prob.declare(dom)

    op = Operation("op", dom, 2)
    prob.declare(op)

    prob.require(op.is_idempotent())
    prob.require(op.is_commutative())
    prob.require(op.is_associative())

    count = prob.find_num_models(["op"])

    print(count)
    assert count == expected


def check_petersen_automorphisms():
    print(f"Number of automorphisms of the Petersen graph is: ",
          end="", flush=True)

    prob = Problem()

    dom = FixedDom("dom", 10)
    prob.declare(dom)

    rel = Relation("rel", dom, 2)
    prob.declare(rel)

    table = [False for _ in range(100)]

    def set(i, j):
        assert 0 <= i < 10 and 0 <= j < 10
        table[i * 10 + j] = True
        table[j * 10 + i] = True

    for i in range(5):
        set(i, (i + 1) % 5)
        set(i, i + 5)
        set(i + 5, (i + 2) % 5 + 5)

    prob.require(rel.has_values(table))

    aut = Operation("aut", dom, 1)
    prob.declare(aut)

    prob.require(aut.is_bijective())
    prob.require(aut.is_compatible_with(rel))

    count = prob.find_num_models(["aut"])

    print(count)
    assert count == 120


@click.command()
def validate():
    check_equivalence_relations(5, 52)
    check_partial_orders(3, 19)
    check_semigroups(3, 113)
    check_semilattices(4, 76)
    check_petersen_automorphisms()
