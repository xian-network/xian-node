# Xian Node

[![CI](https://github.com/xian-network/xian-node/actions/workflows/main.yml/badge.svg)](https://github.com/xian-network/xian-node/actions/workflows/main.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python-based ABCI (Application Blockchain Interface) server designed for CometBFT 0.38. This component serves as the core application layer for the Xian blockchain network.

## Requirements

- [Python 3.11.11](https://www.python.org/downloads/release/python-31111) (other versions are not officially supported)
- [CometBFT 0.38](https://docs.cometbft.com/v0.38) (specifically 0.38.x, not 0.37.x or 1.0.x)
- [PostgreSQL](https://www.postgresql.org) (for Blockchain Data Service)
- [PM2](https://pm2.keymetrics.io) (for process management)

## Dependencies Installation

### Python Installation

Xian Node requires Python 3.11.11 specifically. We recommend using [pyenv](https://github.com/pyenv/pyenv) to manage Python versions.

### Installing pyenv

- **macOS/Linux**: Follow the installation instructions at [https://github.com/pyenv/pyenv#installation](https://github.com/pyenv/pyenv#installation)
- **Windows**: Use [pyenv-win](https://github.com/pyenv-win/pyenv-win#installation) with instructions at [https://github.com/pyenv-win/pyenv-win#installation](https://github.com/pyenv-win/pyenv-win#installation)

### Installing Python 3.11.11 with pyenv

Once pyenv is installed, you can install and set up Python 3.11.11:

```bash
# Install Python 3.11.11
pyenv install 3.11.11

# Set it as your global Python version (optional)
pyenv global 3.11.11

# Verify the installation
python --version  # Should output Python 3.11.11
```

### Installing CometBFT 0.38

Xian Node requires [CometBFT 0.38.x](https://docs.cometbft.com/v0.38) specifically (not 0.37.x or 1.0.x). Follow these steps to install it:

1. Download the appropriate binary for your platform from the [CometBFT releases page](https://github.com/cometbft/cometbft/releases)
   - Make sure to select a release with version 0.38.x (e.g., v0.38.0, v0.38.1, etc.)

2. For Linux/macOS:
   ```bash
   # Example for Linux amd64, adjust the version number and OS/arch as needed
   wget https://github.com/cometbft/cometbft/releases/download/v0.38.0/cometbft_0.38.0_linux_amd64.tar.gz
   
   # Extract the tarball
   tar -xzf cometbft_0.38.0_linux_amd64.tar.gz
   
   # Move the binary to your PATH
   sudo mv cometbft /usr/local/bin/
   
   # Verify the installation
   cometbft version  # Should output v0.38.x
   ```

3. For Windows:
   - Download the appropriate Windows zip file
   - Extract the contents
   - Add the extracted directory to your PATH environment variable
   - Verify installation by running `cometbft version` in Command Prompt or PowerShell
   
Remember, it's crucial to use CometBFT 0.38.x as other versions are not compatible with Xian Node.

## Installation and Usage

There are multiple ways to set up and run Xian Node:

### Method 1: Production Installation (via PyPI)

```bash
# Ensure you're using Python 3.11.11
pyenv local 3.11.11

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install xian-node

# Initialize the node
xian-node init

# Start the node (standard mode)
xian-node up

# Start the node with Blockchain Data Service (BDS)
xian-node up --bds

# View logs
xian-node logs

# Stop the node
xian-node down
```

Additional commands:
```bash
xian-node node-id  # Get node ID
xian-node wipe     # Wipe blockchain data
xian-node help     # Show all available commands
```

### Method 2: Installation with Poetry

[Poetry](https://python-poetry.org) is a dependency management and packaging tool for Python. To install Poetry, follow the instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

```bash
# Ensure pyenv is set to Python 3.11.11
pyenv local 3.11.11

# Clone the repository
git clone https://github.com/xian-network/xian-node.git
cd xian-node

# Configure Poetry to use Python 3.11.11
poetry env use $(pyenv which python)

# Install dependencies with Poetry
poetry install

# Use Poetry to run commands
poetry run xian-node init
poetry run xian-node up

# Or activate the Poetry virtual environment and run directly
poetry shell
xian-node init
xian-node up
```

### Method 3: Development Installation (from source)

```bash
# Ensure you're using Python 3.11.11
pyenv local 3.11.11

# Clone the repository
git clone https://github.com/xian-network/xian-node.git
cd xian-node

# Create and activate a virtual environment
python -m venv xian-venv
source xian-venv/bin/activate  # On Windows: xian-venv\Scripts\activate
cd xian-node

# Install in development mode
pip install -e .

# Initialize CometBFT
make init

# Start the node (standard mode)
make up

# Start the node with Blockchain Data Service (BDS)
make up-bds

# View logs
make logs

# Stop all services
make down
```

Additional Makefile commands:
```bash
make dwu       # Down, wipe, init, up sequence
make node-id   # Show node ID
make ex-state  # Export state
```

## Key Features

- **ABCI Server**: Full implementation of CometBFT's ABCI protocol
- **Smart Contract Support**: Execution environment for Python-based smart contracts
- **State Management**: Advanced state handling with Hash and Variable storage types
- **Transaction Processing**: Comprehensive transaction validation and execution
- **Event System**: Rich event logging system for tracking contract and state changes
- **Blockchain Data Service (BDS)**: PostgreSQL-based service for storing and querying blockchain data
- **Validator Management**: Flexible validator set management
- **Rewards System**: Built-in system for handling transaction fees and rewards

## Blockchain Data Service (BDS)

The Blockchain Data Service provides additional data storage and querying capabilities:
- Store blockchain data in a PostgreSQL database
- Enable advanced querying and indexing of blockchain state
- Enhance performance for complex data retrieval

### Starting with BDS

To start the node with the Blockchain Data Service enabled, use:
```bash
# In PyPI installation
xian-node up --bds

# In development mode
make up-bds
```

## Configuration

The node uses several configuration files:

- CometBFT configuration: `~/.cometbft/config/config.toml`
- Genesis file: `~/.cometbft/config/genesis.json`
- BDS configuration: Located in the BDS service directory

## Query Interface

Examples of querying the node:

```bash
# Get contract state
curl "http://localhost:26657/abci_query?path=\"/get/currency.balances:ADDRESS\""

# Get node health
curl "http://localhost:26657/abci_query?path=\"/health\""

# Get next nonce
curl "http://localhost:26657/abci_query?path=\"/get_next_nonce/ADDRESS\""
```

## Development

### Testing
```bash
# Run tests
python -m pytest tests/
```

## License

This project is licensed under the Apache License Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [xian-stack](https://github.com/xian-network/xian-stack): Complete blockchain stack deployment packaged as a Docker container
- [xian-contracting](https://github.com/xian-network/xian-contracting): Smart contract engine used by xian-node
- [xian-js](https://github.com/xian-network/xian-py): JavaScript SDK for xian-node
- [xian-py](https://github.com/xian-network/xian-js): Python SDK for xian-node

## Repository Stats

![Alt](https://repobeats.axiom.co/api/embed/24d5a438ef0cf14c5f02c7286d04f83148bb192f.svg "Repobeats analytics image")