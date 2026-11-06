# this is an optional command runner using the "just" cli tool to make a starting server's
# and complex command easier

# more info on how to install here: https://github.com/casey/just#packages
# or run: `uv tool install rust-just`
# then run a recipe like 'just run' in your console

# uv if installed, otherwise the activated virtual environment's python
PYTHON := `command -v uv >/dev/null 2>&1 && echo "uv run python" || echo "python"`

# run the main script
run:
    {{ PYTHON }} main.py

# run the test suite
test:
    {{ PYTHON }} -m pytest -v tests/unit/

# format, lint and type check the code
check:
    ruff format . && ruff check .
    ty check .

# install app + dev dependencies (uv, or pip into the activated virtual environment)
install-deps:
    if command -v uv >/dev/null 2>&1; then uv sync; else python -m pip install -r requirements-dev.txt; fi

# regenerate requirements.txt and requirements-dev.txt from pyproject.toml (maintainers; needs uv)
update-dependencies:
    @command -v uv >/dev/null 2>&1 || { echo "error: update-dependencies needs uv. The requirements files are generated with 'uv pip compile', and plain pip can't read the [dependency-groups] table in pyproject.toml. Install uv: https://docs.astral.sh/uv/"; exit 1; }
    uv pip compile pyproject.toml -o requirements.txt
    uv pip compile pyproject.toml --group dev -o requirements-dev.txt
