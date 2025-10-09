#!/usr/bin/env python
# $ uv venv ./venv --python 3.13 --python-preference=only-managed
# $ source ./venv/bin/activate
# $ uv pip install -r nvidia-ml-py
# https://github.com/ilya-zlobintsev/LACT/issues/486#issuecomment-3313801198

import argparse
import csv
import time
import signal
import sys
from datetime import datetime
from collections import defaultdict
from pynvml import *

class GPULogger:
    def __init__(self, gpu_indices, output_file):
        self.gpu_indices = gpu_indices
        self.output_file = output_file
        self.running = True
        self.data = []
        self.fieldnames = ['timestamp']

        # Setup signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C interrupt"""
        print("\nReceived interrupt signal, shutting down...")
        self.running = False

    def get_gpu_metrics(self, handle):
        """Get all available GPU metrics for a single GPU"""
        metrics = {}

        try:
            # Power usage
            power = nvmlDeviceGetPowerUsage(handle)
            metrics['power_usage_w'] = power / 1000.0  # Convert to watts

            # Power management - cap limit
            power_management = nvmlDeviceGetPowerManagementLimit(handle)
            power_cap = nvmlDeviceGetEnforcedPowerLimit(handle)
            metrics['power_cap_w'] = power_cap / 1000.0  # Convert to watts

            # Performance State
            performance_state = nvmlDeviceGetPerformanceState(handle)
            metrics['pstate'] = performance_state
            print(performance_state)

            # # Throttle Reason
            # # https://docs.nvidia.com/deploy/nvml-api/group__nvmlClocksEventReasons.html#group__nvmlClocksEventReasons
            # throttle_reason = nvmlDeviceGetSupportedClocksEventReasons(handle)
            # throttle_reasons = {
            #     0x0000000000000001: "GpuIdle",
            #     0x0000000000000004: "SwPowerCap",
            #     0x0000000000000008: "HwSlowdown",
            #     0x0000000000000010: "SyncBoost",
            #     0x0000000000000020: "SwThermalSlowdown",
            #     0x0000000000000040: "HwThermalSlowdown",
            #     0x0000000000000080: "HwPowerBrakeSlowdown",
            #     0x0000000000000100: "DisplayClockSetting",
            #     0x0000000000000200: "ApplicationsClocksSetting",
            #     0x0000000000000400: "UserDefinedClocks"
            # }
            # reasons = []
            # # Check each bit and add corresponding reason to list
            # for bitmask, reason_text in throttle_reasons.items():
            #     if throttle_reason & bitmask:
            #         reasons.append(reason_text)
            # print(reasons)

            # Temperature
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            metrics['temperature_c'] = temp

            # Fan speed
            fan_speed = nvmlDeviceGetFanSpeed(handle)
            metrics['fan_speed_percent'] = fan_speed

            # Clock speeds
            graphics_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)
            sm_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM)
            mem_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_MEM)
            video_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_VIDEO)

            metrics['graphics_clock_mhz'] = graphics_clock
            metrics['sm_clock_mhz'] = sm_clock
            metrics['mem_clock_mhz'] = mem_clock
            metrics['video_clock_mhz'] = video_clock

            # Utilization
            utilization = nvmlDeviceGetUtilizationRates(handle)
            metrics['gpu_utilization_percent'] = utilization.gpu
            metrics['mem_utilization_percent'] = utilization.memory

            # Memory info
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            metrics['mem_used_mb'] = mem_info.used / (1024 * 1024)
            metrics['mem_free_mb'] = mem_info.free / (1024 * 1024)
            metrics['mem_total_mb'] = mem_info.total / (1024 * 1024)

        except NVMLError as e:
            print(f"Error getting metrics: {e}")
            return None

        return metrics

    def setup_csv(self):
        """Setup CSV file with headers"""
        # Generate fieldnames for all GPUs
        for gpu_idx in self.gpu_indices:
            for metric in [
                'power_usage_w', 'power_cap_w', 'pstate', 'temperature_c', 'fan_speed_percent',
                'graphics_clock_mhz', 'sm_clock_mhz', 'mem_clock_mhz', 'video_clock_mhz',
                'gpu_utilization_percent', 'mem_utilization_percent',
                'mem_used_mb', 'mem_free_mb', 'mem_total_mb'
            ]:
                self.fieldnames.append(f'gpu{gpu_idx}_{metric}')

        # Write header to CSV
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    def log_metrics(self):
        """Log metrics for all specified GPUs"""
        nvmlInit()

        try:
            device_count = nvmlDeviceGetCount()
            print(f"Found {device_count} GPU(s)")

            # Validate GPU indices
            valid_indices = []
            for idx in self.gpu_indices:
                if idx < device_count:
                    valid_indices.append(idx)
                    handle = nvmlDeviceGetHandleByIndex(idx)
                    print(f"Monitoring GPU {idx}: {nvmlDeviceGetName(handle)}")
                else:
                    print(f"Warning: GPU index {idx} not available (only {device_count} GPUs found)")

            if not valid_indices:
                print("No valid GPU indices to monitor")
                return

            self.gpu_indices = valid_indices
            self.setup_csv()

            print(f"Logging to {self.output_file}. Press Ctrl+C to stop and show statistics.")

            # Main logging loop
            while self.running:
                timestamp = datetime.now().isoformat()
                row_data = {'timestamp': timestamp}

                for gpu_idx in self.gpu_indices:
                    try:
                        handle = nvmlDeviceGetHandleByIndex(gpu_idx)
                        metrics = self.get_gpu_metrics(handle)

                        if metrics:
                            for metric_name, value in metrics.items():
                                row_data[f'gpu{gpu_idx}_{metric_name}'] = value

                    except NVMLError as e:
                        print(f"Error accessing GPU {gpu_idx}: {e}")
                        continue

                # Write to CSV
                with open(self.output_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                    writer.writerow(row_data)

                self.data.append(row_data)
                time.sleep(1)

        finally:
            nvmlShutdown()

    def calculate_statistics(self):
        """Calculate and display statistics for collected data"""
        if not self.data:
            print("No data collected")
            return

        # Group metrics by field
        metrics_by_field = defaultdict(list)

        for row in self.data:
            for field, value in row.items():
                if field != 'timestamp' and value is not None:
                    try:
                        metrics_by_field[field].append(float(value))
                    except (ValueError, TypeError):
                        pass

        print("\n" + "="*60)
        print("GPU Monitoring Statistics")
        print("="*60)

        for field, values in metrics_by_field.items():
            if values:
                mean_val = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                print(f"{field}:")
                print(f"  Mean: {mean_val:.2f}")
                print(f"  Min:  {min_val:.2f}")
                print(f"  Max:  {max_val:.2f}")
                print(f"  Samples: {len(values)}")
                print()

def main():
    parser = argparse.ArgumentParser(description='Log GPU metrics to CSV file')
    parser.add_argument('--gpus', type=str, default='0',
                       help='Comma-separated list of GPU indices to monitor (e.g., "0,1,2")')
    parser.add_argument('--output', type=str, default='gpu_metrics.csv',
                       help='Output CSV filename')

    args = parser.parse_args()

    # Parse GPU indices
    try:
        gpu_indices = [int(idx.strip()) for idx in args.gpus.split(',')]
    except ValueError:
        print("Error: Invalid GPU indices format. Use comma-separated integers (e.g., '0,1,2')")
        sys.exit(1)

    # Initialize and run logger
    logger = GPULogger(gpu_indices, args.output)

    try:
        logger.log_metrics()
    except Exception as e:
        print(f"Error during logging: {e}")
    finally:
        logger.calculate_statistics()
        print("Logging completed.")

if __name__ == "__main__":
    main()
