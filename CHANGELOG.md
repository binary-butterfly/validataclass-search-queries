# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.5.0...HEAD)


## [0.5.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.5.0) - 2024-05-15

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.4.2...0.5.0)

This release mostly updates the dependency on validataclass to version 0.10.0.

Also, this library is now licensed under an MIT license to be compatible with FOSS projects.

### Changed

- `MultiSelectValidator`: Empty strings are now parsed as empty lists. [!13] 

### Dependencies

- Update validataclass dependency to version [0.10.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.10.0). [!14]
- Add support and test environment for Python 3.12. [!14]

### Miscellaneous

- Change project license to MIT. [!15]

[!13]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/13
[!14]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/14
[!15]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/15


## [0.4.2](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.4.2) - 2023-08-21

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.4.1...0.4.2)

Add support for SQLAlchemy 2.0.

### Dependencies

- Update dependencies to support SQLAlchemy 2.0. [!11]
- Update build pipeline to test with both SQLAlchemy 1.4 and 2.0. [!11]

[!11]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/11


## [0.4.1](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.4.1) - 2023-05-24

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.4.0...0.4.1)

This release provides compatibility for [validataclass 0.9](https://github.com/binary-butterfly/validataclass/releases/tag/0.9.0)
and thus adds official support for Python 3.11.

### Dependencies

- Update validataclass dependency to version [0.9.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.9.0). [!10]
  - This adds support for Python 3.11.
- Update local test environment for tox 4. [!10]

[!10]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/10


## [0.4.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.4.0) - 2022-11-30

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.3.0...0.4.0)

This release provides compatibility for [validataclass 0.8](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.0).

### Changed

- Updated validataclass dependency to version [0.8.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.1). [!8]
- **Breaking change:** `MultiSelectAnyOfValidator` and `MultiSelectEnumValidator` are now case-sensitive by default. [!8]
  - This is the same change done in validataclass with the `AnyOfValidator` and `EnumValidator`.
  - The parameter `case_insensitive` is now deprecated and will be removed in a future version.
- The pagination and sorting parameters (e.g. `limit`) in the abstract mixin classes are now defined as regular attributes
  instead of abstract properties. [!9]
  - This solves typing/linting problems when manually assigning values to these attributes in a dataclass instance.

[!8]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/8
[!9]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/9


## [0.3.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.3.0) - 2022-11-22

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.2.2...0.3.0)

### Added

- `SearchParamCustom`: Special search parameter that raises an exception unless it's bypassed via a custom filter in the
  repository. [!6]

### Changed

- Enums are now automatically converted to their values in `BaseSearchQuery.to_dict()`. [!7]

### Fixed

- Type hint for `SearchQueryRepositoryMixin.model_cls` is now `Type[T_Model]` instead of just `Type`. [!7]

[!6]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/6
[!7]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/7


## [0.2.2](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.2.2) - 2022-10-27

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.2.1...0.2.2)

### Added

- `MultiSelectAnyOfValidator` and `MultiSelectEnumValidator`: Add (missing) parameter `case_insensitive`. [!5]

[!5]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/5


## [0.2.1](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.2.1) - 2022-09-29

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.2.0...0.2.1)

This release improves type hinting, based on validataclass 0.7.2.

### Changed

- Updated validataclass dependency to version [0.7.2](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.2)
  which improves the type hinting for validataclasses and the `DataclassValidator`. [!4]
- Improved type hinting for `@search_query_dataclass` decorator analogous to `@validataclass`. [!4]

[!4]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/4


## [0.2.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.2.0) - 2022-09-22

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.1.0...0.2.0)

This release is an upgrade to validataclass 0.7.0.

The previous release is not compatible to this version of validataclass, and vice-versa.

### Changed

- Updated validataclass dependency to version [0.7.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.0). [!3]
  - Validators now support context-arguments.
  - MultiSelectValidators now have better type-hinting thanks to `ListValidator` and `EnumValidator` being generic now.
- `BaseSearchQuery`: Search filters that are set to `UnsetValue` are now discarded (same as `None`). [!3]

[!3]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/3


## [0.1.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.1.0) - 2022-08-22

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/commits/0.1.0)

This is the first non-alpha release of validataclass-search-queries.

### General

- Initial release.
