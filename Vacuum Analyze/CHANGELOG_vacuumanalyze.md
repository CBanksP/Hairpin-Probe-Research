# Changelog for vacuum_analysis.py

All notable changes to this script will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1] - 2024-07-07
### Added
- If curve fitting fails, the script now plots the raw data for inspection
- Added more informative print statements to guide the user through the analysis process

### Changed

### Fixed
- Added better initial parameter estimation using find_peaks to locate the highest peak in the data
- Increased the maximum number of function evaluations (maxfev) in curve_fit to allow more iterations for convergence
- Implemented error handling to catch the RuntimeError that occurs when curve fitting fails

## [1.0] - 2024-07-07
### Added
- Initial release of vacuum_analysis.py
- Data loading and preprocessing
- Multiple methods for resonance detection (Maximum, Gaussian Fit, Peak Detection)
- Result visualization and plotting

### Changed

### Fixed