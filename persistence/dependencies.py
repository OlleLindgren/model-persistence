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
        assert sorted(list(set(dependencies))) == dependencies, 'dependencies must be sorted and unique'
        
        # Save dependencies
        self.dependencies = dependencies

        # Save additional kwargs in self.meta
        self.meta = meta or {}
        self.meta.update(kwargs)

    def __iter__(self):
        yield from self.dependencies

    def __len__(self):
        return len(self.dependencies)

    def __add__(self, other):
        # Add a DependencySpec object to this. 
        # Return new DependencySpec object with the union of this and other's dependencies

        # Create result
        return DependencySpec(
            dependencies=sorted(set(self.dependencies+other.dependencies)),
            meta=self.meta
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
