#!/usr/bin/env python3
"""
GPU Stress Test Script using PyTorch
Tests both GPU compute (matrix operations) and GPU memory bandwidth
"""

import torch
import time
import sys
import argparse
from datetime import datetime


def print_gpu_info():
    """Display GPU information"""
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available. Please ensure PyTorch is installed with CUDA support.")
        sys.exit(1)
    
    print("=" * 70)
    print("GPU Information:")
    print("=" * 70)
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"  Total Memory: {props.total_memory / 1024**3:.2f} GB")
        print(f"  Compute Capability: {props.major}.{props.minor}")
    print("=" * 70)
    print()


def stress_compute(device, matrix_size=8192, iterations=100):
    """
    Stress GPU compute cores with matrix multiplications
    
    Args:
        device: torch device to use
        matrix_size: size of square matrices (larger = more compute)
        iterations: number of matrix multiplications per batch
    """
    # Create large matrices on GPU
    A = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
    B = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
    
    # Perform matrix multiplications
    for _ in range(iterations):
        C = torch.matmul(A, B)
        # Use result to prevent optimization
        A = C
    
    # Ensure all operations complete
    torch.cuda.synchronize()
    return C


def stress_memory(device, memory_size_mb=1024, iterations=50):
    """
    Stress GPU memory bandwidth with copy operations
    
    Args:
        device: torch device to use
        memory_size_mb: size of memory blocks to allocate and copy
        iterations: number of memory operations
    """
    # Calculate tensor size (float32 = 4 bytes)
    tensor_elements = (memory_size_mb * 1024 * 1024) // 4
    
    # Create tensors and perform memory-intensive operations
    for _ in range(iterations):
        # Allocate memory
        tensor_a = torch.randn(tensor_elements, device=device, dtype=torch.float32)
        
        # Memory copy operations
        tensor_b = tensor_a.clone()
        tensor_c = tensor_a + tensor_b
        
        # Memory access patterns
        tensor_d = tensor_c * 2.0
        tensor_e = torch.sqrt(torch.abs(tensor_d))
        
        # Clean up to force re-allocation in next iteration
        del tensor_a, tensor_b, tensor_c, tensor_d, tensor_e
    
    torch.cuda.synchronize()


def mixed_workload(device, matrix_size=4096, memory_mb=512):
    """
    Combined compute and memory stress
    
    Args:
        device: torch device to use
        matrix_size: size of matrices for compute operations
        memory_mb: memory size for memory operations
    """
    # Matrix multiplication (compute heavy)
    A = torch.randn(matrix_size, matrix_size, device=device)
    B = torch.randn(matrix_size, matrix_size, device=device)
    C = torch.matmul(A, B)
    
    # Memory operations
    tensor_elements = (memory_mb * 1024 * 1024) // 4
    mem_tensor = torch.randn(tensor_elements, device=device)
    mem_result = mem_tensor * 2.0 + torch.sin(mem_tensor)
    
    # More compute
    D = torch.matmul(C, C.T)
    
    # Ensure completion
    torch.cuda.synchronize()
    
    return D, mem_result


def run_stress_test(device_id=0, duration_seconds=None, intensity='high'):
    """
    Main stress test loop
    
    Args:
        device_id: GPU device ID to test
        duration_seconds: how long to run (None = indefinite)
        intensity: 'low', 'medium', or 'high'
    """
    device = torch.device(f'cuda:{device_id}')
    
    # Configure intensity
    intensity_configs = {
        'low': {'matrix_size': 2048, 'memory_mb': 256, 'compute_iters': 10, 'memory_iters': 10},
        'medium': {'matrix_size': 4096, 'memory_mb': 512, 'compute_iters': 50, 'memory_iters': 25},
        'high': {'matrix_size': 8192, 'memory_mb': 1024, 'compute_iters': 100, 'memory_iters': 50}
    }
    
    config = intensity_configs.get(intensity, intensity_configs['high'])
    
    print(f"Starting GPU stress test on GPU {device_id}")
    print(f"Intensity: {intensity.upper()}")
    print(f"Matrix size: {config['matrix_size']}x{config['matrix_size']}")
    print(f"Memory operations: {config['memory_mb']} MB")
    print(f"Duration: {'Indefinite (press Ctrl+C to stop)' if duration_seconds is None else f'{duration_seconds} seconds'}")
    print("=" * 70)
    print()
    
    start_time = time.time()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            iter_start = time.time()
            
            # Run compute stress
            stress_compute(device, config['matrix_size'], config['compute_iters'])
            
            # Run memory stress
            stress_memory(device, config['memory_mb'], config['memory_iters'])
            
            # Run mixed workload
            mixed_workload(device, config['matrix_size'] // 2, config['memory_mb'] // 2)
            
            iter_time = time.time() - iter_start
            elapsed = time.time() - start_time
            
            # Get GPU memory usage
            memory_allocated = torch.cuda.memory_allocated(device) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(device) / 1024**3
            
            # Print status
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Iteration: {iteration:4d} | "
                  f"Time: {iter_time:6.2f}s | "
                  f"Elapsed: {elapsed:7.1f}s | "
                  f"GPU Mem: {memory_allocated:.2f}/{memory_reserved:.2f} GB")
            
            # Check if duration limit reached
            if duration_seconds is not None and elapsed >= duration_seconds:
                print(f"\nStress test completed after {elapsed:.1f} seconds ({iteration} iterations)")
                break
                
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\nStress test interrupted after {elapsed:.1f} seconds ({iteration} iterations)")
    
    print("=" * 70)
    print("GPU stress test finished successfully")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='GPU Stress Test - Tests GPU compute cores and memory bandwidth',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run indefinitely on GPU 0 with high intensity
  %(prog)s 0                        # Run on GPU 0 (positional argument)
  %(prog)s 1                        # Run on GPU 1
  %(prog)s 0 --duration 300         # Run GPU 0 for 5 minutes
  %(prog)s 1 --intensity medium     # Run GPU 1 with medium intensity
  %(prog)s --duration 60 --intensity low   # Light test for 1 minute on GPU 0
        """
    )
    
    parser.add_argument('device', type=int, nargs='?', default=0,
                        help='GPU device ID to test (default: 0)')
    parser.add_argument('--duration', type=int, default=None,
                        help='Test duration in seconds (default: run indefinitely)')
    parser.add_argument('--intensity', choices=['low', 'medium', 'high'], default='high',
                        help='Test intensity level (default: high)')
    parser.add_argument('--no-info', action='store_true',
                        help='Skip displaying GPU information')
    
    args = parser.parse_args()
    
    # Display GPU info
    if not args.no_info:
        print_gpu_info()
    
    # Verify device exists
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available!")
        sys.exit(1)
    
    if args.device >= torch.cuda.device_count():
        print(f"ERROR: GPU device {args.device} not found. Available devices: 0-{torch.cuda.device_count()-1}")
        sys.exit(1)
    
    # Run the stress test
    run_stress_test(args.device, args.duration, args.intensity)


if __name__ == "__main__":
    main()

