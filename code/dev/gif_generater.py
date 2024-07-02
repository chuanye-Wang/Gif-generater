import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
from PIL import Image, ImageGrab
import imageio
import time
import threading

class GifRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Recorder")
        
        self.recording = False
        self.frames = []
        self.rect = None
        self.start_x = None
        self.start_y = None
        
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.start_button = tk.Button(root, text="开始", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT)
        
        self.stop_button = tk.Button(root, text="结束", command=self.stop_recording)
        self.stop_button.pack(side=tk.LEFT)
    
    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        pass
    
    def start_recording(self):
        if self.rect is None:
            messagebox.showwarning("没有框出录制窗口", "先画一个窗口兄弟")
            return
        
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.recording_area = (int(x1), int(y1), int(x2), int(y2))
        self.recording = True
        self.frames = []
        
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()
        
    def record(self):
        while self.recording:
            img = ImageGrab.grab(bbox=self.recording_area)
            self.frames.append(img)
            time.sleep(0.1)
    
    def stop_recording(self):
        self.recording = False
        self.recording_thread.join()
        
        output_file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF Files", "*.gif")])
        if not output_file:
            return 
        
        self.save_gif(output_file)
        messagebox.showinfo("GIF 已保存", f"GIF 的文件名为：{output_file}")
    
    def save_gif(self, output_file):
        imageio.mimsave(output_file, self.frames, format='GIF', duration=0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = GifRecorder(root)
    root.mainloop()