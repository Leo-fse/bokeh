import time
from datetime import datetime
from pathlib import Path

import pandas as pd

# 元のコード
start_time = time.time()
file_path_list = list(Path("data").glob("*.csv"))
file_info = [
    (fp.name[:8], fp.name, fp, datetime.fromtimestamp(fp.stat().st_mtime)) for fp in file_path_list
]
data = {
    "date": [info[0] for info in file_info],
    "file_name": [info[1] for info in file_info],
    "file_path": [info[2] for info in file_info],
    "update": [info[3] for info in file_info],
}
file_df = pd.DataFrame(data)
print("Original code time:", time.time() - start_time)

# リファクタリング後のコード
start_time = time.time()
file_path_list = list(Path("data").glob("*.csv"))
file_info = [
    (fp.name[:8], fp.name, fp, datetime.fromtimestamp(fp.stat().st_mtime)) for fp in file_path_list
]
data = {
    "date": [info[0] for info in file_info],
    "file_name": [info[1] for info in file_info],
    "file_path": [info[2] for info in file_info],
    "update": [info[3] for info in file_info],
}
file_df = pd.DataFrame(data)
print("Refactored code time:", time.time() - start_time)
