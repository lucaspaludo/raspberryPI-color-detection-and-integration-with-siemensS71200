import cv2

class CameraManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, camera_index=0):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.camera_index = camera_index
            self.cap = None
            self._open_camera()

    def _open_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            self._open_camera()
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            CameraManager._instance = None
