This directory contains necessary stub files for PyCharm.

To include them in PyCharm, right-click the `.stubs` directory in the project view, go to "Mark Directory as" and choose
"Sources Root".


## typing-extensions

The file `typing_extensions.pyi` contains updated stubs for [typing-extensions](https://pypi.org/project/typing-extensions)
from [typeshed](https://github.com/python/typeshed/blob/master/stdlib/typing_extensions.pyi).

They are necessary because the typeshed stubs in PyCharm 2022.2 are outdated: the `field_specifiers` parameter of
`@dataclass_transform` used to be called `field_descriptors` instead, which was changed in typing-extensions 4.2.0.

As soon as PyCharm includes the updated stubs, this file can be deleted from the repository.
