import json
import random
import argparse


# Function to handle the logic of randomly sampling data
def sample_jsonl(input_path, output_path, sample_size=10):
    # Read all lines from the jsonl file
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Randomly select the specified number of lines, default is 10
    sampled_lines = random.sample(lines, sample_size)

    # Write the randomly selected lines to a new file
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in sampled_lines:
            f.write(line)

    print(f"Randomly selected {sample_size} lines have been saved to {output_path}.")


# Set up argparse to parse command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Randomly sample data from a jsonl file and save to a new file")

    # Add input and output file path arguments
    parser.add_argument('--input', type=str, required=True, help="Path to the input jsonl file")
    parser.add_argument('--output', type=str, required=True, help="Path to the output file")
    parser.add_argument('--sample_size', type=int, default=10, help="Number of random samples to select, default is 10")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function to execute the sampling logic
    sample_jsonl(args.input, args.output, args.sample_size)


if __name__ == "__main__":
    main()