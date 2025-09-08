import os
import re


def rename_files_in_context_directory(directory):
    for filename in os.listdir(directory):
        # Process .txt files
        if filename.endswith(".txt"):
            old_path = os.path.join(directory, filename)

            # Convert to lowercase
            new_filename = filename.lower()

            # Replace spaces and multiple hyphens/underscores with single hyphens
            new_filename = re.sub(r"[\s\-_]+", "-", new_filename)

            # Remove special characters (keep alphanumeric, hyphens, and dots for extension)
            new_filename = re.sub(r"[^a-z0-9\-.]", "", new_filename)

            # Ensure it ends with its original extension
            original_extension = os.path.splitext(filename)[1].lower()
            if not new_filename.endswith(original_extension):
                new_filename = os.path.splitext(new_filename)[0] + original_extension

            new_path = os.path.join(directory, new_filename)

            # Avoid renaming if the new name is the same as the old name
            if old_path != new_path:
                print(f"Renaming '{filename}' to '{new_filename}'")
                os.rename(old_path, new_path)
            else:
                print(f"'{filename}' already in desired format.")


if __name__ == "__main__":
    context_dir = "C:\\Users\\craig\\DevAgentZero.V2\\context"
    rename_files_in_context_directory(context_dir)
