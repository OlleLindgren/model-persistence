"""In this file, the ModelContainer class is defined, as well as some helper logic"""
import os
from pathlib import Path
import datetime
import json

from typing import Iterable

if __package__:
    from .dependencies import DependencySpecType
    if os.getenv("SKIP_PERSISTENCE_LOADERS"):
        try:
            from . import model_io
        except ImportError as err:
            pass
    else:
        from . import model_io
else:
    from dependencies import DependencySpecType
    if os.getenv("SKIP_PERSISTENCE_LOADERS"):
        try:
            import model_io
        except ImportError as err:
            pass
    else:
        import model_io

DATE_STR_FORMAT = r"%Y-%m-%d"

MODEL_FILENAME: str = "model"
X_SPEC_FILENAME: str = "X_spec.json"
Y_SPEC_FILENAME: str = "y_spec.json"
EXTRAS_FILENAME: str = "extras.json"

from abc import ABC, abstractmethod


class BaseEstimator(ABC):
    @abstractmethod
    def fit(X: Iterable, y: Iterable) -> None:
        pass

    @abstractmethod
    def predict(X: Iterable) -> Iterable:
        pass


class ModelContainer:
    """Container for a model, X_spec, y_spec, and other metadata used to specify a model"""
    def __init__(self,
                 model: BaseEstimator,
                 X_spec: DependencySpecType,
                 y_spec: DependencySpecType,
                 dt: datetime.timedelta = datetime.timedelta(seconds=0),
                 eval_metrics=None) -> None:

        assert hasattr(model, "predict"), "model must implement 'predict'"
        assert hasattr(model, "fit"), "model must implement 'fit'"

        if eval_metrics:
            assert isinstance(eval_metrics, dict), \
            "eval_metrics (if provided) must be a dict of {metric: value} pairs"

        self.model: BaseEstimator = model
        self.X_spec: DependencySpecType = X_spec
        self.y_spec: DependencySpecType = y_spec
        self.dt: datetime.timedelta = dt
        self.eval_metrics: dict = eval_metrics or {}

    @staticmethod
    def __model_save_paths(save_root: Path):
        # All the save paths for model directories

        model_path = os.path.join(save_root, MODEL_FILENAME)
        X_spec_path = os.path.join(save_root, X_SPEC_FILENAME)
        y_spec_path = os.path.join(save_root, Y_SPEC_FILENAME)
        extras_path = os.path.join(save_root, EXTRAS_FILENAME)

        return model_path, X_spec_path, y_spec_path, extras_path

    @staticmethod
    def __timedelta_to_dict(delta: datetime.timedelta) -> dict:
        return {
            "days": delta.days,
            "seconds": delta.seconds,
            "microseconds": delta.microseconds
        }

    @staticmethod
    def __dict_to_timedelta(delta: dict) -> datetime.timedelta:
        return datetime.timedelta(**delta)

    @staticmethod
    def save_spec(spec: DependencySpecType, path: Path) -> None:
        """Save a DependencySpecType to a path"""
        with open(path, 'w+') as f:
            f.write(json.dumps(spec.to_dict(), indent=2))

    @staticmethod
    def load_spec(path: Path) -> DependencySpecType:
        """Load a DependencySpecType from path"""
        with open(path, 'r') as f:
            dictionary = json.loads(f.read())
            DependencySpecType.from_dict(dictionary)

    def save(self, path: Path) -> None:
        """Save model to model directory, along with everything needed to run the model.
        This will overwrite existing files without asking

        Args:
            path (Path): The path to save to (will create a folder at this location)
        """
        #
        #

        # Pack extras
        extras = {
            "eval_metrics": self.eval_metrics,
            "dt": self.__timedelta_to_dict(self.dt),
            "save_timestamp": datetime.datetime.now().strftime(DATE_STR_FORMAT)
        }

        # Get paths to the different files we're going to save
        model_path, X_spec_path, y_spec_path, extras_path = self.__model_save_paths(
            path)

        # Ensure parent folder exists
        if not os.path.isdir(path):
            os.makedirs(path)

        # Save model and specs
        model_io.save(self.model, model_path)
        self.save_spec(self.X_spec, X_spec_path)
        self.save_spec(self.y_spec, y_spec_path)

        # Write extras
        with open(extras_path, 'w') as f:
            f.write(json.dumps(extras, indent=2))

    @staticmethod
    def load(path: Path):
        """Load saved model from path to folder

        Args:
            path (Path): Path to load from

        Returns:
            ModelContainer: Loaded ModelContainer
        """

        # Get internal paths (i.e. inside the original folder/path)
        model_path, X_spec_path, y_spec_path, extras_path = ModelContainer.__model_save_paths(
            path)

        # assert all the paths exist
        assert os.path.isfile(
            model_path), f"model save file does not exist: {model_path}"
        assert os.path.isfile(
            X_spec_path), f"X_Spec save file does not exist: {X_spec_path}"
        assert os.path.isfile(
            y_spec_path), f"y_Spec save file does not exist: {y_spec_path}"
        assert os.path.isfile(
            extras_path), f"extras save file does not exist: {extras_path}"

        model = model_io.load(model_path)
        X_spec = ModelContainer.load_spec(X_spec_path)
        y_spec = ModelContainer.load_spec(y_spec_path)

        # Eval metrics and dt are stored in the little extras file
        with open(extras_path, 'r') as f:
            extras = json.loads(f.read())

        eval_metrics = extras["eval_metrics"]
        dt = ModelContainer.__dict_to_timedelta(extras["dt"])

        return ModelContainer(model, X_spec, y_spec, dt, eval_metrics)
