Here is the complete .sh script that:

    Clones each GitHub repository from your list into a user-defined output directory (default: cloned_repos).
    Checks for an install.sh or setup.sh. If found, marks it executable and runs it.
    If no install script is found, checks if it’s a Python-based repository (i.e., has requirements.txt or setup.py); if so, creates and uses a Python venv to install dependencies.

EXAMPLE USAGE: 

    Example usage:
    ./install.sh [output_directory]
    If no output_directory is provided, it defaults to \"cloned_repos\".

LOGIC:

    Clones each repository if not already present. If present, does a git pull to update.
    Checks if there is an install.sh or setup.sh. If so, it executes that script.
    Otherwise, if the repository looks Python-based (it has a requirements.txt or setup.py), creates and activates a Python virtual environment (in a venv folder) and installs dependencies there.
    Skips installation if neither case (install script nor Python-based) applies.

This helps ensure that each Python-based repository is installed in isolation, preventing dependency conflicts across different tools.
