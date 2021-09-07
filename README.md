# model-persistence
model-persistence introduces two classes, DependencySpec and ModelContainer.

A DependencySpec object is a list of dependencies in string format, along with an optional meta dictionary. The dependencies are meant to represent columns from a dataset. DependencySpec objects implement save() and load(), so that they can be saved by one script and later loaded by another.

ModelContainer is an extension of DependencySpec, where we essentially pack a model (perhaps from keras or sklearn), along with two DependencySpec objects (one for X and one for y), and some optional metadata. The ModelContainer class also implements save() and load().

# install

`pip install git+https://github.com/OlleLindgren/model-persistence@main`
