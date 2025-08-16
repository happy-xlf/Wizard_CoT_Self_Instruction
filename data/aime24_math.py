import os
from datasets import load_dataset
import json

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

dataset = load_dataset("Maxwell-Jia/AIME_2024")

save_path = "./aime24_math.jsonl"

problem_list = []
solution_list = []
answer_list = []

for problem in dataset["train"]:
    problem_list.append(problem["Problem"])
    solution_list.append(problem["Solution"])
    answer_list.append(problem["Answer"])

with open(save_path, "w") as f:
    for problem, solution, answer in zip(problem_list, solution_list, answer_list):
        f.write(json.dumps({"problem": problem, "solution": solution, "answer": answer}) + "\n")