"""
Cookiecutter Broker Template for pit-38
----------------------------------------
MVP implementation for pbialon/pit-38#50

Usage:
    cookiecutter gh:pbialon/pit-38 --directory templates/broker

This creates a new broker plugin project with:
- Standard directory structure
- Base broker class implementation
- Configuration templates
- Tests
- CI/CD pipeline
"""

import os
import sys
from pathlib import Path
from typing import Optional


# ============================================================
# Broker Plugin Template (for cookiecutter)
# ============================================================

TEMPLATE_STRUCTURE = {
    "{{cookiecutter.project_slug}}": {
        ".github": {
            "workflows": {
                "ci.yml": ".github/workflows/ci.yml",
            },
        },
        "src": {
            "{{cookiecutter.project_slug}}": {
                "__init__.py": "src/__init__.py",
                "broker.py": "src/broker.py",
                "config.py": "src/config.py",
                "exceptions.py": "src/exceptions.py",
            },
        },
        "tests": {
            "__init__.py": "tests/__init__.py",
            "test_broker.py": "tests/test_broker.py",
            "conftest.py": "tests/conftest.py",
        },
        "docs": {
            "index.md": "docs/index.md",
        },
        ".gitignore": ".gitignore",
        "pyproject.toml": "pyproject.toml",
        "README.md": "README.md",
        "LICENSE": "LICENSE",
    }
}


# ============================================================
# Template Files
# ============================================================

PYPROJECT_TOML = """\
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "{{ cookiecutter.project_slug }}"
version = "{{ cookiecutter.version }}"
description = "{{ cookiecutter.description }}"
readme = "README.md"
license = {text = "{{ cookiecutter.license }}"}
authors = [
    {name = "{{ cookiecutter.author }}", email = "{{ cookiecutter.email }}"},
]
requires-python = ">=3.10"
keywords = ["pit-38", "broker", "trading", "plugin"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: {{ cookiecutter.license }}",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "pit-38>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[project.entry-points."pit38.broker"]
{{ cookiecutter.broker_name }} = "{{ cookiecutter.project_slug }}:get_broker"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
strict = true
"""

BROKER_PY = '''\
"""
{{ cookiecutter.broker_name }} Broker Plugin for pit-38
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pit38.broker.base import BaseBroker
from pit38.models import Order, Position, Trade

from .config import BrokerConfig
from .exceptions import BrokerConnectionError, BrokerAPIError

logger = logging.getLogger(__name__)


class {{ cookiecutter.broker_name }}Broker(BaseBroker):
    """
    Broker plugin for {{ cookiecutter.broker_name }}.

    Implements the pit-38 broker interface for {{ cookiecutter.broker_name }}.
    """

    name = "{{ cookiecutter.broker_name }}"
    version = "{{ cookiecutter.version }}"

    def __init__(self, config: BrokerConfig):
        self.config = config
        self._connected = False
        self._client: Optional[Any] = None
        logger.info(f"Initialized {{ cookiecutter.broker_name }}Broker v{{ cookiecutter.version }}")

    async def connect(self) -> None:
        """Establish connection to {{ cookiecutter.broker_name }}."""
        if self._connected:
            return

        try:
            # TODO: Implement actual connection logic
            # self._client = await self.config.create_client()
            self._connected = True
            logger.info(f"Connected to {{ cookiecutter.broker_name }}")
        except Exception as e:
            raise BrokerConnectionError(f"Failed to connect: {e}") from e

    async def disconnect(self) -> None:
        """Close connection to {{ cookiecutter.broker_name }}."""
        if not self._connected:
            return

        # TODO: Implement actual disconnect logic
        self._connected = False
        self._client = None
        logger.info(f"Disconnected from {{ cookiecutter.broker_name }}")

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def get_positions(self) -> List[Position]:
        """Retrieve current positions."""
        if not self._connected:
            raise BrokerConnectionError("Not connected")

        # TODO: Implement actual position fetching
        logger.debug("Fetching positions from {{ cookiecutter.broker_name }}")
        return []

    async def place_order(self, order: Order) -> Trade:
        """Place an order."""
        if not self._connected:
            raise BrokerConnectionError("Not connected")

        # TODO: Implement actual order placement
        logger.info(f"Placing order: {order}")
        raise NotImplementedError("Order placement not yet implemented")

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if not self._connected:
            raise BrokerConnectionError("Not connected")

        # TODO: Implement actual order cancellation
        logger.info(f"Cancelling order: {order_id}")
        raise NotImplementedError("Order cancellation not yet implemented")

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        if not self._connected:
            raise BrokerConnectionError("Not connected")

        # TODO: Implement actual account info fetching
        return {
            "broker": self.name,
            "version": self.version,
            "connected": self._connected,
        }


def get_broker(config: BrokerConfig) -> {{ cookiecutter.broker_name }}Broker:
    """Factory function for pit-38 plugin discovery."""
    return {{ cookiecutter.broker_name }}Broker(config)
'''

CONFIG_PY = '''\
"""Configuration for {{ cookiecutter.broker_name }} broker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrokerConfig:
    """Configuration for {{ cookiecutter.broker_name }} broker connection."""

    # API credentials
    api_key: str = ""
    api_secret: str = ""

    # Connection settings
    base_url: str = "{{ cookiecutter.api_base_url }}"
    timeout: float = 30.0
    max_retries: int = 3

    # Trading settings
    paper_trading: bool = True
    default_symbol: str = ""

    # Optional settings
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        import os
        if not self.api_key:
            self.api_key = os.environ.get("{{ cookiecutter.env_prefix }}_API_KEY", "")
        if not self.api_secret:
            self.api_secret = os.environ.get("{{ cookiecutter.env_prefix }}_API_SECRET", "")

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("API key is required. Set via config or {{ cookiecutter.env_prefix }}_API_KEY env var.")
'''

EXCEPTIONS_PY = '''\
"""Custom exceptions for {{ cookiecutter.broker_name }} broker."""


class BrokerError(Exception):
    """Base exception for broker errors."""


class BrokerConnectionError(BrokerError):
    """Raised when connection to broker fails."""


class BrokerAPIError(BrokerError):
    """Raised when broker API returns an error."""

    def __init__(self, message: str, status_code: int = 0, response: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BrokerTimeoutError(BrokerError):
    """Raised when broker request times out."""


class BrokerRateLimitError(BrokerError):
    """Raised when broker rate limit is exceeded."""
'''

INIT_PY = '''\
"""{{ cookiecutter.broker_name }} broker plugin for pit-38."""

from .broker import {{ cookiecutter.broker_name }}Broker, get_broker
from .config import BrokerConfig
from .exceptions import (
    BrokerAPIError,
    BrokerConnectionError,
    BrokerError,
    BrokerRateLimitError,
    BrokerTimeoutError,
)

__version__ = "{{ cookiecutter.version }}"
__all__ = [
    "{{ cookiecutter.broker_name }}Broker",
    "BrokerConfig",
    "BrokerError",
    "BrokerConnectionError",
    "BrokerAPIError",
    "BrokerTimeoutError",
    "BrokerRateLimitError",
    "get_broker",
]
'''

README_MD = '''\
# {{ cookiecutter.project_slug }}

{{ cookiecutter.description }}

## Installation

```bash
pip install {{ cookiecutter.project_slug }}
```

## Configuration

Set your API credentials via environment variables:

```bash
export {{ cookiecutter.env_prefix }}_API_KEY="your_api_key"
export {{ cookiecutter.env_prefix }}_API_SECRET="your_api_secret"
```

Or via config file:

```python
from {{ cookiecutter.project_slug }} import BrokerConfig, {{ cookiecutter.broker_name }}Broker

config = BrokerConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    paper_trading=True,
)
broker = {{ cookiecutter.broker_name }}Broker(config)
```

## Usage

```python
import asyncio
from {{ cookiecutter.project_slug }} import {{ cookiecutter.broker_name }}Broker, BrokerConfig

async def main():
    config = BrokerConfig(paper_trading=True)
    broker = {{ cookiecutter.broker_name }}Broker(config)

    await broker.connect()
    positions = await broker.get_positions()
    print(f"Positions: {positions}")

    account = await broker.get_account_info()
    print(f"Account: {account}")

    await broker.disconnect()

asyncio.run(main())
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## License

{{ cookiecutter.license }}
'''

TEST_BROKER_PY = '''\
"""Tests for {{ cookiecutter.broker_name }} broker."""

import pytest
from {{ cookiecutter.project_slug }} import (
    {{ cookiecutter.broker_name }}Broker,
    BrokerConfig,
    BrokerConnectionError,
)


class TestBrokerConfig:
    def test_default_config(self):
        config = BrokerConfig()
        assert config.paper_trading is True
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_custom_config(self):
        config = BrokerConfig(
            api_key="test_key",
            api_secret="test_secret",
            paper_trading=False,
            timeout=60.0,
        )
        assert config.api_key == "test_key"
        assert config.paper_trading is False
        assert config.timeout == 60.0

    def test_validate_missing_key(self):
        config = BrokerConfig()
        with pytest.raises(ValueError, match="API key is required"):
            config.validate()

    def test_validate_with_key(self):
        config = BrokerConfig(api_key="test_key")
        config.validate()  # Should not raise


class Test{{ cookiecutter.broker_name }}Broker:
    @pytest.fixture
    def broker(self):
        config = BrokerConfig(api_key="test_key")
        return {{ cookiecutter.broker_name }}Broker(config)

    def test_broker_name(self, broker):
        assert broker.name == "{{ cookiecutter.broker_name }}"

    def test_broker_version(self, broker):
        assert broker.version == "{{ cookiecutter.version }}"

    def test_not_connected_initially(self, broker):
        assert broker.is_connected is False

    @pytest.mark.asyncio
    async def test_connect(self, broker):
        # TODO: Mock the actual connection
        # await broker.connect()
        # assert broker.is_connected is True
        pass

    @pytest.mark.asyncio
    async def test_get_positions_not_connected(self, broker):
        with pytest.raises(BrokerConnectionError):
            await broker.get_positions()

    @pytest.mark.asyncio
    async def test_get_account_info_not_connected(self, broker):
        with pytest.raises(BrokerConnectionError):
            await broker.get_account_info()


class TestGetBroker:
    def test_factory_function(self):
        from {{ cookiecutter.project_slug }} import get_broker
        config = BrokerConfig(api_key="test_key")
        broker = get_broker(config)
        assert isinstance(broker, {{ cookiecutter.broker_name }}Broker)
'''

CONFTEST_PY = '''\
"""Pytest configuration for {{ cookiecutter.project_slug }}."""

import pytest


@pytest.fixture
def sample_config():
    """Provide a sample broker configuration for tests."""
    from {{ cookiecutter.project_slug }} import BrokerConfig
    return BrokerConfig(
        api_key="test_key",
        api_secret="test_secret",
        paper_trading=True,
    )
'''

GITIGNORE = '''\
# Byte-compiled / optimized
__pycache__/
*.py[cod]
*$py.class

# Distribution
dist/
build/
*.egg-info/
*.egg

# Virtual environments
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# MyPy
.mypy_cache/

# OS
.DS_Store
Thumbs.db
'''

CI_YML = '''\
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy src/

      - name: Test with pytest
        run: pytest --cov={{ cookiecutter.project_slug }} --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
'''

LICENSE_TEXT = """\
{{ cookiecutter.license }}

Copyright (c) {{ cookiecutter.year }} {{ cookiecutter.author }}
"""


def generate_template_files(output_dir: str, context: dict) -> None:
    """Generate all template files with context substitution."""
    context.setdefault("year", "2026")

    files = {
        "pyproject.toml": PYPROJECT_TOML,
        "src/__init__.py": INIT_PY,
        "src/broker.py": BROKER_PY,
        "src/config.py": CONFIG_PY,
        "src/exceptions.py": EXCEPTIONS_PY,
        "tests/__init__.py": "",
        "tests/test_broker.py": TEST_BROKER_PY,
        "tests/conftest.py": CONFTEST_PY,
        "docs/index.md": f"# {context.get('project_slug', 'broker-plugin')}\n\nDocumentation coming soon.\n",
        ".github/workflows/ci.yml": CI_YML,
        ".gitignore": GITIGNORE,
        "README.md": README_MD,
        "LICENSE": LICENSE_TEXT,
    }

    for filepath, content in files.items():
        # Simple context substitution
        for key, value in context.items():
            content = content.replace(f"{{{{ cookiecutter.{key} }}}}", str(value))

        full_path = os.path.join(output_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    print(f"Generated {len(files)} files in {output_dir}")


def demo():
    """Generate a demo broker plugin."""
    import tempfile

    context = {
        "project_slug": "my-example-broker",
        "broker_name": "MyExample",
        "version": "0.1.0",
        "description": "Example broker plugin for pit-38",
        "author": "Your Name",
        "email": "you@example.com",
        "license": "MIT",
        "api_base_url": "https://api.example.com/v1",
        "env_prefix": "MYEXAMPLE",
        "year": "2026",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        generate_template_files(tmpdir, context)
        print(f"\nDemo broker plugin generated in: {tmpdir}")

        # List generated files
        for root, dirs, files in os.walk(tmpdir):
            level = root.replace(tmpdir, "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")


if __name__ == "__main__":
    demo()
