#!/bin/bash

# Test I2C access from container
echo "🔍 Testing I2C access..."

# Check if I2C devices exist
echo "📱 I2C devices:"
ls -la /dev/i2c*

# Check I2C bus status
echo "🚌 I2C bus status:"
i2cdetect -y 1 2>/dev/null || echo "i2cdetect failed"

# Check if we can read from I2C
echo "📖 Testing I2C read:"
python3 -c "
import smbus2
try:
    bus = smbus2.SMBus(1)
    print('✅ I2C bus accessible')
    # Try to read from a common address
    try:
        data = bus.read_byte_data(0x0b, 0)  # PDB address
        print(f'✅ Read from PDB: {data}')
    except Exception as e:
        print(f'❌ PDB read failed: {e}')
    bus.close()
except Exception as e:
    print(f'❌ I2C bus access failed: {e}')
"
