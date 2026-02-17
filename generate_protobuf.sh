#!/bin/bash

# Generate Python protobuf files from .proto schema

echo "🔧 Generating Python protobuf files..."

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo "❌ protoc compiler not found. Installing..."
    
    # Try to install protoc
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y protobuf-compiler
    elif command -v brew &> /dev/null; then
        brew install protobuf
    else
        echo "❌ Cannot install protoc automatically. Please install it manually:"
        echo "   Ubuntu/Debian: sudo apt-get install protobuf-compiler"
        echo "   macOS: brew install protobuf"
        echo "   Windows: Download from https://github.com/protocolbuffers/protobuf/releases"
        exit 1
    fi
fi

# Generate Python files
echo "📝 Generating Python protobuf files..."
protoc --python_out=. rov_messages.proto

if [ $? -eq 0 ]; then
    echo "✅ Successfully generated rov_messages_pb2.py"
    echo "📁 Files created:"
    ls -la rov_messages_pb2.py
    
    # Clean up any old copies in subdirectories
    echo "🧹 Cleaning up old copies..."
    find . -name "rov_messages_pb2.py" -not -path "./rov_messages_pb2.py" -delete 2>/dev/null || true
    echo "✅ Cleanup complete"
else
    echo "❌ Failed to generate protobuf files"
    exit 1
fi

echo ""
echo "🚀 Protobuf setup complete! You can now:"
echo "   1. Deploy to Pi: ./docker-update.sh"
echo "   2. Test communication with surface station"
echo ""
echo "💡 Benefits of this setup:"
echo "   - Smaller message sizes (better for underwater communication)"
echo "   - Faster serialization/deserialization"
echo "   - Type-safe message handling"
echo "   - Schema evolution support"
