import sys
import cv2
import pyautogui
import numpy as np
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QComboBox, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap

class Canavar:
    def __init__(self, isim, resimler, olme_suresi):
        self.isim = isim
        self.resimler = resimler
        self.olme_suresi = olme_suresi  # Canavarın ölme süresi (saniye)

class FarmBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Farm Bot")
        self.setGeometry(100, 100, 600, 400)

        # Canavarlar
        self.canavar_list = [
            Canavar("Canavar1", ["C:/Users/canse/Desktop/Warspear/image/onyuz1.jpg", 
 "C:/Users/canse/Desktop/Warspear//image/sagyuz1.jpg", 
 "C:/Users/canse/Desktop/Warspear/image/solyuz1.jpg", 
 "C:/Users/canse/Desktop/Warspear/image/arkayuz1.jpg"]
, 5),
            # Daha fazla canavar ekleyebilirsiniz
        ]
        self.selected_canavar = None
        self.running = False
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Açıklama
        label = QLabel("Hangi canavarı öldürmek istiyorsunuz?")
        layout.addWidget(label)

        # Canavar Seçimi
        self.combo_box = QComboBox()
        for canavar in self.canavar_list:
            self.combo_box.addItem(canavar.isim)
        layout.addWidget(self.combo_box)

        # Resimlerin Görüntülenmesi
        self.image_labels = []
        for i in range(4):  # 4 adet resim kutusu ekliyoruz
            image_label = QLabel(self)
            layout.addWidget(image_label)
            self.image_labels.append(image_label)

        # Başlat Butonu
        start_button = QPushButton("Başlat")
        start_button.clicked.connect(self.start_bot)
        layout.addWidget(start_button)

        # Durdur Butonu
        stop_button = QPushButton("Durdur")
        stop_button.clicked.connect(self.stop_bot)
        layout.addWidget(stop_button)

        # Ana Widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_bot(self):
        selected_name = self.combo_box.currentText()
        self.selected_canavar = next((c for c in self.canavar_list if c.isim == selected_name), None)

        if not self.selected_canavar:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir canavar seçin!")
            return

        self.running = True
        self.show_images()
        self.run_bot()

    def stop_bot(self):
        self.running = False

    def show_images(self):
        for i, resim_yolu in enumerate(self.selected_canavar.resimler):
            # Resmi yükleyip QLabel'a gösterme
            canavar_resmi = QPixmap(resim_yolu)
            if canavar_resmi.isNull():
                self.image_labels[i].setText(f"Resim yüklenemedi: {self.selected_canavar.resimler[i]}")
            else:
                self.image_labels[i].setPixmap(canavar_resmi.scaled(100, 100))  # Resmi 100x100 boyutunda göster

    def run_bot(self):
        def ekran_goruntusu_al():
            ekran = pyautogui.screenshot()
            ekran_np = np.array(ekran)
            ekran_bgr = cv2.cvtColor(ekran_np, cv2.COLOR_RGB2BGR)
            return ekran_bgr

        def nesne_tespit_et(ekran, nesne_resmi, esik=0.8):
            sonuc = cv2.matchTemplate(ekran, nesne_resmi, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(sonuc)
            if max_val > esik:
                return max_loc
            return None

        def nesneye_tikla(pozisyon, nesne_resmi):
            x, y = pozisyon
            merkez_x = x + nesne_resmi.shape[1] // 2
            merkez_y = y + nesne_resmi.shape[0] // 2
            pyautogui.click(merkez_x, merkez_y)

        while self.running:
            ekran = ekran_goruntusu_al()

            # Canavarın tüm yüzlerini kontrol et
            for resim_yolu in self.selected_canavar.resimler:
                canavar_resmi = cv2.imread(resim_yolu)
                if canavar_resmi is None:
                    print(f"Resim bulunamadı: {resim_yolu}")
                    continue

                pozisyon = nesne_tespit_et(ekran, canavar_resmi)

                if pozisyon:
                    print(f"{self.selected_canavar.isim} bulundu. İşlem yapılıyor...")
                    start_time = time.time()
                    while time.time() - start_time < self.selected_canavar.olme_suresi:
                        nesneye_tikla(pozisyon, canavar_resmi)
                        time.sleep(0.2)

                    print(f"{self.selected_canavar.isim} öldürüldü, el işareti aranıyor.")
                    el_isareti_resmi = cv2.imread("C:\\Users\\canse\\Desktop\\Warspear\\image\\El.jpg")
                    pozisyon = nesne_tespit_et(ekran, el_isareti_resmi)
                    if pozisyon:
                        nesneye_tikla(pozisyon, el_isareti_resmi)
                        print("El işareti toplandı.")

                        # Çanta simgesine tıklama
                        cantaya_tikla_resmi = cv2.imread("C:\\Users\\canse\\Desktop\\Warspear\\image\\canta.jpg")
                        pozisyon_canta = nesne_tespit_et(ekran, cantaya_tikla_resmi)
                        if pozisyon_canta:
                            nesneye_tikla(pozisyon_canta, cantaya_tikla_resmi)
                            print("Çanta açıldı ve ganimet toplandı.")
                    break
            time.sleep(0.1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bot = FarmBot()
    bot.show()
    sys.exit(app.exec_())
