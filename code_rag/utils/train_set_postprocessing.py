import json
import argparse


def clean_text(obj):
    if isinstance(obj, str):
        return (
            obj.replace('\\\\', '\\')
               .replace('\\n', '\n')
               .replace('\\t', '\t')
               .replace('\\"', '"')
        )
    elif isinstance(obj, list):
        return [clean_text(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_text(v) for k, v in obj.items()}
    else:
        return obj


def process_file(file_path, output_path):
    # Robust read (mixed encodings)
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        data = [json.loads(line) for line in f]

    for i, entry in enumerate(data):
        entry['task_id'] = f"auto/{i}"

        if 'prompt' in entry:
            entry['prompt'] = clean_text(entry['prompt'])

        if 'right_context' in entry:
            entry['right_context'] = clean_text(entry['right_context'])

        if 'groundtruth' in entry:
            entry['groundtruth'] = clean_text(entry['groundtruth'])

        if 'crossfile_context' in entry:
            entry['crossfile_context'] = clean_text(entry['crossfile_context'])

        # metadata intentionally untouched

    # Write to NEW file (safe)
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"Cleaned file written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str, required=True)
    parser.add_argument('--output_path', type=str, required=True)
    args = parser.parse_args()

    process_file(args.file_path, args.output_path)
