import numpy as np
import cv2
import board
import neopixel
from CameraManager.camera_manager import CameraManager

class ProcessaImagem:
    def __init__(self, camera, capturar_fundo=True, fundo_referencia=None):
        self.camera = camera
        self.fundo_referencia = None
        self.kernel = np.ones((3, 3), "uint8")
        self.roi_x, self.roi_y, self.roi_w, self.roi_h = 80, 50, 220, 180

        self.pixels = neopixel.NeoPixel(board.D18, 12)
        self.leds_acesos = False
        self.ultima_cor_detectada = ""

        self.threshold_preto = 40
        self.threshold_cromado = 20
        self.threshold_transparente = 30

        if fundo_referencia is not None:
            self.fundo_referencia = fundo_referencia
        elif capturar_fundo:
            self._captura_fundo()

        self.pixels.fill((255, 255, 255))
        self.leds_acesos = True

    def atualizar_thresholds(self, preto, cromado, transparente):
        self.threshold_preto = preto
        self.threshold_cromado = cromado
        self.threshold_transparente = transparente

    def _captura_fundo(self):
        for _ in range(10):
            frame = self.camera.get_frame()
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.fundo_referencia = gray
       

    def get_frame(self):
        if self.fundo_referencia is None:
            return None
        frame = self.camera.get_frame()
        if frame is None:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.ultima_cor_detectada = ""

        # DETECÇÃO VERMELHO
        red_lower = np.array([136, 87, 111], np.uint8)
        red_upper = np.array([180, 255, 255], np.uint8)
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        red_mask = cv2.dilate(red_mask, self.kernel, iterations=1)
        contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours_red:
            area = cv2.contourArea(contour)
            if area > 3000:
                x, y, w, h = cv2.boundingRect(contour)
                if self._dentro_roi(x, y, w, h):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "Red Colour", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    self.ultima_cor_detectada = "Vermelho"
                    return frame

        # DETECÇÃO PRETO
        diff = cv2.absdiff(self.fundo_referencia, gray)
        _, diff_thresh = cv2.threshold(diff, self.threshold_preto, 255, cv2.THRESH_BINARY)
        diff_thresh = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, self.kernel)
        diff_thresh = cv2.dilate(diff_thresh, self.kernel, iterations=2)

        black_lower = np.array([0, 0, 0], np.uint8)
        black_upper = np.array([180, 255, 90], np.uint8)
        black_mask = cv2.inRange(hsv, black_lower, black_upper)
        objeto_preto = cv2.bitwise_and(diff_thresh, black_mask)
        contours_black, _ = cv2.findContours(objeto_preto, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours_black:
            area = cv2.contourArea(contour)
            if area > 3000:
                x, y, w, h = cv2.boundingRect(contour)
                if self._dentro_roi(x, y, w, h):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
                    cv2.putText(frame, "Black Color", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    self.ultima_cor_detectada = "Preto"
                    return frame

        # DETECÇÃO CROMADO
        _, diff_thresh = cv2.threshold(cv2.absdiff(self.fundo_referencia, gray), self.threshold_cromado, 255, cv2.THRESH_BINARY)
        diff_thresh = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, self.kernel)
        diff_thresh = cv2.dilate(diff_thresh, self.kernel, iterations=2)

        chrome_lower = np.array([0, 0, 180], np.uint8)
        chrome_upper = np.array([180, 60, 225], np.uint8)
        chrome_mask = cv2.inRange(hsv, chrome_lower, chrome_upper)
        objeto_chrome = cv2.bitwise_and(diff_thresh, chrome_mask)
        contours_chrome, _ = cv2.findContours(objeto_chrome, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours_chrome:
            area = cv2.contourArea(contour)
            if area > 3000:
                x, y, w, h = cv2.boundingRect(contour)
                if self._dentro_roi(x, y, w, h):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (128, 128, 128), 2)
                    cv2.putText(frame, "Chrome Color", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                    self.ultima_cor_detectada = "Cromado"
                    return frame

        # DETECÇÃO TRANSPARENTE
        _, diff_thresh = cv2.threshold(cv2.absdiff(self.fundo_referencia, gray), self.threshold_transparente, 255, cv2.THRESH_BINARY)
        diff_thresh = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, self.kernel)
        diff_thresh = cv2.dilate(diff_thresh, self.kernel, iterations=2)

        contours_transparent, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours_transparent:
            area = cv2.contourArea(contour)
            if area > 3000:
                x, y, w, h = cv2.boundingRect(contour)
                if self._dentro_roi(x, y, w, h):
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.putText(frame, "Transparent?", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    self.ultima_cor_detectada = "Transparente"
                    return frame

        return frame

    def _dentro_roi(self, x, y, w, h):
        return (
            x >= self.roi_x and y >= self.roi_y and
            x + w <= self.roi_x + self.roi_w and
            y + h <= self.roi_y + self.roi_h
        )

    def release(self):
        pass
