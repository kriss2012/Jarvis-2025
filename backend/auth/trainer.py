"""
Face recognition and authentication module
Uses OpenCV and face recognition for user authentication
"""

import cv2
import numpy as np
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_recognizer():
    """
    Initialize face recognizer with support for multiple OpenCV versions
    
    Returns:
        Tuple of (recognizer, detector) or (None, None) if initialization fails
    """
    try:
        # Try to get face module from opencv-contrib-python
        face_module = getattr(cv2, 'face', None)
        
        recognizer = None
        if face_module is not None:
            # Try recent API first
            creator = getattr(face_module, 'LBPHFaceRecognizer_create', None)
            if creator is None:
                # Try older API
                creator = getattr(face_module, 'createLBPHFaceRecognizer', None)
            
            if creator:
                recognizer = creator()
        else:
            # Try very old API
            creator = getattr(cv2, 'createLBPHFaceRecognizer', None)
            if creator:
                recognizer = creator()
        
        if recognizer is None:
            raise ImportError(
                "LBPHFaceRecognizer not found. "
                "Please install: pip install opencv-contrib-python"
            )
        
        # Load the trained model if it exists
        trainer_path = Path("backend/auth/trainer/trainer.yml")
        if trainer_path.exists():
            recognizer.read(str(trainer_path))
            logger.info("Loaded trained face recognition model")
        else:
            logger.warning("Trained model not found. Please train first.")
        
        # Load Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(cascade_path)
        
        if detector.empty():
            logger.error("Could not load Haar Cascade classifier")
            return None, None
        
        logger.info("Face recognizer initialized successfully")
        return recognizer, detector
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Error initializing recognizer: {str(e)}", exc_info=True)
        return None, None


def AuthenticateFace() -> int:
    """
    Authenticate user by recognizing their face
    
    Returns:
        1 if face recognized, 0 if not recognized, -1 if error
    """
    recognizer, detector = initialize_recognizer()
    
    if recognizer is None or detector is None:
        logger.error("Could not initialize face recognizer")
        return -1
    
    try:
        # Initialize webcam
        cam = cv2.VideoCapture(0)
        
        if not cam.isOpened():
            logger.error("Could not access webcam")
            return -1
        
        logger.info("Starting face authentication...")
        
        # Confidence threshold (lower is more confident)
        confidence_threshold = 45
        
        while True:
            ret, img = cam.read()
            
            if not ret:
                logger.error("Failed to read frame from webcam")
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Recognize face
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                
                # Add text to image
                confidence_text = f"Confidence: {round(100-confidence, 2)}%"
                cv2.putText(img, confidence_text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                logger.info(f"Face detected - ID: {id}, Confidence: {confidence}")
                
                # Check if confidence is above threshold
                if confidence < confidence_threshold:
                    logger.info(f"Face recognized with high confidence")
                    cam.release()
                    cv2.destroyAllWindows()
                    return 1
            
            # Display the frame
            cv2.imshow('Face Authentication', img)
            
            # Break on ESC or timeout
            if cv2.waitKey(10) & 0xFF == 27:
                logger.info("Face authentication cancelled by user")
                break
        
        cam.release()
        cv2.destroyAllWindows()
        logger.warning("No face recognized")
        return 0
        
    except Exception as e:
        logger.error(f"Error in face authentication: {str(e)}", exc_info=True)
        return -1


def CaptureImages(id: int, num_images: int = 30) -> bool:
    """
    Capture training images for face recognition
    
    Args:
        id: User ID number
        num_images: Number of images to capture (default: 30)
        
    Returns:
        True if successful, False otherwise
    """
    _, detector = initialize_recognizer()
    
    if detector is None:
        logger.error("Could not initialize face detector")
        return False
    
    try:
        # Create directory for samples if it doesn't exist
        sample_path = Path(f"backend/auth/samples")
        sample_path.mkdir(parents=True, exist_ok=True)
        
        cam = cv2.VideoCapture(0)
        
        if not cam.isOpened():
            logger.error("Could not access webcam")
            return False
        
        logger.info(f"Capturing {num_images} images for user {id}...")
        count = 0
        
        while True:
            ret, img = cam.read()
            
            if not ret:
                logger.error("Failed to read frame")
                break
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1
                
                # Save the image
                img_name = f"{sample_path}/User.{id}.{count}.jpg"
                cv2.imwrite(img_name, gray[y:y+h, x:x+w])
                
                cv2.putText(img, f"Images: {count}/{num_images}", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                logger.info(f"Captured image {count}/{num_images}")
            
            cv2.imshow('Capturing Images', img)
            
            if cv2.waitKey(100) & 0xFF == 27 or count >= num_images:
                break
        
        cam.release()
        cv2.destroyAllWindows()
        logger.info(f"Completed capturing {count} images")
        return True
        
    except Exception as e:
        logger.error(f"Error capturing images: {str(e)}", exc_info=True)
        return False


def TrainModel() -> bool:
    """
    Train the face recognition model using captured images
    
    Returns:
        True if training successful, False otherwise
    """
    from PIL import Image
    
    try:
        path = Path("backend/auth/samples")
        
        if not path.exists():
            logger.error("Sample directory not found")
            return False
        
        recognizer, detector = initialize_recognizer()
        
        if recognizer is None:
            logger.error("Could not initialize recognizer")
            return False
        
        logger.info("Training face recognition model...")
        
        face_samples = []
        ids = []
        
        # Load images from samples directory
        for imageName in os.listdir(path):
            imagePath = path / imageName
            
            try:
                # Convert to grayscale
                gray_img = Image.open(imagePath).convert('L')
                img_numpy = np.array(gray_img, 'uint8')
                
                # Extract ID from filename
                id = int(os.path.split(imagePath)[-1].split(".")[1])
                
                # Detect faces
                faces = detector.detectMultiScale(img_numpy)
                
                for (x, y, w, h) in faces:
                    face_samples.append(img_numpy[y:y+h, x:x+w])
                    ids.append(id)
                    
            except Exception as e:
                logger.warning(f"Error processing {imageName}: {str(e)}")
                continue
        
        if not face_samples:
            logger.error("No face samples found")
            return False
        
        # Train the recognizer
        logger.info(f"Training with {len(face_samples)} samples...")
        recognizer.train(face_samples, np.array(ids))
        
        # Save trained model
        trainer_path = Path("backend/auth/trainer")
        trainer_path.mkdir(parents=True, exist_ok=True)
        
        model_file = trainer_path / "trainer.yml"
        recognizer.write(str(model_file))
        
        logger.info("Model trained and saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}", exc_info=True)
        return False