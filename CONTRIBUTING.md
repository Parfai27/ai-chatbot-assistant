# Contributing

Contributions are welcome. Please follow the steps below to keep the project consistent and easy to review.

## Development workflow

1. Fork the repository and create a feature branch.
2. Create a Python virtual environment and install dependencies.
3. Make your changes and add or update tests where appropriate.
4. Run the test suite and ensure formatting checks pass.
5. Open a pull request with a clear summary of the change.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
```

## Testing

```bash
python scripts/run_tests.py
```

## Coding style

- Keep code modular and readable.
- Prefer descriptive names and small, focused functions.
- Update documentation when public behavior changes.
