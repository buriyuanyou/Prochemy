# 📚 Prochemy

This is the official implementation of the paper Prompt Alchemy: Automatic Iterative Prompt Refinement for Code
Generation

## 🚀 Quick Start

### ⚙️ Preparation

1. **Environmental** settings: `pip install -r requirements.txt`
3. **OpenAI API key** required: add your OpenAI API key, base url and other related settings in the `.env` file. You can also customize these two parameters to use the DeepSeek Model.



### 💻 Code Generation

#### 0. Automatically Generate Training Set

​    Use the following instructions to automatically generate training dataset using a large language model, as described in Section 2.2 of the paper.  `--output_path` parameter is used to specify the file output path.

```python
python 0_train_set_generate.py --output_path ./train_set_gpt3.5turbo.jsonl
```

​    Run the `train_set_postprocessing.py` script in the `code_generation/utils` directory to post-process the generated results.

```python
python train_set_postprocessing --file_path=../train_set_gpt3.5turbo.jsonl
```

​    The format of the processed training dataset may appear as follows:

```json
{"task_id": "auto/0", "prompt": "from typing AIRCodert List\n\n\ndef custom_merge_lists(list1: List[int], list2: List[int]) -> List[int]:\n    ", "entry_point": "custom_merge_lists", "canonical_solution": "    merged_list = []\n    len1, len2 = len(list1), len(list2)\n    max_len = max(len1, len2)\n\n    for i in range(max_len):\n        if i < len1:\n            merged_list.append(list1[i])\n        if i < len2:\n            merged_list.append(list2[i])\n\n    return merged_list\n", "test": "\n\nMETADATA = {\n    'author': 'assistant',\n    'dataset': 'generated'\n}\n\n\ndef check(candidate):\n    assert candidate([1, 2, 3, 4], [5, 6, 7]) == [1, 5, 2, 6, 3, 7, 4]\n    assert candidate([1, 2, 3], [4, 5, 6, 7]) == [1, 4, 2, 5, 3, 6, 7]\n    assert candidate([1, 2], [4, 5, 6, 7]) == [1, 4, 2, 5, 6, 7]\n"}
{"task_id": "auto/1", "prompt": "from typing AIRCodert List\n\n\ndef find_max_subarray_sum(nums: List[int]) -> int:\n    ", "entry_point": "find_max_subarray_sum", "canonical_solution": "    max_sum = current_sum = nums[0]\n\n    for num in nums[1:]:\n        current_sum = max(num, current_sum + num)\n        max_sum = max(max_sum, current_sum)\n\n    return max_sum\n", "test": "\n\nMETADATA = {\n    'author': 'assistant',\n    'dataset': 'test'\n}\n\n\ndef check(candidate):\n    assert candidate([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6\n    assert candidate([1, 2, 3, -2, 5]) == 9\n    assert candidate([-2, -3, 4, -1, -2, 1, 5, -3]) == 7\n    assert candidate([1, -2, 3, -1, 2, -3, 4]) == 6\n    assert candidate([1, -2, -3, 1, 3, -1, 2, -3, 4]) == 5\n    assert candidate([-1, -2, -3, -4, -5]) == -1\n\n"}
```

​    

​    The following instructions are used to randomly extract data from existing datasets:

```
python 0_train_set_select.py --input /path/to/input.jsonl --output /path/to/output.jsonl --sample_size 10
```

​    The `--input` parameter specifies the input file path, the `--output` parameter specifies the output file path, and the `--sample_size` parameter represents the number of data samples to be extracted.



#### 1. Prompt Mutation.

​    Use the following instructions to mutate the prompt. As described in Section 2.3 of the paper.

```
python 1_prompt_mutate.py --model gpt-3.5-turbo --prompt_path ./origin_prompt.jsonl --output_path ./data/mutated_prompt/gpt3.5turbo_epoch0.jsonl
```

​    The `--model` parameter specifies the type of model to be used. If you need to use a DeepSeek series model, simply modify the `base_url` and `API_key` in `.env` to the properties provided by DeepSeek. After that, you can still use `--model` to specify the model version. The `prompt_path` attribute represents the file path where the original prompts to be mutated are stored, while `output_path` specifies the location where the mutated prompts will be saved.

​    The format of the mutated prompt is as follows:

```json
{"prompt_id": 3, "mutated_prompt": "You are a code generation assistant tasked with creating a Python program based on natural language descriptions. The goal of the program is to successfully complete the tasks described in the natural language instructions and pass any test cases specific to those tasks.\n\nYour role is to generate Python code that accurately implements the desired functionality. In order to do this, you should carefully analyze the given task description and design a program that meets all the requirements.\n\nTo optimize the task's effectiveness, please ensure that your generated Python code includes the following:\n\n1. Detailed Task Description: Clearly define the task that needs to be accomplished. This ensures that the code you generate accurately addresses the desired functionality.\n\n2. Inputs and Outputs: Specify the inputs required for the program and the expected outputs. This helps in designing a solution that fulfills the expected requirements.\n\n3. Test Cases: Include specific test cases that the program should pass. These cases will be used to validate the correctness of the generated code.\n\n4. Code Structure and Guidance: Provide an outline or pseudo-code of the program's structure to guide the code generation process. This helps in organizing the code and ensures that it is easy to understand and follow.\n\nBy incorporating these elements into your generated Python code, you will create a more helpful and harmless response that accurately meets the requirements mentioned in the given task description."}
```



#### 2. Prompt Evaluation.

​    Evaluate the obtained mutated prompts and generate the test set code execution results corresponding to each prompt.

```
python 2_prompt_evaluate.py --model gpt-3.5-turbo --trainset_path ./train_set_gpt3.5turbo.jsonl --mutated_prompt_path ./data/mutated_prompt/gpt3.5turbo_epoch0.jsonl --output_path ./data/prompt_evaluate/gpt3.5turbo_test
```

​    The `--trainset_path` parameter is used to specify the path of the training dataset file, the `--mutated_prompt` attribute specifies the path of the file containing the set of prompts to be evaluated, and `--output_path` is used to designate the path where the generated code execution results will be saved.



#### 3. Prompt Update.

​    Evaluate the performance of each prompt, select the best-performing prompts from this round of generated data, and save them as reference data for the next round of prompt mutation.

```
python 3_reinforcement_cal_score_and_select.py --evaluate_path ./data/prompt_evaluate/gpt3.5turbo_test --testset_path ./train_set_gpt3.5turbo.jsonl --origin_prompt ./data/mutated_prompt/gpt3.5turbo_epoch0.jsonl --best_prompt ./data/mutated_prompt/best_prompt_gpt3.5turbo_epoch0.jsonl
```

​    The `--evaluate_path` parameter represents the path where the code files corresponding to the prompts from the previous round are saved. The `--origin_prompt` and `--best_prompt` parameters represent the original set of prompts and the updated best prompts.

​    An example result is as follows:

```
Best prompts saved to ./data/mutated_prompt/best_prompt_gpt3.5turbo_epoch0.jsonl with prompt_ids: [8] and max weighted score: 56.68333333333333
```

​    This represents the prompt that performed best on the test set in this round and will serve as the reference prompt for the next mutation. The corresponding code from step 1 can be used to directly utilize the resulting file for the next round of mutations.



​    You can also modify the corresponding attributes in the `2+3+4_reinforcement.py` file based on the attribute values mentioned above, to complete the iterative steps 1-3 in one process. This continues until the convergence condition is met, i.e., the peak performance of the prompts on the training set remains unchanged in two consecutive prompt evaluation processes.



#### 4. Evaluation

​    Modify the file path of the test set, prompt, and output file path attributes in the `prompt_test_humaneval_ET.py` file to test the performance of different prompts on the HumanEval, MBPP datasets, and their enhanced versions. The processed datasets are stored in the `./Dataset` directory.

​    Use the `./post_processing.py` file to post-process the results returned by the model in order to extract the longest compilable Python code from the responses. Alternatively, you can use `./post_processing_modified.py` to directly extract Python code blocks wrapped in `python`. Then, use the following command:

```
evaluate_functional_correctness ./path_to_sanitized_result_file --problem_file=./corresponding_testset
```

​    to evaluate the pass@1 value for the generated code result files.



### 💻 Code Translation

​    The process of mutating and updating prompts is similar to the one in the `code_generation` module. You only need to modify the corresponding attributes in the `Java2Python` and `Python2Java` folders. The meaning of each attribute is explained in the code files.

​    After obtaining the `best_prompt` file, modify the `task_describe` attribute in the `evaluate_prompt_java2python.py` file to the value of the obtained `best_prompt`. This will generate the code results corresponding to the prompt.

​    Once you modify the file paths in `run_python_testcases_avatar.py` accordingly, use the following command:

```
python run_python_testcases_avatar.py
```

​    This will generate the pass@1 value for the code translation task, as well as the ratio of passed test cases to the total number of test cases. The same applies to the python2java  translation using   `evaluate_prompt_python2java.py` and `run_java_testcases_avatar.py` .
