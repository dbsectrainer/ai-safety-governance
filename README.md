# AI Safety & Governance

[... previous content remains the same until the "Development" section ...]

## Development

### Python Environment Setup

#### Recommended Python Version
- **Supported Versions**: Python 3.10 - 3.11
- **Recommended Version**: Python 3.11
- **Not Supported**: Python 3.12+

#### Virtual Environment Setup
```bash
# Install virtualenv (if not already installed)
pip install virtualenv

# Create a virtual environment
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Unix/macOS
# OR
venv\Scripts\activate     # On Windows

# Install project dependencies
pip install -r requirements.txt
```

### Dependency Management
- Use `pip` to install dependencies
- Always use a virtual environment
- If you encounter installation issues, update pip:
  ```bash
  pip install --upgrade pip
  ```

### Running Tests

#### Basic Test Execution
```bash
# Ensure virtual environment is activated
PYTHONPATH=. python -m pytest tests/
```

#### Troubleshooting Test Runs
1. **ModuleNotFoundError**
   - Ensure you are in the project root directory
   - Verify virtual environment is activated
   - Check that `__init__.py` files exist in all package directories

2. **Python Path Issues**
   - Use `PYTHONPATH=.` before running pytest
   - Verify your Python version matches project requirements

3. **Dependency Conflicts**
   - Create a fresh virtual environment
   - Reinstall dependencies
   - Check `requirements.txt` for version constraints

### Local Development
```bash
# Start local development environment
docker-compose up -d

# Run tests with verbose output
PYTHONPATH=. python -m pytest -v tests/

# Run security checks
safety check
bandit -r src/
```

[... rest of the previous content remains the same ...]
