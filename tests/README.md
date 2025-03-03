# Xian Network Testing Guide

## Overview

This guide explains how to run and understand the test suite for the Xian Network node. Tests are crucial for ensuring the reliability and correctness of the blockchain implementation.

## Motivation

All tests in Xian run in a standardized environment where variables are controlled and predictable. This ensures:

- Reproducible test outcomes across different environments
- Isolation between test cases
- Clear test failures that can be easily debugged

## Test Architecture

The test suite is organized into several categories:

- **Unit Tests** (`tests/unit/`): Tests for individual components and utility functions
- **System Tests** (`tests/system/`): Tests for core system contracts (currency, vault, members)
- **Integration Tests** (`tests/integration/`): Tests for interactions between components
- **ABCI Method Tests** (`tests/abci_methods/`): Tests for CometBFT ABCI interface
- **Governance Tests** (`tests/governance/`): Tests for on-chain governance mechanisms

## Environment Setup

Tests use these key principles:

1. **Fixture Management**:
   - A `.cometbft-fixture` directory contains baseline configurations 
   - This is copied to `/tmp/cometbft/` at the start of each test
   - Tests run against this temporary environment for isolation
   - Each test starts with a clean state

2. **Constants Override**:
   - `MockConstants` overrides production settings during tests
   - This prevents tests from interacting with real blockchain data

## Running the Tests

### Prerequisites

Ensure you have all dependencies installed:

```bash
# Install the package in development mode with test dependencies
pip install -e .
```

### Running Tests with pytest

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/system/
python -m pytest tests/integration/
python -m pytest tests/abci_methods/
python -m pytest tests/governance/

# Run a specific test file
python -m pytest tests/system/test_currency.py

# Run a specific test class or method
python -m pytest tests/system/test_currency.py::TestCurrencyContract
python -m pytest tests/system/test_currency.py::TestCurrencyContract::test_transfer

# Run with verbose output
python -m pytest tests/ -v

# Display print statements during tests
python -m pytest tests/ -s

# Run only tests matching a pattern
python -m pytest tests/ -k "transfer"
```

### Running Tests with unittest

```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests/system/test_currency.py

# Run a specific test class
python -m unittest tests.system.test_currency.TestCurrencyContract

# Run a specific test method
python -m unittest tests.system.test_currency.TestCurrencyContract.test_transfer
```

## Writing New Tests

When writing new tests:

1. **Use the fixture system**:
```python
from fixtures.mock_constants import MockConstants
from utils import setup_fixtures, teardown_fixtures

class TestExample(unittest.TestCase):
    def setUp(self):
        setup_fixtures()
        # Additional setup code here
        
    def tearDown(self):
        teardown_fixtures()
        # Additional cleanup code here
```

2. **Override constants** using `MockConstants`
3. **Ensure proper cleanup** after tests
4. **Make tests independent** from each other

## Test Debugging

If tests are failing:

1. Run with verbose flags (`-v`, `-s`)
2. Check that fixtures are being set up correctly
3. Examine temporary directories created during tests
4. Verify the Python version (tests require Python 3.11.11)

## CI/CD Integration

Tests run automatically on GitHub Actions for:
- Pull requests 
- Commits to all branches
- Release processes

The CI pipeline runs tests against a PostgreSQL service for database-dependent tests.

## Best Practices

- Keep tests small and focused on a single feature
- Use descriptive test method names
- Add comments explaining complex test scenarios
- Ensure tests are deterministic (no random behavior)
- Avoid tests with external dependencies when possible

By following this guide, you'll be able to effectively run, debug, and contribute to the Xian Network test suite.