# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## About

Isabl Skills provides Claude Code skills and an MCP server for the Isabl genomics platform. It enables seamless interaction with Isabl's data management, analysis, and visualization capabilities through AI-powered tools and workflows.

## [0.1.0] - 2026-02-02

### Added

- Initial release of Isabl Skills and MCP server
- 8 Claude Code skills for guided Isabl workflows:
  - `/isabl-query-data` - Query data from Isabl API
  - `/isabl-write-app` - Create new Isabl applications
  - `/isabl-monitor-analyses` - Track analysis status
  - `/isabl-debug-analysis` - Debug failed analyses
  - `/isabl-merge-results` - Aggregate results across analyses
  - `/isabl-submit-data` - Submit new sequencing data
  - `/isabl-project-report` - Generate project status reports
  - `/isabl-run-pipeline` - Run multiple apps as a pipeline
- MCP server with 9 tools for programmatic Isabl API access
- Consolidated install script for easy setup
- Project structure with clear separation of user-facing skills and development files
- CI/CD pipeline configuration
- Comprehensive documentation including CLAUDE.md and CONTRIBUTING.md

### Changed

- Merged `search_apps` and `explain_app` tools into a single `get_apps` tool for improved efficiency
- Removed application path configuration in favor of API-based app discovery
- Restructured repository to separate user-facing skills from development documentation
- Consolidated multiple install scripts into a unified install.sh

### Fixed

- Resolved CI/CD implementation issues
- Fixed skill code bugs for reliable operation
- Corrected MCP server implementation for proper tool registration and execution
