# Tối ưu hóa Models cho Face Swapper - V2

## Tổng quan

Dockerfile đã được tối ưu hóa để **chỉ tải xuống các model cần thiết** cho face_swapper từ [Hugging Face repository](https://huggingface.co/facefusion/models-3.0.0/tree/main) thay vì tải tất cả models, giúp giảm **đáng kể** kích thước Docker image cho RunPod serverless.

## 🎯 **Phương pháp mới**

### V1 (Cũ): Force-download tất cả
- Tải **TẤT CẢ** models (~10-15GB)
- Lãng phí băng thông và storage
- Chậm khởi động

### V2 (Mới): Tải chọn lọc từ Hugging Face
- **Chỉ tải 14 files** cần thiết (~1GB)
- Sử dụng `huggingface_hub` để download chính xác
- Nhanh và hiệu quả

## 📦 **Models được tải xuống (từ HuggingFace)**

### Face Swapper Model chính
- **`ghost_1_256.onnx`** (515 MB) - Model face swapper nhẹ và hiệu quả

### Models hỗ trợ cần thiết
- **`arcface_w600k_r50.onnx`** (174 MB) - Face recognition
- **`bisenet_resnet_34.onnx`** (93.6 MB) - Face parsing/masking  
- **`2dfan4.onnx`** (97.9 MB) - Face landmarks detection
- **`fan_68_5.onnx`** (944 kB) - Face landmarks helper
- **`fairface.onnx`** (85.2 MB) - Face classification
- **`arcface_converter_ghost.onnx`** (21 MB) - Embedding converter

### Hash files (validation)
- Tất cả `.hash` files tương ứng để verify integrity

## 🔧 **Script hoạt động như thế nào**

### 1. Script chính: `download_face_swapper_models.py`
```python
# Tải xuống chọn lọc từ HuggingFace
repo_id = "facefusion/models-3.0.0"
essential_models = [
    "ghost_1_256.onnx",           # 515 MB
    "arcface_w600k_r50.onnx",     # 174 MB  
    "bisenet_resnet_34.onnx",     # 93.6 MB
    # ... chỉ những files cần thiết
]
```

### 2. Model mapping & compatibility
- Tự động tạo symlinks: `ghost_1_256.onnx` → `inswapper_128_fp16.onnx`
- Đảm bảo compatibility với FaceFusion code

## 📊 **So sánh hiệu suất**

| Phương pháp | Kích thước | Thời gian tải | Models |
|-------------|-----------|---------------|--------|
| **V1 (Force-download)** | ~10-15GB | 15-30 phút | TẤT CẢ |
| **V2 (Selective HF)** | ~1GB | 3-5 phút | CHỈ CẦN THIẾT |

### 🎉 **Lợi ích**
- **90% giảm kích thước**: 15GB → 1GB
- **80% giảm thời gian**: 30 phút → 5 phút  
- **Tiết kiệm băng thông**: Chỉ tải cần thiết
- **Nhanh khởi động**: Ít model load
- **Dễ maintain**: Rõ ràng những gì cần

## 🚀 **Cách sử dụng**

### Build Docker image
```bash
docker build -t facefusion-face-swapper-v2 .
```

### Thay đổi model face_swapper
Nếu muốn model khác, sửa `essential_models` trong script:

```python
essential_models = [
    # Thay ghost_1_256 bằng model khác
    "ghost_2_256.onnx",          # 739 MB (chất lượng tốt hơn)
    "ghost_2_256.hash",
    # hoặc
    "blendswap_256.onnx",        # 1.66 GB (chất lượng cao nhất)
    "blendswap_256.hash",
    # ...
]
```

### Các model face_swapper có sẵn trên HuggingFace
- **`ghost_1_256.onnx`** (515 MB) - Nhẹ, nhanh ✅ *Mặc định*
- **`ghost_2_256.onnx`** (739 MB) - Cân bằng
- **`ghost_3_256.onnx`** (856 MB) - Chất lượng cao
- **`blendswap_256.onnx`** (1.66 GB) - Chất lượng tốt nhất

## 🔗 **Nguồn gốc models**

Tất cả models được tải từ repository chính thức:
**[facefusion/models-3.0.0](https://huggingface.co/facefusion/models-3.0.0/tree/main)**

## 🛠️ **Troubleshooting**

### Nếu script HuggingFace thất bại
```bash
# Fallback về force-download
python3 facefusion.py force-download
```

### Nếu model không tương thích
1. Kiểm tra model mapping trong `create_model_links()`
2. Thêm symlink mới nếu cần
3. Đảm bảo đúng tên file

### Nếu thiếu models
1. Kiểm tra list `essential_models`
2. Thêm model cần thiết vào list
3. Rebuild Docker image

## ✅ **Kết luận**

Phiên bản V2 này **tối ưu hoàn toàn** cho RunPod serverless:
- **Chỉ tải những gì cần**: 1GB thay vì 15GB
- **Nhanh deployment**: 5 phút thay vì 30 phút
- **Tiết kiệm chi phí**: Ít bandwidth, ít storage
- **Rõ ràng, dễ maintain**: Biết chính xác model nào được sử dụng 