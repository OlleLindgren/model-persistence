import json
from pathlib import Path
from typing import List

class DependencySpec:
    meta: dict
    dependencies: List[str]
    defaults: List

    def __init__(self, dependencies: List[str], meta: dict = None, **kwargs) -> None:
        
        # Validate inputs
        assert len(dependencies) > 0
        assert len(set(dependencies)) == len(dependencies), 'dependencies must be unique'
        
        # Save dependencies
        self.dependencies = sorted(dependencies)

        # Save additional kwargs in self.meta
        self.meta = meta or {}
        self.meta.update(kwargs)

    def __iter__(self):
        yield from self.dependencies

    def __len__(self):
        return len(self.dependencies)

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
                set.union(set(self), set(other))
                if hasattr(other, '__iter__')
                else set(self)
            ),
            meta=self.meta
        )

    def __iadd__(self, other):
        """Add dependencies from a DependencySpec or iterable to this inplace."""

        if isinstance(other, str):
            other = [other]
        elif isinstance(other, int):
            other = []
        elif not isinstance(other, DependencySpec):
            raise TypeError(f"Cannot add {other} of type {type(other)} to DependencySpec")

        self.dependencies=sorted(
            set.union(set(self), set(other))
            if hasattr(other, '__iter__')
            else set(self)
        )

    def __getitem__(self, attr):
        if isinstance(attr, str):
            if attr in self.dependencies:
                return DependencySpec(
                    dependencies=[attr],
                    meta=self.meta
                )
            else:
                raise ValueError(f"Dependency {attr} not found in dependencies")
        elif isinstance(attr, int):
            return DependencySpec(
                dependencies=[self.dependencies[attr]],
                meta=self.meta
            )
        else:
            for a in attr:
                if a not in self.dependencies:
                    raise ValueError(f"Dependency {a} not found in dependencies")
            return DependencySpec(
                dependencies=[attr],
                meta=self.meta
            )

    def __str__(self):
        result = 'DependencySpec object with dependencies:' + str(self.dependencies)
        return result

    def to_dict(self):
        return {
            "dependencies": self.dependencies,
            "meta": self.meta
        }

    def from_dict(dictionary: dict):
        return DependencySpec(**dictionary)

    def save(self, path: Path):
        with open(path, 'w+') as f:
            f.write(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: Path):
        with open(path, 'r') as f:
            dictionary = json.loads(f.read())
            return DependencySpec.from_dict(dictionary)
