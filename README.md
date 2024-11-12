# aact-openhands

Openhands x AAct

## Overview

This project integrates the Openhands framework with AAct to create a runtime environment for executing actions and handling events. The `openhands_node.py` file defines the `OpenHands` class, which is a node that processes actions and communicates with a runtime environment.

## Project Structure

- `openhands/`: Contains the core implementation of the Openhands node and related utilities.
  - `openhands_node.py`: Main implementation of the OpenHands node.
  - `utils.py`: Contains utility classes and functions, including `AgentAction` and `ActionType`.
  - `__init__.py`: Marks the directory as a Python package.

- `examples/`: Contains example configuration files.
  - `openhands_node.toml`: Configuration file for running the OpenHands node.

- `pyproject.toml`: Configuration file for managing dependencies with Poetry.

## Installation

To set up the project, ensure you have Python 3.12 installed. Then, follow these steps:

1. **Install Poetry**: If you haven't already, install Poetry for dependency management.
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install Dependencies**: Navigate to the project directory and install the dependencies.
   ```bash
   poetry install
   ```

## Usage

### Running the OpenHands Node

To run the OpenHands node with the provided configuration, use the following command:
