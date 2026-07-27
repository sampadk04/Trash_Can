# UV Setup

UV Installation:

```bash
 curl -LsSf https://astral.sh/uv/install.sh | sh
 
 # OR BREW INSTALL UV (RECOMMENDED IN MAC)
```

UV DOCS:

https://docs.astral.sh/uv/guides/install-python/

!image.png

!image.png

# Conda Setup

Below is a clean, structured, and professionally polished version of your tutorial, suitable for internal documentation, onboarding guides, or a README.

---

# Conda Environment Management Guide

This guide covers creating, cloning, activating, and deleting Conda environments, along with configuring Python interpreters in Visual Studio Code.

---

## 1. Global Conda Environments

Global environments are created in Conda’s default environment directory and can be reused across multiple projects.

### Create a New Environment

```bash
conda create --name venv_name python=3.12

```

### Activate the Environment

```bash
conda activate venv_name

```

### Install Required Packages

```bash
conda install pyspark
conda install openjdk

```

### Delete a Global Environment

```bash
conda remove --name venv_name --all

```

---

### Clone an Existing Environment

Use this when you want an exact copy of another Conda environment.

```bash
conda create --name new_env --clone original_env

```

---

## 2. Local (Project-Specific) Conda Environments

Local environments are created inside or alongside a project directory, making them easier to manage per project.

### Navigate to the Project Directory

```bash
cd /path/to/your/project

```

### Create a Local Environment

```bash
conda create --prefix venv_name python=3.12

```

### Activate the Local Environment

```bash
conda activate venv_name/

```

---

### Delete a Local Environment

```bash
conda remove --prefix /Users/sampad.kar/Desktop/Code/CONTENT_GENERATION/content_gen_venv --all

```

---

## 3. Setting the Python Interpreter in VS Code

To ensure VS Code uses the correct Conda environment for your project, follow these steps.

### Select Python Interpreter (Workspace-Level)

1. Open the Command Palette:
    - **macOS:** `Cmd + Shift + P`
    - **Windows/Linux:** `Ctrl + Shift + P`
2. Search for:
    
    ```
    Python: Select Interpreter
    
    ```
    
3. Choose the Conda environment you want to use.

---

### Ensure Automatic Environment Activation

Make sure the following setting is enabled so that VS Code automatically activates the selected environment in new terminals:

```json
"python.terminal.activateEnvironment": true

```

---

## Summary

- Use **global environments** for reusable setups across projects.
- Use **local environments** for strict project isolation.
- Always verify the active Python interpreter in VS Code to avoid dependency or runtime mismatches.

This setup ensures consistent development environments and smoother project workflows.

# UV SETUP

Install `uv` using brew.

`brew install uv`

## Setting up a new venv (named .venv) →

```bash
# 1. Create project folder
mkdir my-project
cd my-project

# 2. Initialize uv project with a specific Python version
uv init --python 3.11

# 3. Add dependencies from requirements.txt into pyproject.toml
uv add -r requirements.txt

# 4. Sync the environment
uv sync

# 5. Activate the env
source .venv/bin/activate

# 6. Verify
python --version
which python
```

## Deleting a venv (named .venv) →

Assume this is in the root.

```bash
# 1. Go to your project folder
cd my-project

# 2. Deactivate the venv if it is currently active
deactivate 2>/dev/null || true

# 3. Remove the local project virtual environment
rm -rf .venv

# 4. Optional: remove Python/tooling caches inside the project
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov

# 5. Check uv cache location
uv cache dir

# 6. Safer uv cache cleanup: remove unused cache entries
uv cache prune

# 7. Full uv cache cleanup: remove entire uv cache
uv cache clean
```
