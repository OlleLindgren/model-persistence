from pathlib import Path

KERAS_MODEL_SAVE_FORMAT = 'tf'

def get_keras():
    # Try to import keras. Return (keras, True) or (None, False) depending on result.
    try:
        import keras
        return keras, True
    except:
        try:
            from tensorflow import keras
            return keras, True
        except:
            pass
    return None, False

def get_joblib():
    # Try to import joblib. Return (joblib, True) or (None, False) depending on result.
    try:
        import joblib
        return joblib, True
    except:
        return None, False

# Try to get import/export libraries
keras, keras_available = get_keras()
joblib, joblib_available = get_joblib()

# Initialize importer/exporter lists
importers = []
exporters = []

# Fill importer/exporter lists

if keras_available:
    def save_keras(model: keras.Model, path: Path):
        model.save(path, 
            save_format=KERAS_MODEL_SAVE_FORMAT)

    def load_keras(path: Path) -> keras.Model:
        return keras.models.load_model(path)

    exporters.append(save_keras)
    exporters.append(load_keras)

if joblib_available:
    def save_pickle(model, path: Path):
        joblib.dump(model, path)
    
    def load_pickle(path: Path):
        return joblib.load(path)
        
    exporters.append(save_pickle)
    exporters.append(load_pickle)

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
        except:
            pass
    
    return None

# Check that any exporters/importers were successfully loaded
assert len(importers) > 0, "No import libraries available. tensorflow or joblib is required, depending on what models you want to load."
