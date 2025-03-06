import customtkinter as ctk
import threading
import os
from yt_dlp import YoutubeDL
from tkinter import messagebox
import time

# Customtkinter 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeMP3Downloader:
    def __init__(self, root):
        self.root = root
        self.root.title("유튜브 MP3 다운로더")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # 메인 프레임
        self.main_frame = ctk.CTkFrame(root, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 제목 라벨
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="유튜브 MP3 다운로더",
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(pady=(20, 10))

        # URL 입력
        self.url_label = ctk.CTkLabel(self.main_frame, text="유튜브 URL:")
        self.url_label.pack(pady=(10, 5))
        self.url_entry = ctk.CTkEntry(self.main_frame, width=400, placeholder_text="유튜브 URL을 입력하세요")
        self.url_entry.pack()

        # 저장 경로 선택
        self.path_label = ctk.CTkLabel(self.main_frame, text="저장 경로:")
        self.path_label.pack(pady=(10, 5))
        self.path_entry = ctk.CTkEntry(self.main_frame, width=400, placeholder_text="기본: 현재 폴더")
        self.path_entry.pack()

        # 다운로드 버튼
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="MP3 다운로드",
            command=self.start_download,
            fg_color="#FF0000",  # 유튜브 레드
            hover_color="#CC0000"
        )
        self.download_button.pack(pady=20)

        # 진행률 바
        self.progress = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # 상태 라벨
        self.status_label = ctk.CTkLabel(self.main_frame, text="상태: 대기 중")
        self.status_label.pack(pady=5)

    def download_mp3(self, url, path):
        """유튜브 영상을 MP3로 다운로드 (yt-dlp 사용)"""
        try:
            self.status_label.configure(text="상태: 다운로드 시작")
            self.download_button.configure(state="disabled")

            # 저장 경로 설정
            save_path = path if path else os.getcwd()
            output_template = os.path.join(save_path, "%(title)s.%(ext)s")

            # yt-dlp 옵션 설정
            ydl_opts = {
                'format': 'bestaudio/best',  # 최고 품질 오디오 선택
                'outtmpl': output_template,  # 출력 파일 이름 템플릿
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',  # 오디오 추출
                    'preferredcodec': 'mp3',      # MP3 포맷
                    'preferredquality': '192',    # 음질 (192kbps)
                }],
                'quiet': True,  # 불필요한 로그 출력 방지
            }

            # 다운로드 실행
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                mp3_file = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

            # 진행률 시뮬레이션 (실제 진행률은 콜백으로 개선 가능)
            for i in range(101):
                self.progress.set(i / 100)
                self.root.update()
                time.sleep(0.02)

            self.status_label.configure(text="상태: 다운로드 완료!")
            messagebox.showinfo("성공", f"MP3 다운로드 완료!\n파일: {mp3_file}")

        except Exception as e:
            self.status_label.configure(text=f"상태: 오류 발생")
            messagebox.showerror("오류", f"다운로드 실패: {str(e)}")

        finally:
            self.download_button.configure(state="normal")

    def start_download(self):
        url = self.url_entry.get()
        path = self.path_entry.get()

        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요!")
            return

        download_thread = threading.Thread(target=self.download_mp3, args=(url, path))
        download_thread.start()

def main():
    root = ctk.CTk()
    app = YouTubeMP3Downloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()