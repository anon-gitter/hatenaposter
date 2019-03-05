import tkinter as tk
import os
from  postblog import *
import tooltip
import threading
import textredirector
import sys
from datetime import datetime
from tkinter import filedialog # for pyinstaller
from tkinter import messagebox # for pyinstaller
from tkinter import scrolledtext

config_file = "hatenaposterConfig.txt"

class HatenaposterUI(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('はてなポスター')
        self.drawgui()
        self.hatenaposter = Hatenaposter()
        
    def drawgui(self):

        # Frame as Widget Container
        frame1 = tk.Frame(self, bg='white')
        frame1.grid()

        frame_button = tk.Frame(frame1, bg='white')
        frame_button.pack(side = 'top', anchor='w', padx=5, pady=5)

        frame_text = tk.LabelFrame(frame1, text='Log', bg='white')
        frame_text.pack(side = 'bottom')

        # Setting button
        self.settingicon = tk.PhotoImage(file='settings.png')
        button_setting = tk.Button(
            frame_button,
            image=self.settingicon,
            command=self.settings,
            bg='white')
        button_setting.pack(fill = 'none', side = 'left', anchor = 'w')
        tooltip.Tooltip(button_setting, text='設定', wraplength=200)

        # Nowexec button
        self.nowexecicon = tk.PhotoImage(file='nowexec.png')

        button_nowexec = tk.Button(
            frame_button,
            image=self.nowexecicon,
            command=self.nowexec,
            bg='white')
        button_nowexec.pack(fill = 'none', side = 'left')
        tooltip.Tooltip(button_nowexec, text='本日分を送信', wraplength=200)

        # Image up button
        self.imgposticon = tk.PhotoImage(file='imgpost.png')

        button_imgpost = tk.Button(
            frame_button,
            image=self.imgposticon,
            command=self.imgpost,
            bg='white')
        button_imgpost.pack(fill = 'none', side = 'left')
        tooltip.Tooltip(button_imgpost, text='画像を指定して送信', wraplength=200)

        # specify date button
        self.dateicon = tk.PhotoImage(file='time.png')

        button_date = tk.Button(
            frame_button,
            image=self.dateicon,
            command=self.imgpost_bydate,
            bg='white')
        button_date.pack(fill = 'none', side = 'left')
        tooltip.Tooltip(button_date, text='日付を指定して送信', wraplength=200)

        # send all images which name contains date
        self.sendallicon = tk.PhotoImage(file='sendallfile.png')

        button_sendall = tk.Button(
            frame_button,
            image=self.sendallicon,
            command=self.imgpost_allfiles,
            bg='white')
        button_sendall.pack(fill = 'none', side = 'left')
        tooltip.Tooltip(button_sendall, text='すべてのファイルを送信', wraplength=200)

        # Textbox
        log_box = tk.scrolledtext.ScrolledText(frame_text,width=40, height=10, bg='white')
        log_box.see(tk.END)
        log_box.pack()
        sys.stdout = textredirector.TextRedirector(log_box, "stdout")
        sys.stderr = textredirector.TextRedirector(log_box, "stderr")

    def nowexec(self):
        ret = messagebox.askquestion('画像アップロード手動実行','いますぐ画像アップロードしますか？')
        if (ret=='yes'):
            if self.hatenaposter.check_config():
                threading.Thread(target=self.hatenaposter.hatenaposter).start()
            else:
                messagebox.showerror('エラー','設定に誤りがあるか、未設定です')

    def imgpost(self):
        filename = filedialog.askopenfilename()
        if filename == "":
            return
        ret = messagebox.askquestion('画像アップロード手動実行','いますぐ指定の画像をアップロードしますか？')
        if ret=='yes':
            if self.hatenaposter.check_config():
                threading.Thread(target=self.hatenaposter.hatenaposter, args=(filename, None,) ).start()
            else:
                messagebox.showerror('エラー','設定に誤りがあるか、未設定です')

    def imgpost_bydate(self):
        # ダイアログで日付を指定
        postbydateframe = tk.Toplevel(bg='white')
        postbydateframe.geometry('220x100')
        postbydateframe.title('日付指定送信')
        date_frame = tk.Frame(postbydateframe)
        year = tk.IntVar()
        year.set(datetime.now().year)
        yearBox = tk.Spinbox(date_frame, from_ = 00, to = 9999, increment = 1, width = 4,
                             format='%4.0f', textvariable = year)
        yearBox.pack(side='left')
        yearLabel = tk.Label(date_frame, text='年', bg='white')
        yearLabel.pack(side='left')
        month=tk.IntVar()
        month.set(datetime.now().month)
        monthBox = tk.Spinbox(date_frame, from_ = 1, to = 12, increment = 1, width = 2,
                              textvariable = month)
        monthBox.pack(side='left')
        monthLabel = tk.Label(date_frame, text='月', bg='white')
        monthLabel.pack(side='left')
        day=tk.IntVar()
        day.set(datetime.now().day)
        dayBox = tk.Spinbox(date_frame, from_ = 1, to = 31, increment = 1, width = 2,
                            textvariable = day)
        dayBox.pack(side='left')
        dayLabel = tk.Label(date_frame, text='日', bg='white')
        dayLabel.pack(side='left')
        button_frame = tk.Frame(postbydateframe)
        sendButton = tk.Button(button_frame, text='送信', bg='white',
                               command=lambda d=(year, month, day, postbydateframe):self.postbydate_exec(d))
        sendButton.pack(side='bottom')
        date_frame.pack(side='top', padx=20, pady=20)
        button_frame.pack(side='bottom')
        
    def postbydate_exec(self, d):
        date = datetime(d[0].get(), d[1].get(), d[2].get())
        self.destroy_frame(d[3])
        ret = messagebox.askquestion('日付指定画像アップロード実行','いますぐ画像をアップロードしますか？')
        if ret=='yes':
            if self.hatenaposter.check_config():
                threading.Thread(target=self.hatenaposter.hatenaposter, args=(None, date,)).start()
            else:
                messagebox.showerror('エラー','設定に誤りがあるか、未設定です')

    def imgpost_allfiles(self):
        ret = messagebox.askquestion('全画像ファイルアップロード実行','いますぐ全画像をアップロードしますか？')
        if ret=='yes':
            if self.hatenaposter.check_config():
                threading.Thread(target=self.hatenaposter.sendall).start()
            else:
                messagebox.showerror('エラー','設定に誤りがあるか、未設定です')

    def destroy_frame(self, frame):
        frame.destroy()

    def read_settings(self, array):
        self.hatenaposter.write_config(array[0].get(),
                                array[1].get(),
                                array[2].get(),
                                array[3].get(),
                                'yes' if array[4].get()==True else 'no')
        self.destroy_frame(array[5])

    def select_config(self, entry):
        filename = filedialog.askdirectory()
        if filename != "":
            entry.delete(0,tk.END)
            entry.insert(tk.END, filename)

    def settings(self):
        '''TODO:スレッド実行中か確認'''
        
        apikey = base_directory = username = blogname = draft = None

        # ファイルの読み出しを追加
        if os.path.exists('hatenaposterConfig.txt'):
            apikey, base_directory, username, blogname, draft = self.hatenaposter.read_config()
        
        setting_frame = tk.Toplevel(bg='white')
        setting_frame.geometry('500x170')
        setting_frame.title('はてなポスター設定')
        label_file = tk.Label(setting_frame, text='対象ディレクトリ', bg='white')
        label_file.grid(column=1,row=1,sticky=tk.W)

        entry_file = tk.Entry(setting_frame,width=45)
        entry_file.grid(column=2,row=1)
        if base_directory is not None:
            entry_file.delete(0,tk.END)
            entry_file.insert(tk.END,base_directory)

        button_file = tk.Button(setting_frame, text='open', bg='white',
                                command=lambda e=entry_file : self.select_config(e))
        button_file.grid(column=3,row=1,sticky=tk.W)

        label_apikey = tk.Label(setting_frame, text='APIキー', bg='white')
        label_apikey.grid(column=1,row=2,sticky=tk.W)

        entry_apikey = tk.Entry(setting_frame,width=45)
        entry_apikey.grid(column=2,row=2)
        if apikey != None:
            entry_apikey.delete(0,tk.END)
            entry_apikey.insert(tk.END,apikey)

        label_username = tk.Label(setting_frame, text='ユーザー名', bg='white')
        label_username.grid(column=1,row=3,sticky=tk.W)

        entry_username = tk.Entry(setting_frame,width=45)
        entry_username.grid(column=2,row=3)
        if username != None:
            entry_username.delete(0,tk.END)
            entry_username.insert(tk.END,username)

        label_blogname = tk.Label(setting_frame, text='ブログ名', bg='white')
        label_blogname.grid(column=1,row=4,sticky=tk.W)

        entry_blogname = tk.Entry(setting_frame,width=45)
        entry_blogname.grid(column=2,row=4)
        if blogname != None:
            entry_blogname.delete(0,tk.END)
            entry_blogname.insert(tk.END,blogname)

        var = tk.IntVar()
        checkbutton_draft = tk.Checkbutton(setting_frame, text='ドラフト指定送信', variable=var, bg='white')
        checkbutton_draft.grid(column=1, row=5, columnspan=2,sticky=tk.W)
        var.set(True if draft == 'yes' else False)

        button_cancel = tk.Button(setting_frame, text='cancel', bg='white',
                                  command=lambda w=setting_frame:self.destroy_frame(w))
        button_cancel.grid(column=2,row=6)

        settings_array = [entry_apikey,
                          entry_file,
                          entry_username,
                          entry_blogname,
                          var,
                          setting_frame]

        button_ok = tk.Button(setting_frame, text='OK', bg='white',
                              command=lambda array=settings_array : self.read_settings(array))
        button_ok.grid(column=1,row=6)
        setting_frame.grab_set()
        setting_frame.focus_set()

if __name__ == '__main__':

    root = HatenaposterUI()
    root.mainloop()

