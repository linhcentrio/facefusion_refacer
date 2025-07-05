#!/usr/bin/env python3
"""
Script backup đơn giản để tải model cơ bản cho face_swapper
Sử dụng lệnh force-download cơ bản
"""

import sys
import subprocess

def download_minimal_models():
    """Tải xuống model cơ bản nhất cho face_swapper"""
    
    print("Đang tải model cơ bản cho face_swapper...")
    
    try:
        # Sử dụng lệnh force-download cơ bản
        cmd = ['python3', 'facefusion.py', 'force-download']
        
        print("Đang chạy lệnh:", ' '.join(cmd))
        
        result = subprocess.run(cmd, timeout=1200)  # 20 phút timeout
        
        if result.returncode == 0:
            print("✓ Tải xuống models thành công!")
            return True
        else:
            print(f"✗ Tải xuống models thất bại! Return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Timeout khi tải xuống models!")
        return False
    except Exception as e:
        print(f"✗ Lỗi khi tải xuống models: {e}")
        return False

if __name__ == "__main__":
    if download_minimal_models():
        print("Tải xuống models thành công!")
        sys.exit(0)
    else:
        print("Tải xuống models thất bại!")
        sys.exit(1) 