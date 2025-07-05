#!/usr/bin/env python3
"""
Script tùy chỉnh để tải model cho face_swapper với logging chi tiết
"""

import os
import sys
import subprocess

def main():
    """Tải xuống models cho face_swapper"""
    
    print("=== BẮT ĐẦU TẢI XUỐNG MODELS ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Kiểm tra facefusion.py có tồn tại không
    if not os.path.exists('facefusion.py'):
        print("ERROR: facefusion.py không tồn tại!")
        return False
    
    print("✓ facefusion.py tồn tại")
    
    try:
        # Chạy force-download với logging chi tiết
        print("Đang chạy: python3 facefusion.py force-download")
        
        # Sử dụng subprocess.Popen để có thể thấy output real-time
        process = subprocess.Popen(
            ['python3', 'facefusion.py', 'force-download'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # In output theo thời gian thực
        if process.stdout:
            for line in process.stdout:
                print(f"[FACEFUSION] {line.rstrip()}")
        
        # Đợi process hoàn thành
        return_code = process.wait()
        
        if return_code == 0:
            print("✓ TẢI XUỐNG MODELS THÀNH CÔNG!")
            return True
        else:
            print(f"✗ TẢI XUỐNG MODELS THẤT BẠI! Return code: {return_code}")
            return False
            
    except Exception as e:
        print(f"✗ LỖI KHI TẢI XUỐNG: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("=== KẾT THÚC ===")
    
    if success:
        print("SUCCESS: Models đã được tải xuống thành công!")
        sys.exit(0)
    else:
        print("FAILED: Không thể tải xuống models!")
        sys.exit(1) 