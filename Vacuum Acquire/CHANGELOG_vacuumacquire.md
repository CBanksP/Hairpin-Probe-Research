# Changelog for vacuum_acquire.py

All notable changes to this script will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.6] - 2024-07-09
### Added

### Changed

### Fixed
- The email includes the plot properly and the toggle feature is fixed

## [2.5] - 2024-07-08
### Added

### Changed
- Improved layout

### Fixed

## [2.4] - 2024-07-08
### Added

### Changed
- The email addresses and password are stored in an .env file so that they are not in the script

### Fixed

## [2.3] - 2024-07-08
### Added
- Raw plot will be attached to the email

### Changed

### Fixed

## [2.2] - 2024-07-08
### Added
- Ability to easily toggle the email notification

### Changed

### Fixed

## [2.1] - 2024-07-08
### Added
- Will estimate the time of completion based upon a certain number of estimation steps set by the user

### Changed

### Fixed

## [2.0] - 2024-07-08
### Added
- Will email the user when the sweep is over to save time

### Changed

### Fixed


## [1.3] - 2024-07-08
### Added
- Short delay between frequency steps to potentially avoid an error
- Error handling to skip a frequency if error occurs there
- Will print if an error occurs
- Control number of decimals for frequency precision by rounding up to specified resolution

### Changed

### Fixed
- Issue where command would be issued to MW generator that exceeded it 0.1 Hz resolution

## [1.2] - 2024-07-08
### Added
- Plots the raw data after the sweep for a quick diagnosis

### Changed

### Fixed

## [1.1] - 2024-07-07
### Added
- Prints out current MW frequency so that progress is known
- More information is printed at initiation of the sweep

### Changed

### Fixed

## [1.0] - 2024-07-07
### Added
- Initial release of vacuum_acquire_v3.py
- Basic data acquisition functionality
- Configurable frequency range and step size
- Data saving in .pkl format

### Changed

### Fixed