#!/usr/bin/env python3
"""
Script to regenerate protobuf files after updating proto definitions
"""

import os
import subprocess
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def regenerate_protos():
    """Regenerate all protobuf files"""
    
    # Get paths relative to project root
    protos_dir = os.path.join(project_root, "protos")
    generated_dir = os.path.join(project_root, "generated")
    
    print("Regenerating protobuf files...")
    print(f"Project root: {project_root}")
    print(f"Protos directory: {protos_dir}")
    print(f"Generated directory: {generated_dir}")
    
    # Ensure generated directory exists
    os.makedirs(generated_dir, exist_ok=True)
    
    # List all proto files
    proto_files = []
    for file in os.listdir(protos_dir):
        if file.endswith('.proto'):
            proto_files.append(os.path.join(protos_dir, file))
    
    print(f"Found proto files: {proto_files}")
    
    # Generate Python files for each proto
    for proto_file in proto_files:
        try:
            cmd = [
                "python3", "-m", "grpc_tools.protoc",
                f"--python_out={generated_dir}",
                f"--grpc_python_out={generated_dir}",
                f"--proto_path={protos_dir}",
                proto_file
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully generated files for {os.path.basename(proto_file)}")
            else:
                print(f"❌ Failed to generate files for {os.path.basename(proto_file)}")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Exception while processing {os.path.basename(proto_file)}: {e}")
    
    # Create __init__.py if it doesn't exist
    init_file = os.path.join(generated_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Generated protobuf files\n")
        print("✅ Created __init__.py in generated directory")
    
    print("\nProtobuf regeneration complete!")

if __name__ == "__main__":
    regenerate_protos() 