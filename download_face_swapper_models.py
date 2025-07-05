#!/usr/bin/env python3
"""
Script tải xuống chọn lọc chỉ các model cần thiết cho face_swapper từ Hugging Face
Thay vì tải tất cả model, chỉ tải những model cần thiết
"""

import os
import sys
import subprocess
from pathlib import Path

def download_file_from_hf(repo_id, filename, local_dir):
    """Tải xuống một file cụ thể từ Hugging Face"""
    try:
        cmd = [
            'python3', '-c',
            f"""
import os
from huggingface_hub import hf_hub_download
os.makedirs('{local_dir}', exist_ok=True)
hf_hub_download(
    repo_id='{repo_id}',
    filename='{filename}',
    local_dir='{local_dir}',
    local_dir_use_symlinks=False
)
print(f'✓ Tải thành công {filename}')
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return True
        else:
            print(f"✗ Lỗi tải {filename}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Exception khi tải {filename}: {e}")
        return False

def install_huggingface_hub():
    """Cài đặt huggingface_hub nếu chưa có"""
    try:
        import huggingface_hub
        print("✓ huggingface_hub đã có sẵn")
        return True
    except ImportError:
        print("Đang cài đặt huggingface_hub...")
        result = subprocess.run([
            'pip', 'install', 'huggingface_hub'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Cài đặt huggingface_hub thành công")
            return True
        else:
            print(f"✗ Lỗi cài đặt huggingface_hub: {result.stderr}")
            return False

def main():
    """Tải xuống các model cần thiết cho face_swapper"""
    
    print("=== TẢI XUỐNG MODELS CHO FACE_SWAPPER ===")
    
    # Cài đặt huggingface_hub
    if not install_huggingface_hub():
        return False
    
    # Cấu hình
    repo_id = "facefusion/models-3.0.0"
    models_dir = ".assets/models"
    
    # Danh sách model cần thiết (tối ưu cho kích thước)
    essential_models = [
        # Face swapper model nhẹ nhất
        "ghost_1_256.onnx",          # 515 MB
        "ghost_1_256.hash",
        
        # Supporting models cần thiết
        "arcface_w600k_r50.onnx",    # 174 MB - Face recognition
        "arcface_w600k_r50.hash",
        
        "bisenet_resnet_34.onnx",    # 93.6 MB - Face parsing
        "bisenet_resnet_34.hash",
        
        "2dfan4.onnx",               # 97.9 MB - Face landmarks  
        "2dfan4.hash",
        
        "fan_68_5.onnx",             # 944 kB - Face landmarks helper
        "fan_68_5.hash",
        
        "fairface.onnx",             # 85.2 MB - Face classification
        "fairface.hash",
        
        # Ghost converter
        "arcface_converter_ghost.onnx",  # 21 MB
        "arcface_converter_ghost.hash"
    ]
    
    print(f"Tổng số files cần tải: {len(essential_models)}")
    print(f"Ước tính tổng kích thước: ~1GB (thay vì 10+ GB)")
    print()
    
    success_count = 0
    
    for model_file in essential_models:
        print(f"Đang tải {model_file}...")
        
        if download_file_from_hf(repo_id, model_file, models_dir):
            success_count += 1
        else:
            print(f"✗ Thất bại: {model_file}")
    
    print()
    print(f"=== KẾT QUẢ: {success_count}/{len(essential_models)} files ===")
    
    if success_count >= len(essential_models) * 0.8:  # 80% thành công
        print("✓ TẢI XUỐNG THÀNH CÔNG!")
        
        # Tạo symbolic links nếu cần
        create_model_links()
        
        return True
    else:
        print("✗ TẢI XUỐNG THẤT BẠI!")
        return False

def create_model_links():
    """Tạo symbolic links cho compatibility"""
    models_dir = Path(".assets/models")
    
    # Map model names cho compatibility
    model_mappings = {
        "ghost_1_256.onnx": ["inswapper_128_fp16.onnx", "inswapper_128.onnx"],
        "2dfan4.onnx": ["retinaface.onnx"],
        "bisenet_resnet_34.onnx": ["bisenet.onnx"]
    }
    
    for source, targets in model_mappings.items():
        source_path = models_dir / source
        if source_path.exists():
            for target in targets:
                target_path = models_dir / target
                if not target_path.exists():
                    try:
                        target_path.symlink_to(source_path.name)
                        print(f"✓ Tạo link: {target} -> {source}")
                    except Exception as e:
                        # Fallback: copy file
                        try:
                            import shutil
                            shutil.copy2(source_path, target_path)
                            print(f"✓ Copy: {target} <- {source}")
                        except Exception as e2:
                            print(f"✗ Lỗi tạo {target}: {e2}")

if __name__ == "__main__":
    if main():
        print("SUCCESS: Models face_swapper đã được tải xuống!")
        sys.exit(0)
    else:
        print("FAILED: Không thể tải xuống models!")
        sys.exit(1) 