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

import re
import subprocess
from typing import Dict, List, Iterator

from .domain import Domain
from .relation import Relation
from .operation import Operation


class Problem:
    def __init__(self):
        self.domains: Dict[str, Domain] = {}
        self.relations: Dict[str, Relation] = {}
        self.operations: Dict[str, Operation] = {}
        self.lines: List[str] = []

    def declare(self, obj: Domain | Relation | Operation):
        if isinstance(obj, Domain):
            assert obj.type_name not in self.domains
            self.domains[obj.type_name] = obj
        elif isinstance(obj, Relation):
            assert obj.name not in self.relations
            self.relations[obj.name] = obj
        elif isinstance(obj, Operation):
            assert obj.name not in self.operations
            self.operations[obj.name] = obj
        else:
            raise ValueError()

        for line in obj.declare():
            self.lines.append(line)

    def require(self, formula: str):
        if formula.startswith("(") and formula.endswith(")"):
            formula = formula[1:-1]
        name = "axiom" + str(len(self.lines))
        self.lines.append(f"tff({name}, axiom, {formula}).")

    def print(self):
        for line in self.lines:
            print(line)

    def execute(self, *options: List[str]) -> str:
        input = "\n".join(self.lines)
        result: subprocess.CompletedProcess = subprocess.run(
            args=("vampire", ) + options,
            input=input,
            text=True,
            capture_output=True,
        )
        if result.returncode:
            print(result.stdout)
            raise RuntimeError(f"failed with {result.returncode} error code")
        return result.stdout

    RE_STATEMENT = re.compile(
        r"^tff\(([\w\s]*),([\w\s]*),([^.]*)\)\.$", flags=re.MULTILINE | re.DOTALL)
    RE_REMOVE_COMMENT = re.compile(r"^%.*$", flags=re.MULTILINE)
    RE_REMOVE_SPACE = re.compile(r"\s")
    RE_DOMAIN_DECL = re.compile(r"^(\w*):\$tType$")
    RE_PREDICATE_DECL = re.compile(r"^(\w*):(?:|\((.*)\)>)\$o$")
    RE_FUNCTION_DECL = re.compile(r"^(\w*):(?:|\((.*)\)>)(\w*)$")
    RE_FINITE_DOM = re.compile(r"^!\[X:(\w*)\]:\((.*)\)$")

    def find_one_model(self) -> Dict:
        result = self.execute("-sa", "fmb", "-fde", "none")
        if not "Finite Model Found!" in result:
            return None

        domains: Dict[str, List[str]] = {}
        predicates = {}
        functions = {}

        for match in Problem.RE_STATEMENT.finditer(result):
            formula = Problem.RE_REMOVE_COMMENT.sub("", match.group(3))
            formula = Problem.RE_REMOVE_SPACE.sub("", formula)
            # print(">" + formula + "<")

            if match.group(2) == "type":
                match2 = Problem.RE_DOMAIN_DECL.match(formula)
                if match2:
                    name = match2.group(1)
                    assert name not in domains
                    domains[name] = []
                    continue

                match2 = Problem.RE_PREDICATE_DECL.match(formula)
                if match2:
                    name = match2.group(1)
                    doms = match2.group(2)
                    if doms is None:
                        doms = []
                    else:
                        doms = doms.split("*")
                    size = 1
                    for dom in doms:
                        size *= len(domains[dom])
                    assert name not in predicates
                    predicates[name] = {
                        "domains": doms,
                        "table": [None for _ in range(size)],
                    }
                    continue

                match2 = Problem.RE_FUNCTION_DECL.match(formula)
                if match2:
                    name = match2.group(1)
                    doms = match2.group(2)
                    codom = match2.group(3)
                    if doms is None:
                        doms = []
                    else:
                        doms = doms.split("*")
                    size = 1
                    for dom in doms:
                        size *= len(domains[dom])
                    assert name not in functions
                    functions[name] = {
                        "domains": doms,
                        "codomain": codom,
                        "table": [None for _ in range(size)],
                    }

            elif match.group(1).startswith("finite_domain_") and match.group(2) == "axiom":
                name = match.group(1)[14:]
                match2 = Problem.RE_FINITE_DOM.match(formula)
                assert name == match2.group(1) and domains[name] == []
                dom = domains[name]
                for idx, elem in enumerate(match2.group(2).split("|")):
                    assert elem.startswith("X=")
                    elem = elem[2:]
                    dom.append(elem)
                    fun = functions[elem]
                    assert fun["domains"] == [] and fun["codomain"] == name
                    assert fun["table"][0] is None
                    fun["table"][0] = idx
                continue

            elif match.group(1).startswith("predicate_") and match.group(2) == "axiom":
                name = match.group(1)[10:]
                doms = predicates[name]["domains"]
                table = predicates[name]["table"]
                if formula:
                    for atom in formula.split("&"):
                        negated = atom.startswith("~")
                        if negated:
                            atom = atom[1:]
                        assert atom.startswith(
                            name + "(") and atom.endswith(")")
                        atom = atom[len(name) + 1:-1]
                        elems = atom.split(",")
                        assert len(elems) == len(doms)
                        idx = 0
                        for dom, elem in zip(doms, elems):
                            idx *= len(domains[dom])
                            idx += domains[dom].index(elem)
                        assert table[idx] is None
                        table[idx] = not negated
                continue

            elif match.group(1).startswith("function_") and match.group(2) == "axiom":
                name = match.group(1)[9:]
                doms = functions[name]["domains"]
                table = functions[name]["table"]
                codom = domains[functions[name]["codomain"]]
                for atom in formula.split("&"):
                    left, right = atom.split("=")
                    assert right in codom
                    assert left.startswith(name + "(") and left.endswith(")")
                    left = left[len(name) + 1:-1]
                    elems = left.split(",")
                    assert len(elems) == len(doms)
                    idx = 0
                    for dom, elem in zip(doms, elems):
                        idx *= len(domains[dom])
                        idx += domains[dom].index(elem)
                    assert table[idx] is None
                    table[idx] = codom.index(right)
                continue

            elif match.group(1).endswith("_definition") and match.group(2) == "axiom":
                name = match.group(1)[:-11]
                if name in predicates:
                    assert formula == name or formula == "~" + name
                    predicate = predicates[name]
                    assert predicate["domains"] == []
                    table = predicate["table"]
                    assert len(table) == 1 and table[0] is None
                    table[0] = formula == name
                elif name in functions:
                    left, right = formula.split("=")
                    assert left == name
                    fun = functions[left]
                    assert fun["domains"] == [] and fun["table"][0] is None
                    codom = domains[fun["codomain"]]
                    assert right in codom
                    fun["table"][0] = codom.index(right)

        return {
            "domains": domains,
            "predicates": predicates,
            "functions": functions,
        }

    def yield_all_models(self, names: List[str]) -> Iterator[Dict]:
        for name in names:
            assert name in self.relations or name in self.operations

        while True:
            result = self.find_one_model()
            if result is None:
                return

            result2 = {}
            omits = []
            for name in names:
                if name in self.relations:
                    rel = self.relations[name]
                    pred = result["predicates"][name]
                    table = pred["table"]
                    result2[name] = table
                    omits.append(rel.has_values(table))
                elif name in self.operations:
                    oper = self.operations[name]
                    func = result["functions"][name]
                    table = func["table"]
                    result2[name] = table
                    omits.append(oper.has_values(table))
                else:
                    raise ValueError()

            yield result2
            if not omits:
                return

            self.require("~(" + "&".join(omits) + ")")

    def find_all_models(self, names: List[str]) -> List[Dict]:
        results = []
        for result in self.yield_all_models(names):
            results.append(result)
        return results
