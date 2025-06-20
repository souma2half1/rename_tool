import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Supported image extensions
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}


def select_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def rename_folder(folder: str, theme: str) -> int:
    """Rename images in *folder* using *theme* and return renamed count."""
    try:
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS]
    except FileNotFoundError:
        return 0

    files.sort()
    total = len(files)
    if total == 0:
        return 0

    digits = max(2, len(str(total)))
    count = 0
    for idx, filename in enumerate(files, start=1):
        old_path = os.path.join(folder, filename)
        _, ext = os.path.splitext(filename)
        new_name = f"{theme}_{str(idx).zfill(digits)}{ext}"
        new_path = os.path.join(folder, new_name)
        if old_path == new_path or os.path.exists(new_path):
            # Skip if the new file already exists or name is unchanged
            continue
        try:
            os.rename(old_path, new_path)
            count += 1
        except OSError:
            # Ignore rename errors for individual files
            continue

    return count


def rename_images(folder, theme):
    if not folder:
        messagebox.showerror("Error", "フォルダを指定してください")
        return
    if not theme:
        messagebox.showerror("Error", "テーマ名を入力してください")
        return

    theme = theme.replace(' ', '_')

    count = rename_folder(folder, theme)
    if count == 0:
        messagebox.showinfo("Info", "対象ファイルがありません")
    else:
        messagebox.showinfo("Success", f"{count} 件のファイルをリネームしました")


def auto_rename(root_folder):
    if not root_folder:
        messagebox.showerror("Error", "フォルダを指定してください")
        return

    if not os.path.isdir(root_folder):
        messagebox.showerror("Error", "フォルダが存在しません")
        return

    total = 0
    for dirpath, dirnames, _ in os.walk(root_folder):
        if dirpath == root_folder:
            continue  # skip root folder itself
        theme = os.path.basename(dirpath)
        total += rename_folder(dirpath, theme)

    if total == 0:
        messagebox.showinfo("Info", "リネーム対象のファイルがありません")
    else:
        messagebox.showinfo("Success", f"{total} 件のファイルをリネームしました")


def main():
    root = tk.Tk()
    root.title("画像リネームツール")
    root.resizable(False, False)
    root.option_add("*Font", ("Arial", 10))

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="フォルダ").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    folder_entry = ttk.Entry(frame, width=45)
    folder_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(frame, text="参照", command=lambda: select_folder(folder_entry)).grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(frame, text="テーマ名").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    theme_entry = ttk.Entry(frame, width=45)
    theme_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(frame, text="リネーム実行", command=lambda: rename_images(folder_entry.get(), theme_entry.get())).grid(row=2, column=1, pady=5)
    ttk.Button(frame, text="オートリネーム", command=lambda: auto_rename(folder_entry.get())).grid(row=3, column=1, pady=5)

    root.mainloop()


if __name__ == '__main__':
    main()
