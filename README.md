# Xian Node

[![CI](https://github.com/xian-network/xian-node/actions/workflows/main.yml/badge.svg)](https://github.com/xian-network/xian-node/actions/workflows/main.yml)

Python-based ABCI (Application Blockchain Interface) server designed for CometBFT 0.38. This component serves as the core application layer for the Xian blockchain network.

## Requirements

- Python 3.11.11 (other versions are not supported)
- CometBFT 0.38
- PostgreSQL (for Blockchain Data Service)
- PM2 (for process management)

## Installation and Usage

There are multiple ways to set up and run Xian Core:

### Method 1: Production Installation (via PyPI)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

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

```bash
# Clone the repository
git clone https://github.com/xian-network/xian-node.git
cd xian-node

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
# Clone the repository
git clone https://github.com/xian-network/xian-node.git
cd xian-node

# Create and activate a virtual environment
python3.11 -m venv xian-venv
source xian-venv/bin/activate
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

## Architecture Components

- **ABCI Server**: Handles communication with CometBFT
- **Transaction Processor**: Manages transaction execution and state updates
- **Validator Handler**: Manages validator set changes
- **Rewards Handler**: Processes transaction fees and rewards
- **Nonce Manager**: Handles transaction ordering
- **Event System**: Tracks and logs blockchain events
- **Blockchain Data Service**: Provides advanced data storage and querying

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

- [xian-contracting](https://github.com/xian-network/xian-contracting): Smart contract engine
- [xian-stack](https://github.com/xian-network/xian-stack): Complete blockchain stack deployment

## Repository Stats

![Alt](https://repobeats.axiom.co/api/embed/24d5a438ef0cf14c5f02c7286d04f83148bb192f.svg "Repobeats analytics image")