#!/usr/bin/env python3
"""
Script tùy chỉnh để tải xuống chỉ các model cần thiết cho face_swapper
Giảm thiểu kích thước Docker image cho RunPod serverless
"""

import os
import sys
import importlib

# Thêm đường dẫn facefusion vào PYTHONPATH
sys.path.insert(0, '/facefusion')

def download_face_swapper_models():
    """Tải xuống các model cần thiết cho face_swapper"""
    
    # Import sau khi thêm path
    from facefusion import state_manager
    from facefusion.download import conditional_download_hashes, conditional_download_sources
    
    print("Bắt đầu tải xuống models cho face_swapper...")
    
    # Danh sách module và model cần tải
    module_configs = [
        {
            'module': 'facefusion.processors.modules.face_swapper',
            'model_key': 'face_swapper_model',
            'default_model': 'inswapper_128_fp16'
        },
        {
            'module': 'facefusion.face_detector',
            'model_key': 'face_detector_model', 
            'default_model': 'retinaface'
        },
        {
            'module': 'facefusion.face_landmarker',
            'model_key': 'face_landmarker_model',
            'default_model': 'many'
        },
        {
            'module': 'facefusion.face_recognizer',
            'model_key': 'face_recognizer_model',
            'default_model': 'arcface_w600k_r50'
        },
        {
            'module': 'facefusion.face_classifier',
            'model_key': 'face_classifier_model',
            'default_model': 'opennsfw'
        },
        {
            'module': 'facefusion.face_masker',
            'model_key': None,  # Có 2 models: face_occluder_model và face_parser_model
            'default_model': None
        },
        {
            'module': 'facefusion.content_analyser',
            'model_key': 'content_analyser_model',
            'default_model': 'open_clip'
        }
    ]
    
    success_count = 0
    total_count = len(module_configs)
    
    for config in module_configs:
        try:
            module_name = config['module']
            print(f"Đang tải model cho {module_name}...")
            
            # Import module
            module = importlib.import_module(module_name)
            
            if not hasattr(module, 'create_static_model_set'):
                print(f"Module {module_name} không có create_static_model_set")
                continue
            
            # Lấy model set
            model_set = module.create_static_model_set('full')
            
            # Xử lý đặc biệt cho face_masker (có 2 models)
            if module_name == 'facefusion.face_masker':
                # Tải cả 2 model: face_occluder và face_parser
                for model_name in ['bisenet', 'occluder']:  # Có thể cần điều chỉnh tên model
                    if model_name in model_set:
                        model = model_set[model_name]
                        if download_model(model, model_name):
                            print(f"✓ Tải thành công {model_name}")
                        else:
                            print(f"✗ Tải thất bại {model_name}")
                            return False
                success_count += 1
            else:
                # Tải model đơn lẻ
                model_name = config['default_model']
                if model_name in model_set:
                    model = model_set[model_name]
                    if download_model(model, model_name):
                        print(f"✓ Tải thành công {model_name}")
                        success_count += 1
                    else:
                        print(f"✗ Tải thất bại {model_name}")
                        return False
                else:
                    print(f"Model {model_name} không tồn tại trong {module_name}")
                    # Thử tải model đầu tiên trong set
                    if model_set:
                        first_model_name = list(model_set.keys())[0]
                        model = model_set[first_model_name]
                        if download_model(model, first_model_name):
                            print(f"✓ Tải thành công {first_model_name} (mặc định)")
                            success_count += 1
                        else:
                            print(f"✗ Tải thất bại {first_model_name}")
                            return False
                    
        except Exception as e:
            print(f"Lỗi khi tải {config['module']}: {str(e)}")
            return False
    
    print(f"Hoàn thành tải xuống {success_count}/{total_count} modules!")
    return success_count > 0

def download_model(model_config, model_name):
    """Tải xuống một model cụ thể"""
    from facefusion.download import conditional_download_hashes, conditional_download_sources
    
    model_hash_set = model_config.get('hashes')
    model_source_set = model_config.get('sources')
    
    if not model_hash_set or not model_source_set:
        print(f"Không có hash/source cho model {model_name}")
        return False
    
    print(f"Đang tải {model_name}...")
    success = conditional_download_hashes(model_hash_set) and conditional_download_sources(model_source_set)
    return success

if __name__ == "__main__":
    if download_face_swapper_models():
        print("Tải xuống models thành công!")
        sys.exit(0)
    else:
        print("Tải xuống models thất bại!")
        sys.exit(1) 