# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.6.0] - 2025-03-19

### Added
- Added support for custom edge behaviors, through the new `queue` argument at `add_node`
  for a custom queue object. (#14)

### Deprecated
- Deprecated the `queue_size` argument at `add_node` -- use the new `queue` instead. (#14)

### Security
- Resolved CVE-2024-56326, CVE-2024-56201, and CVE-2025-27516
  by updating jinja2 to v3.1.6 in requirements for Sphinx docs. (#14)

## [1.5.1] - 2024-11-07

### Added
- Added static type checking using mypy. (#12)

### Fixed
- Fixed documentation to actually show example code. (#12)

## [1.5.0] - 2024-10-30

### Added
- Python 3.13 is officially supported and tested on CI. (#11)

### Changed
- Migrated the docs to the Read The Docs site. (#11)

## [1.4.0] - 2023-11-30

### Added
- Python 3.12 is officially supported and tested on CI.
- Added a technical notes page to the Sphinx documentation.

## [1.3.0] - 2023-06-20

### Added
- `AsyncGraph.add_node` has the new keyword argument `check_async_gen` 
  to optionally disable the async generator function check for advanced usage.

## [1.2.0] - 2023-04-25

### Added
- An `AsyncExecutor` instance now has the `start_nodes` property.
  It maps start nodes to their arguments passed in at the beginning of graph execution. 

### Fixed
- Before a graph executes, the `exceptions` property of an `AsyncExecutor` instance 
  now returns `None`. Previously, accessing this property before graph execute
  would raise an exception.

## [1.1.0] - 2023-03-02

### Added
- Keep track of and expose exceptions. (#6)

## [1.0.0] - 2023-01-05

First release!
