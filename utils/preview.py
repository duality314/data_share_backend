import urllib.request


def read_first_lines(file_path: str, max_lines: int = 10):
    """读取指定文件的前 max_lines 行，返回行内容列表"""
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line.rstrip('\n'))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return lines


def read_first_lines_from_url(url: str, max_lines: int = 10, timeout: int = 5):
    """按流式方式读取URL文本前几行，读取失败时返回空列表"""
    lines = []
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            for raw in resp:
                line = raw.decode("utf-8", errors="ignore").rstrip("\n")
                lines.append(line)
                if len(lines) >= max_lines:
                    break
    except Exception as e:
        print(f"Error reading url {url}: {e}")
    return lines


def can_preview_text(data_type: str):
    """仅文本/CSV类型尝试预览，其他类型直接跳过"""
    normalized = (data_type or "").strip().lower()
    return normalized in ("text", "txt", "csv")


def read_dataset_preview_lines(dataset, max_lines: int = 10):
    """根据存储类型读取预览内容，异常统一返回空列表"""
    return []
