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


def logical_not(formula: str) -> str:
    if formula == "$true":
        return "$false"
    elif formula == "$false":
        return "$true"
    elif formula.startswith("~"):
        return formula[1:]
    else:
        return "~" + formula


def logical_and(formulas: List[str]) -> str:
    if len(formulas) == 0:
        return "$true"
    elif len(formulas) == 1:
        return formulas[0]
    else:
        return "(" + " & ".join(formulas) + ")"


def logical_or(formulas: List[str]) -> str:
    if len(formulas) == 0:
        return "$false"
    elif len(formulas) == 1:
        return formulas[0]
    else:
        return "(" + " | ".join(formulas) + ")"


def equality(term1: str, term2) -> str:
    return term1 + "=" + term2
