# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased](https://github.com/binary-butterfly/validataclass-search-queries/compare/0.6.0...HEAD)


## [0.6.0](https://github.com/binary-butterfly/validataclass-search-queries/releases/tag/0.6.0) - 2026-04-15

[Full changelog](https://github.com/binary-butterfly/validataclass-search-queries/compare/0.5.1...0.6.0)

This is the companion release to [validataclass 0.12.0], which improves typing and adds proper support for type checking
with [mypy](https://mypy-lang.org/) using a custom mypy plugin.

Please also read the release notes for validataclass 0.12.0 for further information on potential breaking changes and
how to update.

To enable the mypy plugin and configure it for compatibility with validataclass-search-queries, have a look at
[`docs/04-mypy-plugin.md`](https://github.com/binary-butterfly/validataclass-search-queries/blob/main/docs/04-mypy-plugin.md).

This is also the first officially public release of the library. Previously, this project was hosted on our company's
internal GitLab (even though publically accessible), because it was originally meant for internal use only. We decided
to migrate the project to GitHub and publish official releases on PyPI, though, to allow easier integration into other
public projects.

This version drops support for Python 3.8 and 3.9 and adds support for Python 3.13 and 3.14.

Additionally, support for SQLAlchemy 1.4 is deprecated now, you should upgrade to SQLAlchemy 2.0 if you haven't done so
already. This version still *works* with SQLAlchemy 1.4, however, proper typing is not supported, so there might be
several type errors in this library if you use that version of SQLAlchemy.

### General

- Migrate project from our company GitLab to GitHub and [PyPI](https://pypi.org/). [#1]

### Added

- Add support for Python 3.13. [#6]
- Add support for Python 3.14. [#6]
- Add `py.typed` file to make the package PEP 561 compatible. [#6]
- Add support for type checking using the validataclass mypy plugin. [#6]

### Changed

- Generic-based typing for validator classes. [#6]
  - Validators have been updated to be compatible with the generic-based typing in validataclass 0.12.0.
  - The `MultiSelectValidator` is a generic class now where the type parameter specifies the type of list items
    (similar to the `ListValidator`). Its subclasses are updated similarly.
  - The `PaginationLimitValidator` is a `Validator[int | None]`. This is because it can return None when pagination is
    optional. The typing might be improved in the future, possibly by splitting up the validator into one that enforces
    pagination and one where it's optional. If you need more precise typing, you can use a regular `IntegerValidator`.
- Restructure files for `MultiSelectValidator` and subclasses. [#4]
  - The `MultiSelectValidator` and its subclasses (`MultiSelectEnumValidator`, etc.) are now defined in separate files.
  - This implies a small **breaking change** if the validators are imported directly from the original module, i.e. from
    `validataclass_search_queries.validators.multi_select_validator`. It is recommended to import them from the parent
    package `validataclass_search_queries.validators` instead.
- Use `DataclassValidatorFieldException` in `@search_query_dataclass` decorator. [#5]
  - Previously, a different type of exception was used. This was inconsistent with the `@validataclass` decorator.
  - This shouldn't break any code, because those exceptions are only raised when your search query dataclass definitions
    are incorrect, so your code isn't valid anyway.
  - Some error messages from the decorator have also been changed for consistency.
- `PaginatedResult.map()` always returns another `PaginatedResult` now, even when subclassed. [#6]
  - Previously, the method used `self.__class__()` to instantiate a new object of the same type as `self` (e.g. a
    subclass). However, this isn't really compatible with generic typing, since the subclass might not actually be
    compatible with the mapped type.

### Deprecated

- Deprecate support for SQLAlchemy 1.4. Support may be dropped in the near future, possibly the next release.
  - There should be no problems with SQLAlchemy 1.4 at runtime with this version. However, typing is not supported since
    SQLAlchemy didn't have good typing prior to 2.0. Type errors in this library related to SQLAlchemy 1.4 are expected.
- Deprecate reusing TypeVars from the library by removing them from `__all__`. [#6]

### Removed

- Drop support for Python 3.8. [#3]
- Drop support for Python 3.9. [#3]

### Fixed

- Fix incorrect short-circuiting of substring search filters. [#6]
  - Previously, substring search filters like `SearchParamContains` had a condition to "short-circuit" if the search
    value was empty. The idea was that a condition like `col LIKE "%%"` is always true, so the clause could be
    simplified. However, the functions simply returned the column itself and not a clause. This didn't seem correct and
    also just unnecessary, so this short-circuiting mechanism was removed.

### Dependencies

- Change required version of validataclass to 0.12.0 or higher, but below 0.13.0. [#6]

### Testing / CI

- Use GitHub Actions instead of GitLab CI. [#1]
- Add more unit tests. [#5]
- Enable mypy type checking with strict mode and extra rules. [#6]
- Update testing dependencies and pin them to minor versions. [#7]
- Fix tox configuration to run unit tests with both SQLAlchemy 1.4 and 2.0. [#7]

### Miscellaneous

- Various code modernizations after dropping support for Python 3.8 and 3.9. [#3]
- Various refactoring, typing improvements and fixes. [#6]

[validataclass 0.12.0]: https://github.com/binary-butterfly/validataclass/releases/tag/0.12.0
[#1]: https://github.com/binary-butterfly/validataclass-search-queries/pull/1
[#3]: https://github.com/binary-butterfly/validataclass-search-queries/pull/3
[#4]: https://github.com/binary-butterfly/validataclass-search-queries/pull/4
[#5]: https://github.com/binary-butterfly/validataclass-search-queries/pull/5
[#6]: https://github.com/binary-butterfly/validataclass-search-queries/pull/6
[#7]: https://github.com/binary-butterfly/validataclass-search-queries/pull/7


## [0.5.1](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.5.1) - 2024-08-12

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.5.0...0.5.1)

This release only adds compatibility with validataclass 0.11.0.

### Dependencies

- Add compatibility for [validataclass 0.11.0]. [!17]

[!17]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/17
[validataclass 0.11.0]: https://github.com/binary-butterfly/validataclass/releases/tag/0.11.0


## [0.5.0](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.5.0) - 2024-05-15

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.4.2...0.5.0)

This release mostly updates the dependency on validataclass to version 0.10.0.

Also, this library is now licensed under an MIT license to be compatible with FOSS projects.

### Changed

- `MultiSelectValidator`: Empty strings are now parsed as empty lists. [!13]

### Dependencies

- Update validataclass dependency to version [0.10.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.10.0). [!14]
- Add support and test environment for Python 3.12. [!14]

### Miscellaneous

- Change project license to MIT. [!15]

[!13]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/13
[!14]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/14
[!15]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/15


## [0.4.2](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.4.2) - 2023-08-21

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.4.1...0.4.2)

Add support for SQLAlchemy 2.0.

### Dependencies

- Update dependencies to support SQLAlchemy 2.0. [!11]
- Update build pipeline to test with both SQLAlchemy 1.4 and 2.0. [!11]

[!11]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/11


## [0.4.1](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.4.1) - 2023-05-24

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.4.0...0.4.1)

This release provides compatibility for [validataclass 0.9](https://github.com/binary-butterfly/validataclass/releases/tag/0.9.0)
and thus adds official support for Python 3.11.

### Dependencies

- Update validataclass dependency to version [0.9.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.9.0). [!10]
  - This adds support for Python 3.11.
- Update local test environment for tox 4. [!10]

[!10]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/10


## [0.4.0](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.4.0) - 2022-11-30

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.3.0...0.4.0)

This release provides compatibility for [validataclass 0.8](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.0).

### Changed

- Updated validataclass dependency to version [0.8.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.1). [!8]
- **Breaking change:** `MultiSelectAnyOfValidator` and `MultiSelectEnumValidator` are now case-sensitive by default. [!8]
  - This is the same change done in validataclass with the `AnyOfValidator` and `EnumValidator`.
  - The parameter `case_insensitive` is now deprecated and will be removed in a future version.
- The pagination and sorting parameters (e.g. `limit`) in the abstract mixin classes are now defined as regular attributes
  instead of abstract properties. [!9]
  - This solves typing/linting problems when manually assigning values to these attributes in a dataclass instance.

[!8]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/8
[!9]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/9


## [0.3.0](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.3.0) - 2022-11-22

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.2.2...0.3.0)

### Added

- `SearchParamCustom`: Special search parameter that raises an exception unless it's bypassed via a custom filter in the
  repository. [!6]

### Changed

- Enums are now automatically converted to their values in `BaseSearchQuery.to_dict()`. [!7]

### Fixed

- Type hint for `SearchQueryRepositoryMixin.model_cls` is now `Type[T_Model]` instead of just `Type`. [!7]

[!6]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/6
[!7]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/7


## [0.2.2](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.2.2) - 2022-10-27

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.2.1...0.2.2)

### Added

- `MultiSelectAnyOfValidator` and `MultiSelectEnumValidator`: Add (missing) parameter `case_insensitive`. [!5]

[!5]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/5


## [0.2.1](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.2.1) - 2022-09-29

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.2.0...0.2.1)

This release improves type hinting, based on validataclass 0.7.2.

### Changed

- Updated validataclass dependency to version [0.7.2](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.2)
  which improves the type hinting for validataclasses and the `DataclassValidator`. [!4]
- Improved type hinting for `@search_query_dataclass` decorator analogous to `@validataclass`. [!4]

[!4]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/4


## [0.2.0](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.2.0) - 2022-09-22

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/compare/0.1.0...0.2.0)

This release is an upgrade to validataclass 0.7.0.

The previous release is not compatible to this version of validataclass, and vice-versa.

### Changed

- Updated validataclass dependency to version [0.7.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.0). [!3]
  - Validators now support context-arguments.
  - MultiSelectValidators now have better type-hinting thanks to `ListValidator` and `EnumValidator` being generic now.
- `BaseSearchQuery`: Search filters that are set to `UnsetValue` are now discarded (same as `None`). [!3]

[!3]: https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/merge_requests/3


## [0.1.0](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/releases/0.1.0) - 2022-08-22

[Full changelog](https://git.binary-butterfly.de/public_libraries/validataclass-search-queries/-/commits/0.1.0)

This is the first non-alpha release of validataclass-search-queries.

### General

- Initial release.
