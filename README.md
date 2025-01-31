BULK GIT INSTALLER:

    Clones each GitHub repository from your list into a user-defined output directory (default: cloned_repos).
    Checks for an install.sh or setup.sh. If found, marks it executable and runs it.
    If no install script is found, checks if it’s a Python-based repository (i.e., has requirements.txt or setup.py); if so, creates and uses a Python venv to install dependencies.

EXAMPLE USAGE: 

    Example usage:
    ./install.sh [output_directory]
    If no output_directory is provided, it defaults to \"cloned_repos\".

PRETTIFY GIT LINKS: 

    LETS YOU TAKE THE GIT URL IN A FILE. IT  THEN APPENDS 'GIT' AND WRAPS THE LINE IN QUOTES "  "
        * Specificy .txt to be cleaned, and txt to write to 
        * ie prettify_git_links.sh dirty_gits.txt 
    RESULT: processed_dirt_gits.txt 

BULK LOCAL INSTALLER:

    ################################################################################
    # This script enumerates subdirectories (up to two levels deep) within a given
    # folder, then:
    #   1) Checks if an install script (install.sh or setup.sh) is present.
    #      - If found, marks it executable and runs it.
    #   2) Otherwise, checks if the subdirectory appears to be Python-based (has
    #      requirements.txt or setup.py). If so, creates a Python virtual environment
    #      and installs dependencies.
    ################################################################################
    

LOGIC:

    Clones each repository if not already present. If present, does a git pull to update.
    Checks if there is an install.sh or setup.sh. If so, it executes that script.
    Otherwise, if the repository looks Python-based (it has a requirements.txt or setup.py), creates and activates a Python virtual environment (in a venv folder) and installs dependencies there.
    Skips installation if neither case (install script nor Python-based) applies.

This helps ensure that each Python-based repository is installed in isolation, preventing dependency conflicts across different tools.
