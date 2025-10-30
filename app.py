from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from PIL import Image
import io
import os

app = FastAPI(title="YOLOv12 FastAPI GPU Service")

# Load model sẵn trên GPU
model = YOLO("yolo12n.pt")
print("Model loaded on:", model.device)

@app.get("/")
def root():
    return {"message": "YOLOv12 FastAPI is running!"}


@app.get("/predict")
def predict_from_path(image: str):
    """Dự đoán từ đường dẫn ảnh (ví dụ: /predict?image=test_images/food1.jpg)"""
    if not os.path.exists(image):
        return {"error": f"Image '{image}' not found"}

    img = Image.open(image)
    results = model.predict(
        source=img,
        device='cuda',
        save=True,
        save_dir='runs/detect/api',
        exist_ok=True
    )

    labels = [results[0].names[int(c)] for c in results[0].boxes.cls]
    return {"labels": labels}


@app.post("/predict")
async def predict_from_upload(file: UploadFile = File(...)):
    """Dự đoán từ ảnh upload"""
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    results = model.predict(
        source=img,
        device='cuda',
        save=True,
        save_dir='runs/detect/api_upload',
        exist_ok=True
    )

    labels = [results[0].names[int(c)] for c in results[0].boxes.cls]
    return {"labels": labels}
