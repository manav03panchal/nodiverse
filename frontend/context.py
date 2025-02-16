import os
import argparse
import logging
import fnmatch


def is_text_file(file_path, blocksize=512):
    """
    Check if a file is a text file.
    """
    try:
        with open(file_path, "rb") as file:
            block = file.read(blocksize)
            if b"\0" in block:
                return False
        return True
    except:
        return False


def copy_directory_contents_to_file(
    source_dir, output_file, ignore_dirs=None, ignore_files=None, log_file=None
):
    """
    Recursively copies all text file contents from source_dir into output_file.
    Each file's content is preceded by its relative path.
    Skips directories and files specified in ignore_dirs and ignore_files.
    Logs skipped files and directories to log_file if provided.
    """
    if ignore_dirs is None:
        ignore_dirs = []
    if ignore_files is None:
        ignore_files = []

    # Set up logging if a log_file is provided
    if log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip ignored directories
            dirs_to_remove = []
            for d in dirs:
                dir_path = os.path.join(root, d)
                if d in ignore_dirs or dir_path in ignore_dirs:
                    dirs_to_remove.append(d)
                    relative_skipped = os.path.relpath(dir_path, source_dir)
                    logging.info(f"Skipped directory: {relative_skipped}")
            for d in dirs_to_remove:
                dirs.remove(d)

            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, source_dir)

                # Check if the file should be ignored
                if should_ignore_file(filename, ignore_files):
                    logging.info(f"Skipped file (ignored): {relative_path}")
                    continue

                if is_text_file(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                        outfile.write(f"\n\n=== File: {relative_path} ===\n\n")
                        outfile.write(content)
                    except Exception as e:
                        logging.info(f"Failed to read {relative_path}: {e}")
                else:
                    logging.info(f"Skipped non-text file: {relative_path}")


def should_ignore_file(filename, ignore_files):
    """
    Determines if a file should be ignored based on exact names or wildcard patterns.
    """
    for pattern in ignore_files:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def read_ignore_dirs(ignore_list, source_dir):
    """
    Processes the ignore list to handle both absolute and relative paths.
    Returns a list of absolute paths to ignore.
    """
    ignore_dirs = []
    for item in ignore_list:
        # If the path is absolute, use it directly
        if os.path.isabs(item):
            ignore_dirs.append(os.path.normpath(item))
        else:
            # Otherwise, consider it relative to the source directory
            ignore_dirs.append(os.path.normpath(os.path.join(source_dir, item)))
    return ignore_dirs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combine directory contents into a single text file, excluding specified directories and files."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="combined_file.txt",
        help="Name of the output file (default: combined_file.txt)",
    )
    parser.add_argument(
        "-id",
        "--ignore-dirs",
        type=str,
        nargs="*",
        default=[".git", "__pycache__", "node_modules"],
        help="List of directory names or paths to ignore (default: .git, __pycache__, node_modules)",
    )
    parser.add_argument(
        "-if",
        "--ignore-files",
        type=str,
        nargs="*",
        default=["*.log", "*.tmp", "README.md"],
        help="List of file names or wildcard patterns to ignore (e.g., *.log, secret.txt)",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="skipped_items.log",
        help="Name of the log file to record skipped files and directories (default: skipped_items.log)",
    )
    args = parser.parse_args()

    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Process ignore directories
    ignore_dirs = read_ignore_dirs(args.ignore_dirs, script_directory)

    # Define the output file path within the script directory
    output_text_file = os.path.join(script_directory, args.output)

    # Define the log file path within the script directory
    log_file = os.path.join(script_directory, args.log)

    # Define ignore files list
    ignore_files = args.ignore_files

    copy_directory_contents_to_file(
        source_dir=script_directory,
        output_file=output_text_file,
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files,
        log_file=log_file,
    )
    print(
        f"All text files in '{script_directory}' have been combined into '{output_text_file}'"
    )
    print(f"Skipped files and directories have been logged to '{log_file}'")
