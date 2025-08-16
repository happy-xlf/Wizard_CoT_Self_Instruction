import json
from openai import OpenAI
import sys
import os
# Add the parent directory to the path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt.system_prompt import system_with_cot_plan_instruction, system_with_cot_answer
from utils.check_box import last_boxed_only_string, remove_boxed
import re
from typing import List
from tqdm import tqdm
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 线程锁，用于文件写入
file_lock = threading.Lock()

client = OpenAI(
    base_url="http://gpunode19:8999/v1",
    api_key="key", # 随便填写，只是为了通过接口参数校验
)

def process_single_request(seed_tasks_sample, save_path):
    """处理单个请求的函数"""
    prompt_template = system_with_cot_answer.replace("{seed_questions}", "\n".join([f"Seed Question {i+1}: {task}" for i, task in enumerate(seed_tasks_sample)]))
    
    try:
        response = client.chat.completions.create(
            model="qwen3-30b-a3b-thinking-2507",
            messages=[{"role": "user", "content": prompt_template}]
        )
        content = response.choices[0].message.content

        # 解析输出
        question = re.search(r"\[New Question Begin\](.*?)\[New Question End\]", content, re.DOTALL).group(1).strip()
        reasoning_steps = re.search(r"\[Reasoning Steps Begin\](.*?)\[Reasoning Steps End\]", content, re.DOTALL).group(1).strip()
        answer = re.search(r"\[Final Answer to New Question Begin\](.*?)\[Final Answer to New Question End\]", content, re.DOTALL).group(1).strip()
        if "\\boxed{" in answer:
            answer = remove_boxed(last_boxed_only_string(answer))
    
        dt = {
            "question": question,
            "answer": answer,
            "solution": reasoning_steps
        }
        
        # 线程安全地写入文件
        with file_lock:
            with open(save_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(dt, ensure_ascii=False) + "\n")
        
        return True
    except Exception as e:
        print(f"请求处理失败: {e}")
        return False

# 生成可验证推理任务
def generate_reasoning_task(seed_tasks: List[str], num_new=10, save_path: str = None, max_workers=4):
    """
    使用多线程生成推理任务
    
    Args:
        seed_tasks: 种子任务列表
        num_new: 要生成的新任务数量
        save_path: 保存路径
        max_workers: 最大线程数
    """
    # 准备任务列表
    tasks = []
    for _ in range(num_new):
        # 从seed_tasks中随机选择5个任务
        seed_tasks_sample = random.sample(seed_tasks, 5)
        tasks.append((seed_tasks_sample, save_path))
    
    # 使用线程池执行任务
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {executor.submit(process_single_request, seed_tasks_sample, save_path): i 
                         for i, (seed_tasks_sample, save_path) in enumerate(tasks)}
        
        # 使用tqdm显示进度
        with tqdm(total=num_new, desc="Generating reasoning tasks") as pbar:
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    success = future.result()
                    if success:
                        pbar.update(1)
                    else:
                        print(f"任务 {task_id} 失败")
                except Exception as e:
                    print(f"任务 {task_id} 执行异常: {e}")

# 生成非可验证指令任务
def generate_instruction_task(seed_tasks: List[str]) -> str:
    prompt_template = system_with_cot_plan_instruction.replace("{INSTRUCTION 1}", seed_tasks[0]).replace("{INSTRUCTION 2}", seed_tasks[1])
    
    response = client.chat.completions.create(
        model="qwen3-30b-a3b-thinking-2507",
        messages=[{"role": "user", "content": prompt_template}]
    )
    return response.choices[0].message.content

def seed_question_from_file(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip())["problem"] for line in f.readlines()]


def seed_question_from_file_with_cot(file_path: str) -> dict:
    tags_list = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            dt = json.loads(line.strip())
            question = dt["question"].split("问题：")[1].split("\n领域：")[0].strip()
            if dt["parent_tag"] not in tags_list:
                tags_list[dt["parent_tag"]] = []
            tags_list[dt["parent_tag"]].append(question)
    return tags_list


if __name__ == "__main__":
    # seed_tasks = seed_question_from_file("./data/aime24_math.jsonl")
    # # 使用多线程生成任务，设置4个线程
    # generate_reasoning_task(seed_tasks, num_new=450, save_path="./data/aime24_math_llm_cot.jsonl", max_workers=32)


    # 生成非可验证指令任务
    file_path= "/data02/home/zdhs0092/Code/s1_yayi_data_analyse/code/second_tag_s1_agent_new.jsonl"
    seed_tasks = seed_question_from_file_with_cot(file_path)
    for parent_tag, questions in seed_tasks.items():
        for question in questions:
            question_1 = random.choice(questions)
            question_2 = random.choice(questions)
            while question_1 == question_2:
                question_2 = random.choice(questions)
            prompt_template = system_with_cot_plan_instruction.replace("{INSTRUCTION 1}", question_1).replace("{INSTRUCTION 2}", question_2)
        print(prompt_template)
        print("-"*100)
        response = client.chat.completions.create(
            model="qwen3-30b-a3b-thinking-2507",
            messages=[{"role": "user", "content": prompt_template}]
        )
        print(response.choices[0].message.content)
        print("-"*100)