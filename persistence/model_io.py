"""Tools for saving and loading models with keras and joblib (sklearn)"""
from pathlib import Path

KERAS_MODEL_SAVE_FORMAT = "tf"

# Try to import keras. Return (keras, True) or (None, False) depending on result.
keras = None
try:
    import keras
except ImportError:
    try:
        from tensorflow import keras
    except ImportError:
        pass

# Try to import joblib. Return (joblib, True) or (None, False) depending on result.
joblib = None
try:
    import joblib
except ImportError:
    pass

# Initialize importer/exporter lists
importers = []
exporters = []

# Fill importer/exporter lists

if keras:

    def save_keras(model: keras.Model, path: Path):
        model.save(path, save_format=KERAS_MODEL_SAVE_FORMAT)

    def load_keras(path: Path) -> keras.Model:
        return keras.models.load_model(path)

    exporters.append(save_keras)
    importers.append(load_keras)

if joblib:

    def save_pickle(model, path: Path):
        joblib.dump(model, path)

    def load_pickle(path: Path):
        return joblib.load(path)

    exporters.append(save_pickle)
    importers.append(load_pickle)


def save(model, path: Path) -> None:
    # Save a model to a file
    success = False
    for export_func in exporters:
        try:
            export_func(model, path)
            success = True
        except:
            pass

    return success


def load(path: Path):
    # Load a model from a file
    for import_func in importers:
        try:
            result = import_func(path)
            assert result is not None
            return result
        except BaseException as err:
            pass

    raise err


if __package__ and not importers and not exporters:
    raise ImportError(
        "No importers or exporters loaded. Install joblib (sklearn) or tensorflow, or set the SKIP_PERSISTENCE_LOADERS environment variable."
    )
