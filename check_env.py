import torch
import cv2
import numpy as np
import sys

def main():
    print("="*50)
    print("DEEPFAKE DETECTION PLATFORM - ENVIRONMENT CHECK")
    print("="*50)
    print(f"Python Version: {sys.version.split(' ')[0]}")
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"NumPy Version: {np.__version__}")
    print(f"PyTorch Version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version (PyTorch built with): {torch.version.cuda}")
    else:
        print("\nWARNING: CUDA is not available. Training will use CPU.")
        print("If you have an NVIDIA GPU, ensure drivers and PyTorch-CUDA are installed correctly.")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred during verification: {e}")
