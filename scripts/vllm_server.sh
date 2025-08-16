vllm serve /data02/home/zdhs0092/Models/Qwen3-30B-A3B-Thinking-2507 \
    --served-model-name qwen3-30b-a3b-thinking-2507 \
    --host 0.0.0.0 \
    --port 8999 \
    --max-model-len 262144 \
    --enable-reasoning \
    --reasoning-parser deepseek_r1 \
    --trust-remote-code \
    --tensor-parallel-size 8 \
    --gpu-memory-utilization 0.8