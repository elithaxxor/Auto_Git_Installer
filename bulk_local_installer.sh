#!/usr/bin/env bash

################################################################################
# This script enumerates subdirectories (up to two levels deep) within a given
# folder, then:
#   1) Checks if an install script (install.sh or setup.sh) is present.
#      - If found, marks it executable and runs it.
#   2) Otherwise, checks if the subdirectory appears to be Python-based (has
#      requirements.txt or setup.py). If so, creates a Python virtual environment
#      and installs dependencies.
################################################################################

set -e  # Exit on first error

################################################################################
# Helper Functions
################################################################################

error_exit() {
    echo "[ERROR]: $1" 1>&2
    exit 1
}

# Detect if the given directory is Python-based.
# Return 0 (true) if 'requirements.txt' or 'setup.py' is found at that path.
is_python_repo() {
    local repo_path="$1"
    if [[ -f "$repo_path/requirements.txt" || -f "$repo_path/setup.py" ]]; then
        return 0  # True
    else
        return 1  # False
    fi
}

# Check if there's an install script in the directory (install.sh or setup.sh)
has_install_script() {
    local repo_path="$1"
    if [[ -f "$repo_path/install.sh" || -f "$repo_path/setup.sh" ]]; then
        return 0  # True
    else
        return 1  # False
    fi
}

################################################################################
# Main logic: Enumerate directories and run installation tasks.
################################################################################

install_tools_in_folder() {
    # We sanitize the argument to remove any leading/trailing quotes.
    local raw_dir="$1"
    local sanitized_dir
    sanitized_dir="$(sed -E 's/^\"+|\"+$//g' <<< "$raw_dir")"

    # If no argument was supplied, or the sanitized argument is empty, error out.
    if [[ -z "$sanitized_dir" ]]; then
        error_exit "No target folder was provided. Usage: ./install.sh <target_folder>"
    fi

    if [[ ! -d "$sanitized_dir" ]]; then
        error_exit "The path '$sanitized_dir' does not exist or is not a directory."
    fi

    echo "[INFO]: Searching subdirectories (2 levels deep) in: $sanitized_dir"

    # We find all subdirectories from 1 to 2 levels below $sanitized_dir.
    # -mindepth 1 = ignore $sanitized_dir itself
    # -maxdepth 2 = search only 2 levels deep
    mapfile -t folders < <(find "$sanitized_dir" -mindepth 1 -maxdepth 2 -type d)

    if [[ ${#folders[@]} -eq 0 ]]; then
        echo "[INFO]: No subdirectories found within 2 levels of '$sanitized_dir'."
        return 0
    fi

    for dir in "${folders[@]}"; do
        # Skip the folder if it is the same as $sanitized_dir or does not exist
        if [[ "$dir" == "$sanitized_dir" ]]; then
            continue
        fi

        local name
        name="$(basename "$dir")"
        echo "========================================================="
        echo "[INFO]: Checking directory: $dir (name: $name)"
        echo "========================================================="

        # Check for install script
        if has_install_script "$dir"; then
            echo "[INFO]: Found an installation script in $dir."
            # Mark them executable quietly (in case no file matches, no error)
            chmod +x "$dir"/*install*.sh "$dir"/*setup*.sh 2>/dev/null || true

            # Attempt to run each found script
            for script in "$dir"/install.sh "$dir"/setup.sh; do
                if [[ -f "$script" ]]; then
                    echo "[INFO]: Running script: $script"
                    (
                        cd "$dir"
                        bash "$script" || echo "[WARNING]: Could not run the installation script for $dir."
                    )
                fi
            done
        # Otherwise, check if Python-based
        elif is_python_repo "$dir"; then
            echo "[INFO]: Detected Python-based directory: $dir"
            (
                cd "$dir" || exit 1
                python3 -m venv venv
                source venv/bin/activate
                if [[ -f "requirements.txt" ]]; then
                    echo "[INFO]: Installing from requirements.txt..."
                    pip install --upgrade pip
                    pip install -r requirements.txt
                elif [[ -f "setup.py" ]]; then
                    echo "[INFO]: Running setup.py install..."
                    pip install --upgrade pip
                    python setup.py install
                fi
                deactivate
            )
        else
            echo "[INFO]: Not Python-based and no install script found. Skipping."
        fi
    done

    echo "[INFO]: Finished enumerating and processing subdirectories."
}

################################################################################
# Script Entry Point
################################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_tools_in_folder "$1"
fi
