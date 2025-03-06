import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLineEdit, QPushButton, QProgressBar, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from yt_dlp import YoutubeDL
from pathlib import Path
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 다운로드 작업을 위한 워커 클래스
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.download_dir = Path.home() / "Downloads"

    def run(self):
        try:
            self.download_dir.mkdir(exist_ok=True)
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'merge_output_format': 'mp4',
                'quiet': True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit("다운로드 완료!")
        except Exception as e:
            logger.error(f"다운로드 실패: {str(e)}")
            self.error.emit(f"에러: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int((downloaded / total) * 100)
                self.progress.emit(percent)

# 메인 윈도우
class DownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grok Video Downloader")
        self.setFixedSize(500, 200)
        self.setup_ui()
        self.worker = None

    def setup_ui(self):
        # 위젯 설정
        container = QWidget()
        layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("동영상 URL을 입력하세요 (YouTube, etc.)")
        self.url_input.setStyleSheet("padding: 8px; font-size: 14px;")
        
        self.download_btn = QPushButton("다운로드")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.download_btn.clicked.connect(self.start_download)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.status_label = QLabel("상태: 준비")
        self.status_label.setAlignment(Qt.AlignCenter)

        # 레이아웃에 추가
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def validate_url(self, url):
        # 간단한 URL 유효성 검사
        pattern = r'^(https?://)?(www\.)?[\w-]+\.\w+'
        return bool(re.match(pattern, url))

    def start_download(self):
        url = self.url_input.text().strip()
        if not self.validate_url(url):
            self.status_label.setText("상태: 유효한 URL을 입력하세요")
            return
        
        self.download_btn.setEnabled(False)
        self.status_label.setText("상태: 다운로드 중...")
        self.progress_bar.setValue(0)

        # 워커 스레드 시작
        self.worker = DownloadWorker(url)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)
        self.worker.start()

    def update_progress(self, percent):
        self.progress_bar.setValue(percent)

    def download_finished(self, message):
        self.status_label.setText(f"상태: {message}")
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(100)

    def download_error(self, message):
        self.status_label.setText(f"상태: {message}")
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(0)

# 애플리케이션 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())