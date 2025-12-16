import json
import re
import argparse


# Function to clean escape characters
def clean_escape_characters(text):
    # Replace all double backslashes with single backslash
    text = text.replace('\\\\', '\\')
    # Remove any unnecessary escape sequences
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', '\t')
    # Handle escaped quotes properly
    text = text.replace('\\"', '"')
    return text


# Function to process the file
def process_file(file_path):
    # Read the JSONL file and load each line as a JSON object
    with open(file_path, 'r') as file:
        data = [json.loads(line) for line in file]

    # Modify each entry
    for i, entry in enumerate(data):
        # Update task_id
        entry['task_id'] = f"auto/{i}"

        # Clean the 'prompt', 'canonical_solution', and 'test' fields
        if 'prompt' in entry:
            entry['prompt'] = clean_escape_characters(entry['prompt'])
        if 'canonical_solution' in entry:
            entry['canonical_solution'] = clean_escape_characters(entry['canonical_solution'])
        if 'test' in entry:
            entry['test'] = clean_escape_characters(entry['test'])

    # Write the modified data back to the JSONL file
    with open(file_path, 'w') as file:
        for entry in data:
            # Write each entry back with the appropriate formatting
            file.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"File {file_path} has been successfully updated with cleaned entries and new task IDs.")


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process and clean a JSONL file with task data.")
    parser.add_argument('--file_path', type=str, required=True, help="The file path for the JSONL file to process.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the processing function with the provided file path
    process_file(args.file_path)