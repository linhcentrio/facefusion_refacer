#!/usr/bin/env python3
"""
Script backup đơn giản để tải model cơ bản nhất cho face_swapper
Chỉ tải inswapper_128_fp16 và retinaface
"""

import sys
import os

# Thêm đường dẫn facefusion vào PYTHONPATH
sys.path.insert(0, '/facefusion')

try:
    # Import sau khi thêm path
    from facefusion.download import conditional_download_hashes, conditional_download_sources
    from facefusion.processors.modules.face_swapper import create_static_model_set as create_face_swapper_set
    from facefusion.face_detector import create_static_model_set as create_face_detector_set
    
    print("Đang tải model inswapper_128_fp16...")
    
    # Tải face_swapper model
    face_swapper_models = create_face_swapper_set('full')
    if 'inswapper_128_fp16' in face_swapper_models:
        model = face_swapper_models['inswapper_128_fp16']
        hash_set = model.get('hashes')
        source_set = model.get('sources')
        
        if hash_set and source_set:
            if conditional_download_hashes(hash_set) and conditional_download_sources(source_set):
                print("✓ Tải thành công inswapper_128_fp16")
            else:
                print("✗ Tải thất bại inswapper_128_fp16")
                sys.exit(1)
        else:
            print("✗ Không tìm thấy hash/source cho inswapper_128_fp16")
            sys.exit(1)
    else:
        print("✗ Không tìm thấy model inswapper_128_fp16")
        sys.exit(1)
    
    print("Đang tải model retinaface...")
    
    # Tải face_detector model
    face_detector_models = create_face_detector_set('full')
    if 'retinaface' in face_detector_models:
        model = face_detector_models['retinaface']
        hash_set = model.get('hashes')
        source_set = model.get('sources')
        
        if hash_set and source_set:
            if conditional_download_hashes(hash_set) and conditional_download_sources(source_set):
                print("✓ Tải thành công retinaface")
            else:
                print("✗ Tải thất bại retinaface")
                sys.exit(1)
        else:
            print("✗ Không tìm thấy hash/source cho retinaface")
            sys.exit(1)
    else:
        print("✗ Không tìm thấy model retinaface")
        sys.exit(1)
    
    print("Hoàn thành tải model cơ bản!")
    
except Exception as e:
    print(f"Lỗi: {e}")
    sys.exit(1) 