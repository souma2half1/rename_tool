import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Supported image extensions
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}


def normalize_theme(theme: str) -> str:
    """Return a filesystem-friendly theme string."""
    theme = theme.strip()
    if not theme:
        return ""
    # Collapse any whitespace into underscores and remove repeated underscores
    theme = re.sub(r"\s+", "_", theme)
    theme = re.sub(r"_+", "_", theme)
    return theme


def _paths_refer_to_same_file(path_a: str, path_b: str) -> bool:
    """Return True if *path_a* and *path_b* point to the same file.

    ``os.path.samefile`` is not always available (or may raise ``OSError``) on
    some platforms, so we guard the call and fall back to a conservative
    comparison that still works for the case-insensitive file systems we care
    about (e.g. Windows)."""

    try:
        return os.path.samefile(path_a, path_b)
    except (OSError, AttributeError):
        return os.path.normcase(os.path.abspath(path_a)) == os.path.normcase(
            os.path.abspath(path_b)
        )


def _should_rename(old_path: str, new_path: str) -> bool:
    """Return True if *old_path* can safely be renamed to *new_path*."""

    if old_path == new_path:
        return False

    if not os.path.exists(new_path):
        return True

    return _paths_refer_to_same_file(old_path, new_path)


def build_rename_plan(folder: str, theme: str, start_index: int = 1):
    """Return rename plan for files in *folder* using *theme* from *start_index*."""
    theme = normalize_theme(theme)
    if not theme:
        return []
    try:
        files = [
            f
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS
        ]
    except FileNotFoundError:
        return []

    files.sort()
    total = len(files)
    if total == 0:
        return []

    digits = max(2, len(str(start_index + total - 1)))
    plan = []
    for idx, filename in enumerate(files, start=start_index):
        old_path = os.path.join(folder, filename)
        _, ext = os.path.splitext(filename)
        new_name = f"{theme}_{str(idx).zfill(digits)}{ext}"
        new_path = os.path.join(folder, new_name)
        will_rename = _should_rename(old_path, new_path)
        plan.append((old_path, new_path, filename, new_name, will_rename))
    return plan


def select_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def rename_folder(folder: str, theme: str, start_index: int = 1) -> int:
    """Rename images in *folder* using *theme* and return renamed count."""
    count = 0
    for old_path, new_path, _, _, will_rename in build_rename_plan(folder, theme, start_index):
        if not will_rename:
            continue
        try:
            os.rename(old_path, new_path)
            count += 1
        except OSError:
            # Ignore rename errors for individual files
            continue

    return count


def rename_images(folder, theme, start_index):
    if not folder:
        messagebox.showerror("Error", "フォルダを指定してください")
        return
    if not theme:
        messagebox.showerror("Error", "テーマ名を入力してください")
        return

    theme = normalize_theme(theme)
    if not theme:
        messagebox.showerror("Error", "テーマ名を入力してください")
        return
    if start_index < 1:
        messagebox.showerror("Error", "開始番号は1以上を指定してください")
        return

    count = rename_folder(folder, theme, start_index)
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


class RenameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像リネームツール")
        self.root.resizable(False, False)
        self.root.option_add("*Font", ("Arial", 10))

        self.folder_var = tk.StringVar()
        self.theme_var = tk.StringVar()
        self.start_var = tk.IntVar(value=1)
        self.status_var = tk.StringVar(value="フォルダを選択してプレビューを確認してください")

        self.theme_var.trace_add("write", lambda *_: self.update_preview())
        self.start_var.trace_add("write", lambda *_: self.update_preview())

        self.build_ui()
        self.update_preview()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")

        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="フォルダ").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        folder_entry = ttk.Entry(frame, textvariable=self.folder_var, width=45)
        folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(frame, text="参照", command=lambda: self.handle_select_folder(folder_entry)).grid(
            row=0, column=2, padx=5, pady=5
        )

        ttk.Label(frame, text="テーマ名").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        theme_entry = ttk.Entry(frame, textvariable=self.theme_var, width=45)
        theme_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        ttk.Label(frame, text="開始番号").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        start_spin = ttk.Spinbox(frame, from_=1, to=9999, textvariable=self.start_var, width=10)
        start_spin.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame, text="プレビュー").grid(row=3, column=0, padx=5, pady=(10, 5), sticky="ne")
        preview_frame = ttk.Frame(frame)
        preview_frame.grid(row=3, column=1, columnspan=2, padx=5, pady=(10, 5), sticky="nsew")

        columns = ("current", "new", "status")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
        self.preview_tree.heading("current", text="現在のファイル名")
        self.preview_tree.heading("new", text="リネーム後")
        self.preview_tree.heading("status", text="状態")
        self.preview_tree.column("current", width=200, anchor="w")
        self.preview_tree.column("new", width=200, anchor="w")
        self.preview_tree.column("status", width=80, anchor="center")
        self.preview_tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.preview_tree.configure(yscrollcommand=scroll.set)

        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="対応拡張子: ", foreground="#555").grid(
            row=4, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="w"
        )
        ttk.Label(
            frame,
            text=", ".join(sorted(ext for ext in SUPPORTED_EXTS)),
            foreground="#777",
        ).grid(row=5, column=0, columnspan=3, padx=5, pady=(0, 10), sticky="w")

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=5)

        ttk.Button(
            button_frame,
            text="プレビュー更新",
            command=self.update_preview,
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            button_frame,
            text="リネーム実行",
            command=self.on_rename,
        ).grid(row=0, column=1, padx=5)
        ttk.Button(
            button_frame,
            text="オートリネーム",
            command=self.on_auto_rename,
        ).grid(row=0, column=2, padx=5)

        status_bar = ttk.Label(
            frame,
            textvariable=self.status_var,
            anchor="w",
            relief=tk.SUNKEN,
            padding=(8, 4),
        )
        status_bar.grid(row=7, column=0, columnspan=3, sticky="we", pady=(10, 0))

        self.folder_var.trace_add("write", lambda *_: self.update_preview())

    def run(self):
        self.root.mainloop()

    def handle_select_folder(self, entry_widget):
        select_folder(entry_widget)
        folder = self.folder_var.get()
        if folder and not self.theme_var.get():
            self.theme_var.set(os.path.basename(folder))
        self.update_preview()

    def update_preview(self):
        folder = self.folder_var.get()
        theme = self.theme_var.get()
        start = self.get_start_index()

        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        if not folder:
            self.status_var.set("フォルダを指定してください")
            return
        if not os.path.isdir(folder):
            self.status_var.set("フォルダが存在しません")
            return

        plan = build_rename_plan(folder, theme, start)
        if not plan:
            self.status_var.set("リネーム対象のファイルがありません")
            return

        rename_total = sum(1 for item in plan if item[-1])
        skip_total = len(plan) - rename_total

        for _, _, current, new, will_rename in plan[:200]:  # limit preview to first 200 entries
            status_text = "リネーム" if will_rename else "スキップ"
            self.preview_tree.insert("", tk.END, values=(current, new, status_text))

        remaining = max(0, len(plan) - 200)
        if remaining:
            self.status_var.set(
                f"{len(plan)} 件中 200 件を表示 (残り {remaining} 件) / リネーム: {rename_total} 件, スキップ: {skip_total} 件"
            )
        else:
            self.status_var.set(
                f"{len(plan)} 件のファイルがプレビューされています / リネーム: {rename_total} 件, スキップ: {skip_total} 件"
            )

    def on_rename(self):
        folder = self.folder_var.get()
        theme = self.theme_var.get()
        start = self.get_start_index()
        rename_images(folder, theme, start)
        self.update_preview()

    def on_auto_rename(self):
        folder = self.folder_var.get()
        auto_rename(folder)
        self.update_preview()

    def get_start_index(self) -> int:
        try:
            value = int(self.start_var.get())
        except (tk.TclError, ValueError):
            value = 1
        return max(1, value)


def main():
    app = RenameApp()
    app.run()


if __name__ == '__main__':
    main()
