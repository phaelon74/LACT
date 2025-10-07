# Dual RTX PRO 6000 Blackwell Setup - Quick Reference

## Your GPUs

✅ **GPU 1**: `10DE:2BB1-10DE:204B-0000:49:00.0`  
✅ **GPU 2**: `10DE:2BB1-10DE:204B-0000:c5:00.0`

Both GPUs are **already configured** in the config file with identical settings.

## Quick Deploy

```bash
# 1. Verify GPUs are detected
lact cli list-gpus

# 2. Copy config (GPU IDs already set!)
sudo cp RTXPro6000Blackwell.yaml /etc/lact/config.yaml

# 3. Restart daemon
sudo systemctl restart lactd

# 4. Monitor both GPUs
watch -n 1 nvidia-smi
```

## Current Settings (Default Profile)

| Setting | Value | Notes |
|---------|-------|-------|
| **Power Cap** | 450W per GPU | 25% undervolt (saves 300W total!) |
| **Core Clocks** | 1800-2400 MHz | ~8% below stock boost |
| **Memory Clocks** | 1600-1700 MHz | Slightly below stock 1750 MHz |
| **Total Power** | **900W** | vs 1200W at stock |

## Power by Profile

| Profile | Per GPU | **Total System** | Savings |
|---------|---------|------------------|---------|
| Default | 450W | **900W** | -300W (-25%) |
| Performance | 600W | **1,200W** | Stock TDP |
| Balanced | 500W | **1,000W** | -200W (-17%) |
| Efficiency | 420W | **840W** | -360W (-30%) |

## PSU Requirements

- **Minimum**: 1500W for Performance mode
- **Recommended**: 1600-1800W for headroom
- **With default 450W**: 1200-1400W sufficient

## Switch Profiles

Both GPUs change together:

```bash
# Maximum performance (1200W total)
lact cli profile set "Performance"

# Balanced power (1000W total)
lact cli profile set "Balanced"

# Maximum efficiency (840W total)
lact cli profile set "Efficiency"

# Return to default (900W total)
lact cli profile set "Default"
```

## Monitoring Commands

```bash
# Real-time monitoring (most useful)
watch -n 1 nvidia-smi

# Power draw details
nvidia-smi -q -d POWER

# Temperature monitoring
nvidia-smi -q -d TEMPERATURE

# Both GPUs at a glance
nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw,clocks.gr,clocks.mem --format=csv
```

## Important Notes

1. ✅ **No manual editing needed** - GPU IDs are already configured
2. ⚡ **Total power**: 900W (vs 1200W stock) saves $$$
3. 🌡️ **Monitor temps**: Keep both GPUs under 85°C
4. 🔒 **Auto-revert**: Settings revert after 5 sec if system crashes
5. 📊 **Independent fans**: Each GPU controls its own fans
6. 🧪 **Test gradually**: Start with default, adjust if needed

## Troubleshooting

**If one GPU behaves differently:**
```bash
# Check both GPU stats individually
nvidia-smi -i 0  # GPU 1
nvidia-smi -i 1  # GPU 2

# View LACT info for both
lact cli info
```

**To reset to defaults:**
```bash
# Remove config
sudo rm /etc/lact/config.yaml

# Restart daemon
sudo systemctl restart lactd
```

## Files Included

- `RTXPro6000Blackwell.yaml` - Main config (both GPUs configured)
- `README_RTX_PRO_6000.md` - Detailed documentation
- `DUAL_GPU_SETUP.md` - This quick reference

---

**Ready to deploy!** Just copy the config and restart the daemon. 🚀

