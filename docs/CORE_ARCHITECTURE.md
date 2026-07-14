# PTH Fausta — Core Architecture

**Document version:** 1.0
**Status:** Approved
**Last updated:** 2026-07-14

---

# Purpose

This document defines the architecture of the **PTH Fausta Core**.

The Core layer provides the technical foundation of the application. Every higher layer (MVC, services, repositories, UI, etc.) depends on the Core, while the Core itself must remain independent of business logic.

The primary goal of the Core is stability, predictability and long-term maintainability.

---

# Design Principles

The Core follows these principles:

* Single Responsibility Principle (SRP)
* Explicit dependencies
* No hidden global state
* Predictable initialization
* Fail fast
* Testability
* Standard Library first
* Clear separation of responsibilities

Whenever there is uncertainty, simplicity is preferred over cleverness.

---

# Dependency Direction

The dependency graph is strictly one-way.

```text
main.py
    │
    ▼
Application
    │
    ▼
AppConfig
    │
    ├── ProjectPaths
    ├── SettingsManager
    ├── Logger
    ├── Version
    └── Future Core Services
```

No Core module may depend on MVC, GUI or business logic.

---

# Core Modules

## paths.py

Responsible for:

* project directory discovery
* runtime directory creation
* project structure validation

Not responsible for:

* application configuration
* logging
* settings
* business logic

---

## logger.py

Responsible for:

* logging configuration
* log formatting
* log file creation
* application loggers

Not responsible for:

* GUI messages
* error dialogs
* exception handling policy

---

## settings.py

Responsible for:

* application settings model
* settings validation
* JSON loading
* atomic JSON saving

Not responsible for:

* user interface
* deciding when settings are saved

---

## config.py

Responsible for:

* initialization of Core components
* dependency composition
* exposing Core services

Not responsible for:

* application lifecycle
* GUI
* business logic

---

## version.py

Responsible for:

* application identity
* semantic version information
* version validation

---

## app.py

Responsible for:

* application lifecycle
* startup
* shutdown
* execution flow

Not responsible for:

* process entry point
* system exit
* user interaction

---

## main.py

Responsible only for:

* creating Application
* transferring the exit code to the operating system

Nothing else.

---

# Initialization Sequence

Application startup follows this exact order:

```text
ProjectPaths
        │
        ▼
Validate project structure
        │
        ▼
SettingsManager
        │
        ▼
Load settings
        │
        ▼
Configure logging
        │
        ▼
Create AppConfig
        │
        ▼
Create Application
        │
        ▼
Run application
```

This order must not be changed without an architectural decision.

---

# Import Rules

Allowed direction:

```text
main
    ↓
core.app
    ↓
core.config
    ↓
other Core modules
```

Forbidden:

* circular imports
* MVC importing Core internals through side effects
* GUI initialization inside Core
* business logic inside Core

---

# Error Handling Policy

Core modules must never silently ignore errors.

Unexpected situations should raise explicit exceptions.

Errors are handled only by higher application layers.

---

# Logging Policy

Only one logging configuration exists.

No module may call:

* logging.basicConfig()

No module may configure logging independently.

All loggers are created through:

```python
get_logger(...)
```

---

# Settings Policy

Settings are stored in:

```text
database/settings.json
```

Saving is atomic.

Invalid settings never overwrite existing valid data.

---

# Project Structure Policy

Project directories are divided into two groups.

## Required directories

These must already exist.

```text
src
database
resources
docs
tests
```

Missing required directories indicate a damaged project structure.

---

## Runtime directories

Created automatically when needed.

Currently:

```text
logs
```

Future examples:

```text
cache
temp
exports
backups
```

---

# Testing Policy

Every Core module must have dedicated unit tests.

New functionality is accepted only after:

* successful compilation
* successful unit tests
* architecture review

---

# Coding Standards

Core code must:

* use type hints
* use pathlib
* follow PEP 8
* use English identifiers
* contain English docstrings

---

# Architectural Restrictions

Core must never:

* know about GUI
* know about controllers
* know about repositories
* know about business rules
* know about invoice processing
* know about database schema

Those responsibilities belong to higher layers.

---

# Future Development

The Core is considered stable.

Future work should extend the application by adding higher-level layers without changing the Core architecture unless a documented architectural decision requires it.

Any modification affecting the Core architecture must be reviewed before implementation.

---

# Approval

**Status:** Approved

This document defines the official architecture of the PTH Fausta Core and serves as the primary technical reference for all future development.
