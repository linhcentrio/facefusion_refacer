#!/usr/bin/env python3
"""
RunPod Serverless Handler for FaceFusion Face Swap
"""

import runpod
import os
import tempfile
import uuid
import requests
import time
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path
from minio import Minio
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MinIO Configuration
MINIO_ENDPOINT = "108.181.198.160:9000"
MINIO_ACCESS_KEY = "a9TFRtBi8q3Nvj5P5Ris"
MINIO_SECRET_KEY = "fCFngM7YTr6jSkBKXZ9BkfDdXrStYXm43UGa0OZQ"
MINIO_BUCKET = "aiclipdfl"
MINIO_SECURE = False

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# FaceFusion configuration
FACEFUSION_PATH = "/facefusion"
FACEFUSION_PYTHON = f"{FACEFUSION_PATH}/venv/bin/python"
FACEFUSION_SCRIPT = f"{FACEFUSION_PATH}/facefusion.py"

# Supported face swapper models
FACE_SWAPPER_MODELS = [
    "uniface_256",
    "blendswap_256", 
    "ghost_256_unet_1",
    "deepinsight",
    "lightweight_swapper",
    "stylegan_swapper",
    "arcface_swapper",
    "unet_face_swapper"
]

def validate_face_swapper_model(model: str) -> str:
    """Validate and return face swapper model"""
    if model in FACE_SWAPPER_MODELS:
        return model
    logger.warning(f"Invalid face swapper model '{model}', defaulting to 'uniface_256'")
    return "uniface_256"

def download_file(url: str, local_path: str) -> bool:
    """Download file from URL with progress tracking"""
    try:
        logger.info(f"📥 Downloading {url}")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        logger.info(f"✅ Downloaded: {local_path} ({downloaded/1024/1024:.1f} MB)")
        return True
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def upload_to_minio(local_path: str, object_name: str) -> str:
    """Upload file to MinIO storage"""
    try:
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        minio_client.fput_object(MINIO_BUCKET, object_name, local_path)
        file_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{quote(object_name)}"
        logger.info(f"✅ Uploaded successfully: {file_url}")
        return file_url
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise e

def run_facefusion_faceswap(
    source_image_path: str,
    target_video_path: str,
    output_path: str,
    face_swapper_model: str = "uniface_256",
    pixel_boost: str = "1024x1024",
    output_quality: int = 100,
    output_resolution: str = "1920x1080",
    execution_threads: int = 8
) -> bool:
    """Run FaceFusion face swap command"""
    try:
        logger.info(f"🎭 Running FaceFusion face swap with model: {face_swapper_model}")
        
        # Validate model
        face_swapper_model = validate_face_swapper_model(face_swapper_model)
        
        # Build command
        cmd = [
            FACEFUSION_PYTHON,
            FACEFUSION_SCRIPT,
            "headless-run",
            "--processors", "face_swapper",
            "--face-swapper-model", face_swapper_model,
            "--face-swapper-pixel-boost", pixel_boost,
            "--output-video-quality", str(output_quality),
            "--output-video-resolution", output_resolution,
            "--execution-providers", "cuda",
            "--execution-thread-count", str(execution_threads),
            "-s", source_image_path,
            "-t", target_video_path,
            "-o", output_path
        ]
        
        logger.info(f"🚀 Command: {' '.join(cmd)}")
        
        # Run command
        result = subprocess.run(
            cmd,
            cwd=FACEFUSION_PATH,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"✅ Face swap completed successfully ({file_size:.1f} MB)")
                return True
            else:
                logger.error("❌ Face swap completed but output file not found")
                return False
        else:
            logger.error(f"❌ Face swap failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Face swap timed out (30 minutes)")
        return False
    except Exception as e:
        logger.error(f"❌ Face swap error: {e}")
        return False

def get_file_extension(url: str) -> str:
    """Get file extension from URL"""
    try:
        path = url.split('?')[0]  # Remove query parameters
        return Path(path).suffix.lower()
    except:
        return ""

def handler(job):
    """Main RunPod handler for FaceFusion face swap"""
    job_id = job.get("id", "unknown")
    start_time = time.time()
    
    try:
        job_input = job.get("input", {})
        source_image_url = job_input.get("source_image_url")
        target_video_url = job_input.get("target_video_url")
        
        if not source_image_url or not target_video_url:
            return {"error": "Missing source_image_url or target_video_url"}
        
        # Processing parameters
        face_swapper_model = job_input.get("face_swapper_model", "uniface_256")
        pixel_boost = job_input.get("pixel_boost", "1024x1024")
        output_quality = job_input.get("output_quality", 100)
        output_resolution = job_input.get("output_resolution", "1920x1080")
        execution_threads = job_input.get("execution_threads", 8)
        
        logger.info(f"🚀 Job {job_id}: FaceFusion Face Swap")
        logger.info(f"👤 Source: {source_image_url}")
        logger.info(f"🎬 Target: {target_video_url}")
        logger.info(f"🤖 Model: {face_swapper_model}")
        logger.info(f"⚙️ Settings: quality={output_quality}, resolution={output_resolution}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # File paths
            source_ext = get_file_extension(source_image_url) or '.jpg'
            target_ext = get_file_extension(target_video_url) or '.mp4'
            
            source_path = os.path.join(temp_dir, f"source{source_ext}")
            target_path = os.path.join(temp_dir, f"target{target_ext}")
            
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_dir, f"faceswap_{current_time}.mp4")
            
            # Step 1: Download input files
            logger.info("📥 Step 1/3: Downloading input files...")
            if not download_file(source_image_url, source_path):
                return {"error": "Failed to download source image"}
            
            if not download_file(target_video_url, target_path):
                return {"error": "Failed to download target video"}
            
            # Step 2: Run FaceFusion face swap
            logger.info("🎭 Step 2/3: Running FaceFusion face swap...")
            swap_success = run_facefusion_faceswap(
                source_path,
                target_path, 
                output_path,
                face_swapper_model,
                pixel_boost,
                output_quality,
                output_resolution,
                execution_threads
            )
            
            if not swap_success:
                return {"error": "Face swap processing failed"}
            
            if not os.path.exists(output_path):
                return {"error": "Face swap output not generated"}
            
            # Step 3: Upload result
            logger.info("📤 Step 3/3: Uploading result...")
            output_filename = f"faceswap_{face_swapper_model}_{job_id}_{uuid.uuid4().hex[:8]}.mp4"
            output_url = upload_to_minio(output_path, output_filename)
            
            processing_time = time.time() - start_time
            
            # Prepare response
            response = {
                "output_video_url": output_url,
                "processing_time_seconds": round(processing_time, 2),
                "face_swapper_model": face_swapper_model,
                "settings": {
                    "pixel_boost": pixel_boost,
                    "output_quality": output_quality,
                    "output_resolution": output_resolution,
                    "execution_threads": execution_threads
                },
                "status": "completed"
            }
            
            return response
            
    except Exception as e:
        logger.error(f"❌ Handler error: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "processing_time_seconds": round(time.time() - start_time, 2)
        }

if __name__ == "__main__":
    logger.info("🚀 Starting FaceFusion Face Swap Serverless Worker...")
    logger.info(f"🎭 FaceFusion Path: {FACEFUSION_PATH}")
    logger.info(f"🗄️ Storage: {MINIO_ENDPOINT}/{MINIO_BUCKET}")
    logger.info(f"🤖 Supported Models: {', '.join(FACE_SWAPPER_MODELS)}")
    
    # Verify environment
    try:
        import torch
        logger.info(f"🔥 PyTorch: {torch.__version__}")
        logger.info(f"⚡ CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"🎮 GPU: {torch.cuda.get_device_name()}")
            logger.info(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")
    except Exception as e:
        logger.warning(f"⚠️ Environment check failed: {e}")
    
    # Verify FaceFusion installation
    if os.path.exists(FACEFUSION_SCRIPT):
        logger.info("✅ FaceFusion installation verified")
    else:
        logger.error("❌ FaceFusion script not found")
        exit(1)
    
    # Start RunPod serverless worker
    logger.info("🎬 Ready to process face swap requests...")
    runpod.serverless.start({"handler": handler})
