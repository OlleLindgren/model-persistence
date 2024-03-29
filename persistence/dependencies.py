"""This module contains the DependencySpec classes"""
from __future__ import annotations

import itertools
import json
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import List


class DependencySpecType(ABC):
    """Abstract base class for all DependencySpec classes"""

    meta: dict
    defaults: List

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """The dependencies of this DependencySpec"""

    def __iter__(self):
        yield from self.dependencies

    def __len__(self):
        return len(self.dependencies)

    def __getitem__(self, attr):

        if isinstance(attr, str):
            if attr in self.dependencies:
                return DependencySpec(dependencies=[attr], meta=self.meta)
            raise ValueError(f"Dependency {attr} not found in dependencies")

        if isinstance(attr, int):
            return DependencySpec(dependencies=[self.dependencies[attr]], meta=self.meta)

        for dep in attr:
            if dep not in self.dependencies:
                raise ValueError(f"Dependency {dep} not found in dependencies")

        return DependencySpec(dependencies=list(attr), meta=self.meta)

    @staticmethod
    def from_dict(dictionary: dict | list):
        """Convert a dictionary or list to a DependencySpec

        Args:
            dictionary (dict | list): The object to convert

        Raises:
            ValueError: If the object is a dict, but does not have any "dependencies" key
            TypeError: If the object is neither dict or list

        Returns:
            [type]: [description]
        """
        if isinstance(dictionary, dict):
            if dictionary.keys() <= {"dependencies", "meta"}:
                return DependencySpec(**dictionary)
            if dictionary.keys() <= {"children", "meta"}:
                children = [
                    DependencySpecType.from_dict(child) for child in dictionary.get("children", [])
                ]
                return NestedDependencySpec(
                    children=children,
                    meta=dictionary.get("meta", {}),
                )

            raise ValueError(f"Invalid dictionary: {dictionary}")

        if isinstance(dictionary, list):
            return NestedDependencySpec(
                children=[DependencySpecType.from_dict(d) for d in dictionary]
            )

        raise TypeError(f"from_dict argument must be dict or list, not {type(dictionary)}")

    def save(self, path: Path):
        """Save self to some path

        Args:
            path (Path): The path to save to
        """
        with open(path, "w+", encoding="utf-8") as handle:
            handle.write(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: Path):
        """Load DependencySpec from some path

        Args:
            path (Path): Path to load from

        Returns:
            DependencySpecType: The loaded dependencySpec,
            either a DependencySpec or NestedDependencySpec.
        """
        with open(path, "r", encoding="utf-8") as handle:
            dictionary = json.loads(handle.read())
            return DependencySpec.from_dict(dictionary)

    @abstractmethod
    def __add__(self, other: str | DependencySpecType):
        pass

    @abstractmethod
    def __iadd__(self, other: str | DependencySpecType):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def to_dict(self):
        """Convert self to a dict."""


class DependencySpec(DependencySpecType):
    """A normal, non-nested DependencySpec"""

    def __init__(self, dependencies: List[str], meta: dict = None, **kwargs) -> None:

        if not all(isinstance(dep, str) for dep in dependencies):
            raise TypeError("All dependencies must be of type str")
        # Validate inputs
        assert len(dependencies) > 0
        assert len(set(dependencies)) == len(dependencies), "dependencies must be unique"

        # Save dependencies
        self.__dependencies = sorted(dependencies)

        # Save additional kwargs in self.meta
        self.meta = meta or {}
        self.meta.update(kwargs)

    @property
    def dependencies(self) -> List[str]:
        return self.__dependencies

    def __add__(self, other):
        """Add dependencies from a DependencySpec or iterable to this."""

        if isinstance(other, str):
            other = [other]
        elif isinstance(other, int):
            other = []
        elif not isinstance(other, DependencySpec):
            raise TypeError(f"Cannot add {other} of type {type(other)} to DependencySpec")

        return DependencySpec(
            dependencies=sorted(
                set.union(set(self), set(other)) if hasattr(other, "__iter__") else set(self)
            ),
            meta=self.meta,
        )

    def __iadd__(self, other):
        """Add dependencies from a DependencySpec or iterable to this inplace."""

        if isinstance(other, str):
            other = [other]
        elif isinstance(other, int):
            other = []
        elif not isinstance(other, DependencySpec):
            raise TypeError(f"Cannot add {other} of type {type(other)} to DependencySpec")

        self.dependencies = sorted(
            set.union(set(self), set(other)) if hasattr(other, "__iter__") else set(self)
        )

    def __str__(self):
        result = "DependencySpec object with dependencies:" + str(self.dependencies)
        return result

    def to_dict(self):
        return {"dependencies": self.dependencies, "meta": self.meta or {}}


class NestedDependencySpec(DependencySpecType):
    """A nested DependencySpec."""

    def __init__(self, children: List[DependencySpecType], meta: dict = None, **kwargs) -> None:

        if any(isinstance(child, str) for child in children):
            raise TypeError(
                "NestedDependencySpec cannot have str children, "
                "did you mean to construct a DependencySpec?"
            )

        self.children = children

        # Validate inputs
        assert len(children) > 0
        if len(set(self.dependencies)) != len(self.dependencies):
            print("Some dependencies found multiple times. Violators:")
            cnt = Counter()
            for dep in self.dependencies:
                cnt[dep] += 1
            longest_dep_name = max(map(len, cnt.keys()))
            longest_ntimes_str = max(map(len, map(str, cnt.values())))
            for dep, n_finds in cnt.items():
                if n_finds > 1:
                    spacing1 = " " * (longest_dep_name - len(dep))
                    spacing2 = " " * (longest_ntimes_str - len(str(n_finds)))
                    print(f"{dep} {spacing1} found {n_finds} {spacing2} times.")
            raise ValueError("some dependencies exist multiple times")

        # Save additional kwargs in self.meta
        self.meta = meta or {}
        self.meta.update(kwargs)

    @property
    def dependencies(self) -> List[str]:
        return list(itertools.chain(*(child.dependencies for child in self.children)))

    def __add__(self, other: DependencySpec):
        if not isinstance(other, DependencySpec):
            raise TypeError(
                f"Cannot add '{other}' of type type {type(other)} to NestedDependencySpec"
            )
        return NestedDependencySpec(children=self.children + other, meta=self.meta)

    def __iadd__(self, other: DependencySpec):
        if not isinstance(other, DependencySpec):
            raise TypeError(
                f"Cannot add '{other}' of type type {type(other)} to NestedDependencySpec"
            )
        if not set(self.dependencies).isdisjoint(other.dependencies):
            raise ValueError("Dependencies in other overlaps with self; cannot add")
        self.children.append(other)

    def __str__(self):
        result = "NestedDependencySpec object with dependencies:\n  " + "\n  ".join(
            map(str, self.dependencies)
        )
        return result

    def to_dict(self):
        return {"children": [child.to_dict() for child in self.children], "meta": self.meta or {}}
