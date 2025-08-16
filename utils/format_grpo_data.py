import pandas as pd
import json

def format_grpo_data(data_path):
    new_data = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            question = data["question"]
            answer = data["answer"]

            dt = {
                "data_source": "grpo_mix_math",
                "question": question,
                "ability": "math",
                "reward_model": {
                    "ground_truth": answer,
                    "style": "rule"
                },
                "extra_info": {
                    "index": None,
                    "source": "xxx"
                },
                "system_prompt": "You are a helpful assistant that can solve the given question step by step with the help of the search tool and python interpreter tool.\nGiven a question, you need to first think about the reasoning process in the mind and then provide the answer.\nDuring thinking, you can invoke the search tool to search and python interpreter tool to calculate the math problem for fact information about specific topics if needed.\nThe reasoning process is enclosed within <think> </think>, and the answer is after </think>,\nand the search query and result are enclosed within <search> </search> and <result> </result> tags respectively.\nFor example, <think> This is the reasoning process. </think> <search> search query here </search> <result> search result here </result>\n<think> This is the reasoning process. </think> <python> python code here </python> <result> python interpreter result here </result>\n<think> This is the reasoning process. </think> The final answer is \\[ \\boxed{answer here} \\]\nIn the last part of the answer, the final exact answer is enclosed within \\boxed{} with latex format."
            }
            new_data.append(dt)
    # 转为parquet,其中随机抽选50道题为测试集，其余为训练集
    df = pd.DataFrame(new_data)
    df = df.sample(frac=1).reset_index(drop=True)
    df_train = df.iloc[:-50]
    df_test = df.iloc[-50:]
    df_train.to_parquet("../data/aime24_math_llm_cot_train.parquet")
    df_test.to_parquet("../data/aime24_math_llm_cot_test.parquet")

if __name__ == "__main__":
    format_grpo_data("../data/aime24_math_llm_cot.jsonl")