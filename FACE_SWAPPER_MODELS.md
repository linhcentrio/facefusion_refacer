# Tối ưu hóa Models cho Face Swapper - V3

## Tổng quan

Dockerfile đã được tối ưu hóa để **chỉ tải xuống các model cần thiết** cho face_swapper từ [Hugging Face repository](https://huggingface.co/facefusion/models-3.0.0/tree/main) thay vì tải tất cả models, giúp giảm **đáng kể** kích thước Docker image cho RunPod serverless.

## 🎯 **Phương pháp V3 (Mới nhất)**

- **Tải chọn lọc từ Hugging Face**: Chỉ tải 10 files cần thiết (~730MB) thay vì ~15GB.
- **Sử dụng `inswapper_128_fp16`**: Model mặc định, nhẹ và hiệu suất cao.
- **Loại bỏ symlinks không cần thiết**: Script đơn giản và đáng tin cậy hơn.

## 📦 **Models được tải xuống (V3)**

### Face Swapper Model chính
- **`inswapper_128_fp16.onnx`** (278 MB) - Model face swapper chính

### Models hỗ trợ cần thiết
- **`arcface_w600k_r50.onnx`** (174 MB) - Face recognition (lấy embedding)
- **`bisenet_resnet_34.onnx`** (93.6 MB) - Face parsing/masking  
- **`2dfan4.onnx`** (97.9 MB) - Face landmarks detection
- **`fairface.onnx`** (85.2 MB) - Face classification

### Hash files (validation)
- Tất cả `.hash` files tương ứng để verify integrity

## 📊 **So sánh hiệu suất**

| Phương pháp | Kích thước | Models |
|-------------|-----------|--------|
| **V1 (Force-download)** | ~15GB | TẤT CẢ |
| **V2 (Ghost)** | ~1GB | ghost_1_256 + dependencies |
| **V3 (Inswapper)** | **~730MB** | **inswapper_128_fp16 + dependencies** |

### 🎉 **Lợi ích của V3**
- **Nhẹ nhất**: Giảm thêm 30% so với V2.
- **Chuẩn nhất**: Sử dụng model mặc định `inswapper_128_fp16`.
- **Nhanh nhất**: Thời gian tải và khởi động được tối ưu tối đa.

## 🚀 **Cách sử dụng**

### Build Docker image
```bash
docker build -t facefusion-face-swapper-v3 .
```

### Thay đổi model face_swapper
Sửa list `essential_models` trong `download_face_swapper_models.py`:

```python
essential_models = [
    # Thay inswapper_128_fp16 bằng model khác
    "inswapper_128.onnx",        # 555 MB (chất lượng cao hơn)
    "inswapper_128.hash",
    # ... và giữ các model phụ thuộc
]
```

## 🔗 **Nguồn gốc models**

Tất cả models được tải từ repository chính thức:
**[facefusion/models-3.0.0](https://huggingface.co/facefusion/models-3.0.0/tree/main)**

## 🛠️ **Troubleshooting**

### Nếu script HuggingFace thất bại
Dockerfile sẽ tự động fallback về `facefusion.py force-download` để đảm bảo ứng dụng vẫn có thể khởi động.

### Nếu thiếu models
1. Kiểm tra list `essential_models` trong script.
2. Thêm model cần thiết từ HuggingFace vào list.
3. Rebuild Docker image.

## ✅ **Kết luận**

Phiên bản V3 là phiên bản **tối ưu nhất** cho RunPod serverless, đảm bảo kích thước nhỏ nhất, tốc độ nhanh nhất và sử dụng đúng model mặc định. 