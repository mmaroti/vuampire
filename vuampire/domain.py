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

from abc import ABC, abstractmethod
from typing import Iterator, Callable, List


class Term:
    def __init__(self, domain: 'Domain', value: str):
        self.domain = domain
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: 'Term') -> 'Term':
        assert self.domain == other.domain
        return Term(BOOLEAN, f"{self} = {other}")

    def __ne__(self, other: 'Term') -> 'Term':
        assert self.domain == other.domain
        return Term(BOOLEAN, f"{self} != {other}")

    def __and__(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        return Term(BOOLEAN, f"({self} & {other})")

    def __or__(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        return Term(BOOLEAN, f"({self} | {other})")

    def __invert__(self) -> 'Term':
        assert self.domain == BOOLEAN
        if self.value.startswith("~"):
            return Term(BOOLEAN, self.value[1:])
        else:
            return Term(BOOLEAN, f"~{self.value}")

    def imp(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        return Term(BOOLEAN, f"({self} => {other})")

    @staticmethod
    def any(terms: List['Term']) -> 'Term':
        assert all(t.domain == BOOLEAN for t in terms)
        if len(terms) == 0:
            return Term(BOOLEAN, '$false')
        elif len(terms) == 1:
            return terms[0]
        else:
            return Term(BOOLEAN, "(" + " | ".join(str(t) for t in terms) + ")")

    @staticmethod
    def all(terms: List['Term']) -> 'Term':
        assert all(t.domain == BOOLEAN for t in terms)
        if len(terms) == 0:
            return Term(BOOLEAN, '$true')
        elif len(terms) == 1:
            return terms[0]
        else:
            return Term(BOOLEAN, "(" + " & ".join(str(t) for t in terms) + ")")


class Domain(ABC):
    nesting: int = 0

    @property
    @abstractmethod
    def type_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def declare(self) -> Iterator[str]:
        raise NotImplementedError()

    def forall(self, callable: Callable[..., Term]):
        num_args: int = callable.__code__.co_argcount
        args = [Term(self, f"X{Domain.nesting + i}")
                for i in range(num_args)]

        Domain.nesting += num_args
        result = callable(*args)
        Domain.nesting -= num_args

        assert result.domain == BOOLEAN
        args = [f"{arg}:{self.type_name}" for arg in args]
        return Term(BOOLEAN, f"(![{','.join(args)}]: {result.value})")


class PrimitiveDom(Domain):
    def __init__(self, name: str):
        self.name = name

    @property
    def type_name(self) -> str:
        return self.name

    def declare(self) -> Iterator[str]:
        if False:
            yield


UNIVERSE = PrimitiveDom("$i")
BOOLEAN = PrimitiveDom("$o")
INTEGER = PrimitiveDom("$int")


class NamedDom(Domain):
    def __init__(self, name: str):
        self.name = name

    @property
    def type_name(self) -> str:
        return self.name

    def declare(self) -> Iterator[str]:
        yield f"tff(declared_{self.name}, type, {self.name}:$tType)."


class FixedDom(NamedDom):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size
        self.elems = [Term(self, f"{name}{i}") for i in range(size)]

    def declare(self) -> Iterator[str]:
        for line in super().declare():
            yield line

        for i in range(self.size):
            yield f"tff(declare_{self.elems[i]}, type, {self.elems[i]}: {self.type_name})."

        axiom = self.forall(lambda x: Term.any([x == e for e in self.elems]))
        yield f"tff({self.name}_elements, axiom, {axiom})."

        elems = ', '.join([str(e) for e in self.elems])
        yield f"tff({self.name}_distinct, axiom, $distinct({elems}))."


class ProductDom(Domain):
    def __init__(self, domain: Domain, arity: int):
        assert arity >= 0
        self.domain = domain
        self.arity = arity
