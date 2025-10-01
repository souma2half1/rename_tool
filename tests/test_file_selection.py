import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import rename_gui


def test_should_rename_when_target_missing(tmp_path):
    src = tmp_path / "image.jpg"
    src.write_bytes(b"")
    target = tmp_path / "theme_01.jpg"

    assert rename_gui._should_rename(str(src), str(target))


def test_should_not_rename_when_other_file_exists(tmp_path):
    src = tmp_path / "image.jpg"
    src.write_bytes(b"")
    target = tmp_path / "theme_01.jpg"
    target.write_bytes(b"")

    assert not rename_gui._should_rename(str(src), str(target))


def test_should_rename_when_paths_point_to_same_file(monkeypatch, tmp_path):
    src = tmp_path / "test_01.jpg"
    src.write_bytes(b"")
    target = tmp_path / "TEST_01.jpg"

    real_exists = rename_gui.os.path.exists
    real_samefile = rename_gui.os.path.samefile

    def fake_exists(path):
        if path == str(target):
            return True
        return real_exists(path)

    def fake_samefile(path_a, path_b):
        candidates = {path_a, path_b}
        if candidates == {str(src), str(target)}:
            return True
        return real_samefile(path_a, path_b)

    monkeypatch.setattr(rename_gui.os.path, "exists", fake_exists)
    monkeypatch.setattr(rename_gui.os.path, "samefile", fake_samefile)

    assert rename_gui._should_rename(str(src), str(target))
