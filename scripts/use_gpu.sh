#!/bin/bash
#SBATCH -A wenge
#SBATCH --partition=wenge
#SBATCH --nodes=1
#SBATCH --chdir=./job_log
#SBATCH --gres=gpu:8
#SBATCH --exclude=gpunode46,gpunode47,gpunode62,gpunode15,gpunode16,gpunode17

# 获取第一个节点的IP
ALL_NODES=$(scontrol show hostnames "$SLURM_NODELIST")
FIRST_NODE=$(echo "$ALL_NODES" | head -n 1)
NODE_0_ADDR=$(getent hosts "$FIRST_NODE" | awk '{print $1}')

export SWANLAB_API_KEY=97gnZlgMCxPf5NqEPAqPL

echo "ALL_NODES"
echo $ALL_NODES

echo "FIRST_NODE"
echo $FIRST_NODE

echo "FIRST_NODE"
echo $NODE_0_ADDR

train_grpo="sleep inf"
# 运行脚本
srun bash -c "$train_grpo"
# 任务结束时的通知 (可选)
echo "Serving job completed at $(date)"