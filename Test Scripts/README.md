# GPU Stress Test Scripts

## GPU Stress Test (`gpu_stress_test.py`)

A PyTorch-based GPU stress testing script that thoroughly tests both GPU compute cores and memory bandwidth.

### Requirements

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Or for ROCm (AMD GPUs):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### Features

- **Compute Stress**: Large matrix multiplications to max out GPU cores
- **Memory Stress**: Memory allocation, copying, and bandwidth-intensive operations  
- **Mixed Workload**: Combined compute and memory operations
- **Real-time Monitoring**: Shows iteration time, elapsed time, and GPU memory usage
- **Configurable Intensity**: Low, medium, or high stress levels
- **Flexible Duration**: Run indefinitely or for a specific time period

### Usage

**Basic usage (run indefinitely on GPU 0 with high intensity):**
```bash
python gpu_stress_test.py
```

**Test specific GPU (positional argument):**
```bash
python gpu_stress_test.py 0    # Test GPU 0
python gpu_stress_test.py 1    # Test GPU 1
python gpu_stress_test.py 2    # Test GPU 2
```

**Run GPU 0 for 5 minutes:**
```bash
python gpu_stress_test.py 0 --duration 300
```

**Test GPU 1 with medium intensity:**
```bash
python gpu_stress_test.py 1 --intensity medium
```

**Light 1-minute test on GPU 0:**
```bash
python gpu_stress_test.py 0 --duration 60 --intensity low
```

**Stop anytime with `Ctrl+C`**

### Intensity Levels

| Level  | Matrix Size | Memory Size | Description |
|--------|-------------|-------------|-------------|
| Low    | 2048×2048   | 256 MB      | Light load for basic testing |
| Medium | 4096×4096   | 512 MB      | Moderate load for sustained testing |
| High   | 8192×8192   | 1024 MB     | Maximum load for stress testing |

### What It Tests

1. **Matrix Multiplications**: Stresses GPU compute cores with large GEMM operations
2. **Memory Allocations**: Tests memory allocation/deallocation speed
3. **Memory Copies**: Tests GPU memory bandwidth with clone operations
4. **Element-wise Operations**: Tests memory throughput with arithmetic operations
5. **Mixed Workloads**: Combines compute and memory operations simultaneously

### Monitoring GPU During Test

While the script runs, you can monitor your GPU with:

**For AMD GPUs (using LACT):**
```bash
lact cli info
```

**For NVIDIA GPUs:**
```bash
watch -n 1 nvidia-smi
```

**For AMD GPUs (using rocm-smi):**
```bash
watch -n 1 rocm-smi
```

### Expected Behavior

When running properly, you should see:
- GPU utilization at or near 100%
- GPU memory utilization high (depending on your GPU memory size)
- GPU clocks boosting to maximum frequencies
- GPU temperature increasing (ensure adequate cooling!)
- Power draw near TDP limits

### Safety Notes

⚠️ **Warning**: This script will push your GPU to maximum load!

- Ensure adequate cooling (fans/airflow)
- Monitor temperatures (should stay below thermal limits)
- Start with lower intensity if unsure
- Stop immediately if you notice artifacts or crashes

### Troubleshooting

**"CUDA is not available" error:**
- Install PyTorch with CUDA/ROCm support (see Requirements above)
- Verify your GPU drivers are installed correctly

**Out of memory error:**
- Use lower intensity: `--intensity low`
- Test a different GPU if you have multiple: `--device 1`

**Performance lower than expected:**
- Check if GPU is thermal throttling
- Verify GPU clocks are boosting properly with LACT or monitoring tools
- Ensure power limits are set appropriately

