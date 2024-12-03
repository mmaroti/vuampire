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
from typeguard import typechecked


class Term:
    @typechecked
    def __init__(self, domain: 'Domain', value: str):
        self.domain = domain
        self.value = value

    @typechecked
    def __str__(self) -> str:
        return self.value

    @typechecked
    def __eq__(self, other: 'Term') -> 'Term':
        assert self.domain == other.domain
        return Term(BOOLEAN, f"{self} = {other}")

    @typechecked
    def __ne__(self, other: 'Term') -> 'Term':
        assert self.domain == other.domain
        return Term(BOOLEAN, f"{self} != {other}")

    @typechecked
    def __and__(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        if self.value == "$false" or other.value == "$true":
            return self
        elif self.value == "$true" or other.value == "$false":
            return other
        else:
            return Term(BOOLEAN, f"({self} & {other})")

    @typechecked
    def __or__(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        if self.value == "$false" or other.value == "$true":
            return other
        elif self.value == "$true" or other.value == "$false":
            return self
        else:
            return Term(BOOLEAN, f"({self} | {other})")

    @typechecked
    def __invert__(self) -> 'Term':
        assert self.domain == BOOLEAN
        if self.value == "$true":
            return Term(BOOLEAN, "$false")
        elif self.value == "$false":
            return Term(BOOLEAN, "$true")
        elif self.value.startswith("~"):
            return Term(BOOLEAN, self.value[1:])
        else:
            return Term(BOOLEAN, f"~{self.value}")

    @typechecked
    def imp(self, other: 'Term') -> 'Term':
        assert self.domain == BOOLEAN and other.domain == BOOLEAN
        return Term(BOOLEAN, f"({self} => {other})")

    @staticmethod
    @typechecked
    def any(terms: List['Term']) -> 'Term':
        assert all(t.domain == BOOLEAN for t in terms)
        terms = [t for t in terms if t.value != "$false"]
        if len(terms) == 0:
            return Term(BOOLEAN, '$false')
        elif len(terms) == 1:
            return terms[0]
        elif any(t.value == "$true" for t in terms):
            return Term(BOOLEAN, "$true")
        else:
            return Term(BOOLEAN, "(" + " | ".join(str(t) for t in terms) + ")")

    @staticmethod
    @typechecked
    def all(terms: List['Term']) -> 'Term':
        assert all(t.domain == BOOLEAN for t in terms)
        terms = [t for t in terms if t.value != "$true"]
        if len(terms) == 0:
            return Term(BOOLEAN, '$true')
        elif len(terms) == 1:
            return terms[0]
        elif any(t.value == "$false" for t in terms):
            return Term(BOOLEAN, "$false")
        else:
            return Term(BOOLEAN, "(" + " & ".join(str(t) for t in terms) + ")")


class Domain(ABC):
    nesting: int = 0

    @typechecked
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()

    @typechecked
    @abstractmethod
    def declare(self) -> Iterator[str]:
        raise NotImplementedError()

    @typechecked
    def forall(self, callable: Callable[..., Term]) -> Term:
        num_args: int = callable.__code__.co_argcount
        args = [Term(self, f"X{Domain.nesting + i}")
                for i in range(num_args)]

        Domain.nesting += num_args
        result = callable(*args)
        Domain.nesting -= num_args

        assert result.domain == BOOLEAN
        args = [f"{arg}:{self}" for arg in args]
        return Term(BOOLEAN, f"(![{','.join(args)}]: {result.value})")


class PrimitiveDom(Domain):
    @typechecked
    def __init__(self, name: str):
        self.name = name

    @typechecked
    def __str__(self) -> str:
        return self.name

    @typechecked
    def declare(self) -> Iterator[str]:
        if False:
            yield


UNIVERSE = PrimitiveDom("$i")
BOOLEAN = PrimitiveDom("$o")
INTEGER = PrimitiveDom("$int")


class NamedDom(Domain):
    @typechecked
    def __init__(self, name: str):
        self.name = name

    @typechecked
    def __str__(self) -> str:
        return self.name

    @typechecked
    def declare(self) -> Iterator[str]:
        yield f"tff(declared_{self.name}, type, {self.name}:$tType)."


class FixedDom(NamedDom):
    @typechecked
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size
        self.elems = [Term(self, f"{name}{i}") for i in range(size)]

    @typechecked
    def declare(self) -> Iterator[str]:
        for line in super().declare():
            yield line

        for i in range(self.size):
            yield f"tff(declare_{self.elems[i]}, type, {self.elems[i]}: {self})."

        axiom = self.forall(lambda x: Term.any([x == e for e in self.elems]))
        yield f"tff({self.name}_elements, axiom, {axiom})."

        elems = ', '.join([str(e) for e in self.elems])
        yield f"tff({self.name}_distinct, axiom, $distinct({elems}))."
