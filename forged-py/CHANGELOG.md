# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0 - 2025-11-17

## Changed
* Added support for synchronous access to the forged API
* The `forged.upload_value` and friends have been changed to sync by default.
* Added a new `Forged.upload_block` method to simplify API access

## Fixed
* Locked the gql dependency to avoid failures due to unsupported deprecation features.

## 0.1.0 - 2023-05-05

### Added
* Support now added for querying uploaded blocks for the current run.
