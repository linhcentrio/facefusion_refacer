# Tối ưu hóa Models cho Face Swapper

## Tổng quan

Dockerfile đã được tối ưu hóa để chỉ tải xuống các model cần thiết cho face_swapper thay vì tải tất cả models, giúp giảm đáng kể kích thước Docker image cho RunPod serverless.

## Các Models được tải xuống

### Model chính
- **face_swapper**: `inswapper_128_fp16` (model mặc định, hiệu suất cao)

### Models phụ thuộc
- **face_detector**: `retinaface` (phát hiện khuôn mặt)
- **face_landmarker**: `many` (định vị điểm mốc khuôn mặt)  
- **face_recognizer**: `arcface_w600k_r50` (nhận diện khuôn mặt)
- **face_classifier**: `opennsfw` (phân loại nội dung)
- **face_masker**: `bisenet` (tạo mask khuôn mặt)
- **content_analyser**: `open_clip` (phân tích nội dung)

## Scripts tải xuống

### 1. Script chính: `download_face_swapper_models.py`
- Tải xuống tất cả models cần thiết cho face_swapper
- Xử lý lỗi và retry logic
- Báo cáo tiến độ chi tiết

### 2. Script backup: `download_minimal_models.py`
- Chỉ tải 2 model cơ bản nhất: `inswapper_128_fp16` + `retinaface`
- Sử dụng khi cần giảm tối đa kích thước image

## Cách sử dụng

### Build Docker image
```bash
docker build -t facefusion-face-swapper .
```

### Thay đổi model face_swapper
Nếu muốn sử dụng model khác, sửa `default_model` trong `download_face_swapper_models.py`:

```python
{
    'module': 'facefusion.processors.modules.face_swapper',
    'model_key': 'face_swapper_model',
    'default_model': 'simswap_256'  # Thay đổi ở đây
}
```

### Các model face_swapper có sẵn
- `inswapper_128_fp16` (mặc định - nhẹ, nhanh)
- `inswapper_128` (phiên bản đầy đủ)
- `simswap_256` (chất lượng cao hơn)
- `ghost_1_256`, `ghost_2_256`, `ghost_3_256` (các phiên bản Ghost)
- `hyperswap_1a_256`, `hyperswap_1b_256`, `hyperswap_1c_256` (HyperSwap)
- `uniface_256` (Uniface)
- `blendswap_256` (BlendSwap)

## Lợi ích

### Giảm kích thước Docker image
- **Trước**: ~8-12GB (tất cả models)
- **Sau**: ~2-4GB (chỉ models cần thiết)

### Tăng tốc độ deployment
- Giảm thời gian tải xuống models
- Giảm thời gian khởi động container
- Tối ưu cho RunPod serverless

### Tiết kiệm tài nguyên
- Ít dung lượng lưu trữ
- Ít băng thông mạng
- Tiết kiệm chi phí cloud

## Troubleshooting

### Nếu script chính thất bại
```bash
# Thử script backup
python3 download_minimal_models.py
```

### Nếu model không tải được
1. Kiểm tra kết nối internet
2. Xem log lỗi chi tiết
3. Thử model khác trong danh sách

### Nếu face_swapper không hoạt động
1. Đảm bảo có đủ models phụ thuộc
2. Kiểm tra cấu hình CUDA
3. Xem log runtime 