import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Supported image extensions
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}


def select_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def rename_images(folder, theme):
    if not folder:
        messagebox.showerror("Error", "フォルダを指定してください")
        return
    if not theme:
        messagebox.showerror("Error", "テーマ名を入力してください")
        return

    theme = theme.replace(' ', '_')

    try:
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS]
    except FileNotFoundError:
        messagebox.showerror("Error", "フォルダが存在しません")
        return

    files.sort()
    total = len(files)
    if total == 0:
        messagebox.showinfo("Info", "対象ファイルがありません")
        return

    digits = max(2, len(str(total)))
    count = 0
    for idx, filename in enumerate(files, start=1):
        old_path = os.path.join(folder, filename)
        _, ext = os.path.splitext(filename)
        new_name = f"{theme}_{str(idx).zfill(digits)}{ext}"
        new_path = os.path.join(folder, new_name)
        try:
            os.rename(old_path, new_path)
            count += 1
        except OSError as e:
            messagebox.showerror("Error", f"{filename} のリネームに失敗しました: {e}")
            return

    messagebox.showinfo("Success", f"{count} 件のファイルをリネームしました")


def main():
    root = tk.Tk()
    root.title("画像リネームツール")

    tk.Label(root, text="フォルダ").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    folder_entry = tk.Entry(root, width=40)
    folder_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="参照", command=lambda: select_folder(folder_entry)).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="テーマ名").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    theme_entry = tk.Entry(root, width=40)
    theme_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(root, text="リネーム実行", command=lambda: rename_images(folder_entry.get(), theme_entry.get())).grid(row=2, column=1, pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
