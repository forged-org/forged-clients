# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.3.1 - 2026-10-14

## Changed
* The client no longer fetches the GraphQL schema on every connection, saving about a second per
  upload.
* gql's per-request transport logging is now quieted to `WARNING`, so request and response bodies
  no longer flood test output and the run's command log.

## 0.3.0 - 2026-10-09

## Added
* Added `forged.upload_attachment` (and `Forged.upload_attachment`) to attach files, such as plots,
  to the current run.

## Changed
* `Forged.upload_value` and `Forged.upload_block` now log and ignore errors communicating with
  forged.dev (server errors, rejected requests, connection failures and timeouts) instead of
  raising, so a failed upload no longer aborts the running test.

## Fixed
* Fixed an issue where the user input socket was left alive after user input requests were handled.

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
