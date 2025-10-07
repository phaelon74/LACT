# RTX PRO 6000 Blackwell Dual GPU Configuration Guide

## Summary

This guide helps you configure your **TWO** Nvidia RTX PRO 6000 Blackwell workstation cards using LACT for undervolting and overclocking. Both GPUs will use identical settings.

## Files Created

1. **RTXPro6000Blackwell.yaml** - Complete LACT configuration file with conservative settings
2. **README.md** - Updated with comprehensive Ubuntu CLI instructions

## Quick Start (Ubuntu)

### 1. Install LACT

```bash
# Download the latest .deb from releases
wget https://github.com/ilya-zlobintsev/LACT/releases/download/v0.6.0/lact_0.6.0_amd64.deb

# Install
sudo dpkg -i lact_0.6.0_amd64.deb
sudo apt-get install -f

# Ensure Nvidia drivers are installed
sudo apt install nvidia-driver-550 nvidia-cuda-toolkit
```

### 2. Verify Your GPU IDs

```bash
lact cli list-gpus
```

You should see BOTH GPUs:
```
10DE:2BB1-10DE:204B-0000:49:00.0 (NVIDIA RTX PRO 6000 Blackwell Workstation Edition)
10DE:2BB1-10DE:204B-0000:c5:00.0 (NVIDIA RTX PRO 6000 Blackwell Workstation Edition)
```

✅ **Good news**: The config file already has both GPU IDs configured!

### 3. Copy Configuration

```bash
# No need to edit - both GPU IDs are already set!
# Just copy to system config location
sudo cp RTXPro6000Blackwell.yaml /etc/lact/config.yaml
```

### 4. Start LACT Daemon

```bash
# Enable and start the daemon
sudo systemctl enable --now lactd

# Check status
sudo systemctl status lactd
```

### 5. Verify Settings for BOTH GPUs

```bash
# View current GPU info (shows both GPUs)
lact cli info

# Monitor both GPUs in real-time
watch -n 1 nvidia-smi

# Check specific GPU power draw
nvidia-smi -q -d POWER

# Check temperatures for both
nvidia-smi -q -d TEMPERATURE
```

## Configuration Settings Explained

The provided configuration includes **conservative starting values** based on RTX PRO 6000 Blackwell specs:

### GPU Specifications (Blackwell Architecture - TechPowerUp Verified)
- **CUDA Cores**: ~24,064
- **Memory**: 96GB GDDR7
- **Base Clock**: 1590 MHz
- **Boost Clock**: 2617 MHz  
- **Memory Clock**: 1750 MHz (28 Gbps effective bandwidth)
- **TDP**: 600W

**CRITICAL**: Memory CLOCK is 1750 MHz, not 28000 MHz! The 28 Gbps is the effective data transfer rate.

### Power Settings - PRIMARY UNDERVOLTING METHOD
- **Power Cap**: 540W (10% reduction from 600W TDP)
  - **This is the ONLY way to undervolt Nvidia GPUs in LACT**
  - Limiting power forces the GPU to use lower voltages
  - Conservative: 540W (10% reduction)
  - Moderate: 480-510W (15-20% reduction)
  - Aggressive: 420-480W (20-30% reduction)

### Clock Configuration - TWO OPTIONS

**OPTION 1: Locked Clocks (Default in Config)**
- **Core Clocks**: min: 1800 MHz, max: 2400 MHz
  - Locks GPU to operate within this range
  - Max reduced ~8% from stock boost (2617 MHz)
  - Good for consistent performance with undervolting
  
- **Memory Clocks**: min: 1600 MHz, max: 1700 MHz
  - Slightly below stock (1750 MHz actual clock)
  - Conservative for stability with undervolting

**OPTION 2: Clock Offsets (Alternative)**
- **GPU Clock Offset**: +100 to +150 MHz (per-pstate)
  - Adds offset to each performance state
  - Example: +150 MHz → 2617 + 150 = 2767 MHz boost
  - More flexible than locked clocks
  - Better for pure overclocking
  
- **Memory Clock Offset**: +100 to +150 MHz
  - Example: +150 MHz → 1750 + 150 = 1900 MHz
  - GDDR7 can handle moderate overclocking
  - Start at +100 MHz and test stability

### Fan Curve
- Temperature-based automatic fan control
- Ranges from 30% at 40°C to 90% at 80°C
- Optimized for quiet operation at lower temps
- Auto-threshold at 40°C allows zero-RPM when idle

## Adjustment Guidelines

### Testing Stability

1. **Start conservative** - Use the provided settings as baseline
2. **Stress test** - Run your typical workload or a GPU benchmark
3. **Monitor temps** - Keep GPU under 85°C for longevity
4. **Increase gradually** - Adjust clocks by +25-50 MHz at a time
5. **Test each change** - Run stress tests after each adjustment

### Recommended Stress Tests

```bash
# Install GPU benchmarking tools
sudo apt install mesa-utils glmark2

# Basic OpenGL test
glxgears

# More intensive benchmark
glmark2

# For CUDA workloads - use your specific applications
```

### If You Experience Issues

**System crashes or artifacts:**
- Reduce clock offsets by -25 MHz
- Settings auto-revert after 5 seconds if system becomes unresponsive
- Reboot to reset GPU to defaults

**GPU running too hot:**
- Lower power_cap by 10-20W
- Increase fan curve aggressiveness
- Reduce clock offsets

**Not seeing performance gains:**
- Increase clock offsets gradually
- Raise power_cap by 10W increments (don't exceed card's TDP rating)

## Dual GPU Power Considerations

With two RTX PRO 6000 Blackwell GPUs, power consumption is critical:

### Power Usage by Profile:

| Profile | Per GPU | Total (Both GPUs) | vs Stock |
|---------|---------|-------------------|----------|
| **Default** | 450W | **900W** | -25% (saves 300W!) |
| **Performance** | 600W | **1,200W** | Stock TDP |
| **Balanced** | 500W | **1,000W** | -17% (saves 200W) |
| **Efficiency** | 420W | **840W** | -30% (saves 360W!) |

**PSU Requirements:**
- Minimum: 1500W PSU for Performance profile + system overhead
- Recommended: 1600-1800W PSU for headroom
- With default 450W setting: 1200-1400W PSU is sufficient

## Advanced: Multiple Profiles

The config includes three profiles that apply to **BOTH GPUs simultaneously**:

1. **Performance** - Maximum performance (1200W total)
   - Full 600W per GPU
   - +150 MHz core / +150 MHz memory
   - More aggressive fan curve

2. **Balanced** - Moderate power (1000W total)
   - 500W per GPU
   - Locked clocks slightly below stock
   - Balanced fan curve

3. **Efficiency** - Low power (840W total)
   - 420W per GPU (30% reduction!)
   - Reduced locked clocks
   - Quieter fan curve

### Switch Profiles

```bash
# List profiles
lact cli profile list

# Switch to Performance
lact cli profile set "Performance"

# Switch to Efficiency
lact cli profile set "Efficiency"

# Return to default
lact cli profile set "Default"
```

## Important Safety Notes

1. **Blackwell GPUs are NEW** - Specific safe limits are not yet widely documented
2. **Professional cards prioritize stability** - Don't push as hard as gaming cards
3. **Your mileage may vary** - Every chip is different (silicon lottery)
4. **Monitor closely** - Watch temps, power draw, and stability
5. **Backup your work** - Before testing aggressive settings
6. **Start conservative** - It's easier to increase than recover from damage

## Troubleshooting

### Daemon won't start
```bash
# Check logs
sudo journalctl -u lactd -f

# Verify config syntax
sudo nano /etc/lact/config.yaml
```

### Settings not applying
```bash
# Ensure GPU ID is correct
lact cli list-gpus

# Restart daemon
sudo systemctl restart lactd
```

### Permission denied
```bash
# Add your user to sudo group
sudo usermod -aG sudo $USER

# Or edit config to specify your user
sudo nano /etc/lact/config.yaml
# Add under daemon section:
#   admin_user: your_username
```

## Resources

- [LACT GitHub Repository](https://github.com/ilya-zlobintsev/LACT)
- [LACT Configuration Documentation](https://github.com/ilya-zlobintsev/LACT/blob/master/docs/CONFIG.md)
- [LACT API Documentation](https://github.com/ilya-zlobintsev/LACT/blob/master/docs/API.md)
- [Nvidia Overclocking FAQ](https://github.com/ilya-zlobintsev/LACT/wiki/Frequently-asked-questions#how-to-undervolt-nvidia-gpus)

## Critical Information: Nvidia GPU Control in LACT

### What WORKS on Nvidia:

1. **Power Cap** (primary undervolting method)
   - Reducing `power_cap` forces GPU to use lower voltages
   - Most effective way to reduce power/heat on Nvidia

2. **Locked Clocks** (min/max together)
   - `min_core_clock` + `max_core_clock` must be set together
   - `min_memory_clock` + `max_memory_clock` must be set together
   - Creates fixed frequency ranges

3. **Clock Offsets** (per-performance-state)
   - `gpu_clock_offsets` - per-pstate core clock adjustments
   - `mem_clock_offsets` - per-pstate memory clock adjustments
   - More flexible than locked clocks

4. **Fan Control**
   - Full fan curve support
   - Static speed mode
   - Auto-threshold for zero-RPM mode

### What DOES NOT WORK on Nvidia (AMD only):

❌ `min_voltage` - Ignored by Nvidia controller  
❌ `max_voltage` - Ignored by Nvidia controller  
❌ `voltage_offset` - AMD RDNA only  
❌ `performance_level` - AMD specific  
❌ `power_states` - AMD specific  
❌ `power_profile_mode_index` - AMD specific  

### How Undervolting Actually Works on Nvidia:

**Method 1: Power Cap Reduction (Easiest)**
```yaml
power_cap: 480.0  # Reduce from 600W to force lower voltages
```

**Method 2: Locked Clocks + Reduced Power**
```yaml
power_cap: 500.0
min_core_clock: 1800
max_core_clock: 2200  # Lower than stock boost
```
GPU runs at lower clocks → needs less voltage → power limit forces it lower

**Method 3: Clock Offsets + Power Limit**
```yaml
power_cap: 520.0
gpu_clock_offsets:
  0: -100  # Negative offset = lower clocks = less voltage needed
```

### For Advanced Voltage Curve Control:

LACT cannot edit Nvidia voltage curves directly. Use these tools instead:
- **MSI Afterburner** (Windows/Wine) - Full voltage curve editor
- **GreenWithEnvy** (Linux native GUI) - Some voltage control
- **nvidia-settings** (Linux) - Limited control
- **nvidia-smi** (CLI) - Power limits only

The config file includes three profiles optimized for different scenarios (all apply to BOTH GPUs):
- **Performance**: 600W per GPU (1200W total), high clocks
- **Balanced**: 500W per GPU (1000W total), moderate clocks  
- **Efficiency**: 420W per GPU (840W total, 30% reduction), reduced clocks

## Dual GPU Monitoring Commands

Monitor both GPUs effectively:

```bash
# Monitor both GPUs continuously (most useful)
watch -n 1 nvidia-smi

# Detailed power info for both GPUs
nvidia-smi -q -d POWER

# Temperature monitoring with continuous updates
nvidia-smi dmon -s pucvmet

# Per-GPU process monitoring
nvidia-smi pmon

# Query total power draw (CSV format)
nvidia-smi --query-gpu=index,name,power.draw,power.limit --format=csv

# Check PCIe link status for both GPUs
nvidia-smi -q -d PCIE
```

---

**Questions or Issues?** Check the main README.md for additional CLI commands and troubleshooting steps.

