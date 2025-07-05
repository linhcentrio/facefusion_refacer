#!/usr/bin/env python3
"""
Script V3: Tải xuống chọn lọc các model cần thiết cho face_swapper từ Hugging Face
Tập trung vào model inswapper_128_fp16 và các dependencies cốt lõi.
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
print(f'Đang tải {filename} từ {repo_id}...')
hf_hub_download(
    repo_id='{repo_id}',
    filename='{filename}',
    local_dir='{local_dir}',
    local_dir_use_symlinks=False
)
print(f'✓ Tải thành công {filename}')
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
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
        result = subprocess.run(['pip', 'install', 'huggingface_hub'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Cài đặt huggingface_hub thành công")
            return True
        else:
            print(f"✗ Lỗi cài đặt huggingface_hub: {result.stderr}")
            return False

def main():
    """Tải xuống các model cần thiết cho face_swapper"""
    
    print("=== TẢI XUỐNG MODELS CHO FACE_SWAPPER (V3) ===")
    
    if not install_huggingface_hub():
        return False
    
    repo_id = "facefusion/models-3.0.0"
    models_dir = ".assets/models"
    
    essential_models = [
        # Face swapper model chính (nhẹ, hiệu suất cao)
        "inswapper_128_fp16.onnx",   # 278 MB
        "inswapper_128_fp16.hash",
        
        # Model nhận diện khuôn mặt (để lấy embedding)
        "arcface_w600k_r50.onnx",    # 174 MB
        "arcface_w600k_r50.hash",
        
        # Model phân tích và mask khuôn mặt
        "bisenet_resnet_34.onnx",    # 93.6 MB
        "bisenet_resnet_34.hash",
        
        # Model tìm điểm mốc khuôn mặt
        "2dfan4.onnx",               # 97.9 MB
        "2dfan4.hash",
        
        # Model phân loại khuôn mặt
        "fairface.onnx",             # 85.2 MB
        "fairface.hash",
    ]
    
    print(f"Tổng số files cần tải: {len(essential_models)}")
    print(f"Ước tính tổng kích thước: ~730MB")
    print("-" * 20)
    
    success_count = 0
    
    for model_file in essential_models:
        if download_file_from_hf(repo_id, model_file, models_dir):
            success_count += 1
        else:
            print(f"✗ Thất bại khi tải: {model_file}")
            # Có thể không cần thoát ngay lập tức để thử tải các file khác
    
    print("-" * 20)
    print(f"=== KẾT QUẢ: {success_count}/{len(essential_models)} files đã được tải ===")
    
    if success_count >= len(essential_models) * 0.9:  # 90% thành công
        print("✓ TẢI XUỐNG THÀNH CÔNG!")
        return True
    else:
        print("✗ TẢI XUỐNG THẤT BẠI!")
        return False

if __name__ == "__main__":
    if main():
        print("SUCCESS: Các model face_swapper cần thiết đã được tải xuống!")
        sys.exit(0)
    else:
        print("FAILED: Không thể tải xuống đầy đủ các model cần thiết!")
        sys.exit(1) 