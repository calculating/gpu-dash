#!/bin/bash

HOSTNAME=$(hostname)

# Get GPU data using nvidia-smi
GPU_DATA=$(nvidia-smi --query-gpu=index,power.draw,memory.used --format=csv,noheader,nounits)

# Function to post data to Flask server
post_data() {
    GPU_ID="$1"
    GPU_WATTS="$2"
    GPU_MEM="$3"

    # Send data to the Flask server
    curl -X POST https://nel.ag/api/log \
        -H "Content-Type: application/json" \
        -d "{\"gpu_id\": \"$GPU_ID\", \"gpu_watts\": $GPU_WATTS, \"gpu_mem\": $GPU_MEM}"
}

# Read each line of GPU data
echo "$GPU_DATA" | while IFS=',' read -r INDEX GPU_WATTS GPU_MEM; do
    GPU_ID="${HOSTNAME}_gpu${INDEX}"

    # Handle missing data
    if [ -z "$GPU_WATTS" ]; then
        GPU_WATTS=null
    fi

    if [ -z "$GPU_MEM" ]; then
        GPU_MEM=null
    fi

    post_data "$GPU_ID" "$GPU_WATTS" "$GPU_MEM"
done
