# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.2.0) - 2022-09-22

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/compare/0.1.0...0.2.0)

### Changed

- Updated validataclass dependency to version [0.7.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.0). [#3]
  - Validators now support context-arguments.
  - MultiSelectValidators now have better type-hinting thanks to `ListValidator` and `EnumValidator` being generic now.
- `BaseSearchQuery`: Search filters that are set to `UnsetValue` are now discarded (same as `None`). [#3]

[#3]: https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/merge_requests/3


## [0.1.0](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/releases/0.1.0) - 2022-08-22

[Full changelog](https://git.sectio-aurea.org/public_libraries/validataclass-search-queries/-/commits/0.1.0)

### General

- Initial release.
