import os
import json
import re
import httpx
import random
import concurrent.futures
from tqdm import tqdm
from openai import OpenAI
import argparse 
from dotenv import load_dotenv

load_dotenv()

# Set API Key
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

task_describe = """
You are an expert in software engineering.
"""

information = """
Please help me generate similar data based on the format provided below.
"""

format_instructions = """
Ensure that the data you provide is consistent with the reference data format, and that all test cases included in the data are correct.
Ensure that the generated data is different from the provided reference data.
Return the data in the same Json format as the reference data and wrapped the data with [Start] and [End].
"""

def load_jsonl(file_path):
    """Load data from a jsonl file."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def GEN_ANSWER(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": task_describe},
            {"role": "user", "content": information + prompt + format_instructions}
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content, response.usage.total_tokens

def extract_wrapped_content(text):
    match = re.search(r'\[Start\]\s*\n(.*?)\n\[End\]', text, re.DOTALL)
    if not match:
        return None
    content = match.group(1).strip()

    task_id_match = re.search(r'"task_id"\s*:\s*"([^"]+)"', content)
    task_id = task_id_match.group(1) if task_id_match else None

    prompt_match = re.search(r'"prompt"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
    prompt = prompt_match.group(1).replace('\n', '\\n') if prompt_match else None

    entry_point_match = re.search(r'"entry_point"\s*:\s*"([^"]+)"', content)
    entry_point = entry_point_match.group(1) if entry_point_match else None

    canonical_solution_match = re.search(r'"canonical_solution"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
    canonical_solution = canonical_solution_match.group(1).replace('\n', '\\n') if canonical_solution_match else None

    test_match = re.search(r'"test"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
    test = test_match.group(1).replace('\n', '\\n') if test_match else None

    if task_id and prompt and entry_point and canonical_solution and test:
        extracted_data = {
            "task_id": task_id,
            "prompt": prompt,
            "entry_point": entry_point,
            "canonical_solution": canonical_solution,
            "test": test
        }
        return extracted_data
    return None

def process_task(task_id, prompt):
    total_tokens = 0
    while True:
        completion, tokens_used = GEN_ANSWER(prompt)
        total_tokens += tokens_used
        json_content = extract_wrapped_content(completion)
        if json_content:
            return json_content, total_tokens
        else:
            print(f"No valid Json data found for task {task_id}. Retrying...")

def main(output_path, prompt_file):
    # Load prompts from jsonl file
    try:
        all_prompts = load_jsonl(prompt_file)
    except Exception as e:
        raise ValueError(f"Error loading prompts from {prompt_file}: {e}")

    if len(all_prompts) < 3:
        raise ValueError("The jsonl file must contain at least 3 prompts.")

    # Randomly select 3 to 5 prompts
    num_samples = random.randint(3, 5)
    num_samples = min(num_samples, len(all_prompts))
    selected_prompts = random.sample(all_prompts, num_samples)

    # Format the selected prompts into a template string
    prompt_template = '\n'.join(json.dumps(p) for p in selected_prompts)

    samples = []
    total_tokens_used = 0
    problems = {i: {"prompt": prompt_template} for i in range(10)}  # Create 10 tasks

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_task, task_id, problem["prompt"]) for task_id, problem in problems.items()]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing tasks"):
            result, tokens_used = future.result()
            if result:
                samples.append(result)
                total_tokens_used += tokens_used

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir) and output_dir:
        os.makedirs(output_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')

    print(f"Total tokens used: {total_tokens_used}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data and save it to a specified output path.")
    parser.add_argument('--output_path', type=str, required=True, help="The output path for the generated data.")
    parser.add_argument('--prompt_file', type=str, required=True, help="Path to the jsonl file containing prompt templates.")
    args = parser.parse_args()

    main(args.output_path, args.prompt_file)
