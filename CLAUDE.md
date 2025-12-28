# Timer 計時器專案 - 開發文件

## 專案概述

這是一個 Windows 桌面計時器程式，使用 Python 開發，支援自訂熱鍵、本地設定記憶、系統音效提醒等功能。

## 核心需求與實作歷程

### 1. 初始需求：建立基礎計時器程式

**用戶需求：**
```
請你幫我建立以下的程式碼，把相關需要安裝的東西放進去 requirements.txt,
然後要寫 README 教我怎麼打包成 exe, 或是推上github 打包完成也行
```

**原始程式碼特徵：**
- 使用 Page Up/Page Down 作為熱鍵
- 倒數 130 秒
- 播放 `alarm.wav` 音效檔
- 使用 PyInstaller 打包成 exe

**實作內容：**
- ✅ 建立 `timer.py` 主程式
- ✅ 建立 `requirements.txt` (keyboard, pyinstaller)
- ✅ 建立 `README.md` 打包教學
- ✅ 建立 `.github/workflows/build.yml` GitHub Actions 自動打包
- ✅ 建立 `.gitignore`

---

### 2. 改進需求：可自訂按鍵 + 移除外部音效檔

**用戶需求：**
```
我希望 trigger-key & stop-key 應該可以讓用戶在啟動之後自行設定，
然後會記憶在本地上，下次起來重新開啟之後只會問他要不要重新設定，
然後 sound_filename 請用系統預設的
```

**實作內容：**
- ✅ 加入 JSON 設定檔功能 (`timer_config.json`)
- ✅ 實作 `load_config()` / `save_config()` 函式
- ✅ 實作 `setup_config()` 互動式按鍵設定
  - 讓用戶實際按下想要的按鍵來設定
  - 支援 ESC 取消設定
  - 驗證按鍵不能相同
- ✅ 改用系統預設音效 `winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)`
- ✅ 設定檔儲存位置：
  - 執行 `.py` 時：當前目錄
  - 執行 `.exe` 時：exe 同目錄
- ✅ 更新打包指令：移除 `--add-data`，改用 `--console`

**技術細節：**
- 使用 `keyboard.read_event(suppress=True)` 偵測按鍵
- 使用 `sys._MEIPASS` 處理打包後的資源路徑
- 使用 `getattr(sys, 'frozen', False)` 判斷是否為打包後的執行檔

---

### 3. 需求確認：倒數時間可設定

**用戶需求：**
```
時間也要可以設定
```

**實作確認：**
- ✅ 倒數秒數已包含在 `setup_config()` 中
- ✅ 在設定按鍵時一併設定時間
- ✅ 支援按 Enter 使用預設值（130 秒）

---

### 4. 增強需求：時間到後可調整時間

**用戶需求：**
```
每次的 time's up 要有一個按鈕問用戶要不要重新設定時間
```

**實作內容：**
- ✅ 修改 `on_timeout()` 函式
- ✅ 時間到後詢問是否調整倒數時間
- ✅ 如果要調整，可輸入新的秒數並儲存
- ✅ 詢問是否立即重新開始計時
- ✅ 提供友善的提示訊息

**函式修改：**
```python
def on_timeout():
    play_sound()
    # 詢問是否調整時間
    # 如果調整，更新 config 並儲存
    # 詢問是否立即開始
```

---

### 5. 進階需求：執行中可隨時重新設定

**用戶需求：**
```
要讓用戶可以輸入/setup
```

**實作內容：**
- ✅ 建立 `command_listener()` 在背景 thread 監聽輸入
- ✅ 建立 `register_hotkeys()` / `unregister_hotkeys()` 管理熱鍵
- ✅ 當輸入 `/setup` 時：
  1. 暫時移除所有熱鍵
  2. 停止當前計時器
  3. 執行設定流程
  4. 重新註冊熱鍵
  5. 恢復程式運作
- ✅ 使用 daemon thread 避免阻塞主程式

**技術細節：**
- 使用 `threading.Thread(target=command_listener, daemon=True)`
- 在設定模式時安全地切換熱鍵狀態
- 處理 EOFError 和一般例外

---

### 6. 部署問題修正：GitHub Actions 權限

**問題：**
```
Run softprops/action-gh-release@v1
⚠️ Unexpected error fetching GitHub release for tag refs/tags/v0.0.1:
HttpError: Resource not accessible by integration
Error: Resource not accessible by integration
```

**解決方案：**
- ✅ 在 `.github/workflows/build.yml` 加入權限設定
```yaml
jobs:
  build:
    permissions:
      contents: write
```

---

## 檔案結構

```
farm-check-rms/
├── timer.py                  # 主程式
├── requirements.txt          # Python 相依套件
├── timer_config.json        # 使用者設定檔（自動產生，已加入 .gitignore）
├── README.md                # 使用說明
├── CLAUDE.md                # 開發文件（本檔案）
├── .gitignore               # Git 忽略檔案
└── .github/
    └── workflows/
        └── build.yml        # GitHub Actions 自動打包設定
```

---

## 核心功能列表

### 設定管理
- [x] 首次啟動引導設定
- [x] 本地設定檔儲存與讀取
- [x] 啟動時詢問是否重新設定
- [x] 執行中輸入 `/setup` 重新設定
- [x] 時間到後快速調整倒數時間

### 計時功能
- [x] 自訂倒數秒數（預設 130 秒）
- [x] 使用熱鍵啟動/重置計時
- [x] 使用熱鍵停止計時
- [x] 時間到播放系統音效

### 熱鍵系統
- [x] 自訂 START/RESET 熱鍵
- [x] 自訂 STOP 熱鍵
- [x] 動態註冊/移除熱鍵
- [x] 按鍵偵測與驗證

### 打包與部署
- [x] PyInstaller 本地打包
- [x] GitHub Actions 自動打包
- [x] 設定檔跟隨執行檔位置

---

## 技術架構

### 主要模組
```python
# 設定管理
- get_config_path()      # 取得設定檔路徑
- load_config()          # 讀取設定
- save_config()          # 儲存設定
- setup_config()         # 互動式設定

# 計時功能
- start_timer()          # 啟動計時器
- stop_timer()           # 停止計時器
- on_timeout()           # 時間到的處理

# 熱鍵管理
- register_hotkeys()     # 註冊熱鍵
- unregister_hotkeys()   # 移除熱鍵

# 背景監聽
- command_listener()     # 監聽 /setup 指令

# 主程式
- main()                 # 程式入口
```

### 全域變數
```python
current_timer = None     # 當前計時器 (threading.Timer)
config = {}              # 設定字典
                         # - trigger_key: str
                         # - stop_key: str
                         # - countdown_seconds: int
```

---

## 打包指令

### 本地打包
```bash
pip install -r requirements.txt
pyinstaller --onefile --console timer.py
```

### GitHub Actions
- 推送 tag 觸發自動打包：`git tag v1.0.0 && git push origin v1.0.0`
- 或手動觸發：workflow_dispatch

---

## 已知限制與注意事項

1. **平台限制**：僅支援 Windows（使用 winsound 模組）
2. **權限需求**：需要管理員權限註冊全域熱鍵
3. **特殊按鍵**：某些按鍵（Fn、Windows 鍵）可能無法偵測
4. **熱鍵衝突**：使用者應避免選擇與其他程式衝突的按鍵

---

## 未來可能的改進方向

- [ ] 支援多組計時器設定檔（工作/休息等）
- [ ] 加入視覺化進度條
- [ ] 支援自訂音效檔案（可選）
- [ ] 加入計時歷史記錄
- [ ] 支援 macOS/Linux（替代 winsound）
- [ ] 加入系統托盤圖示
- [ ] 支援快捷指令（如 `/start`, `/stop`）
- [ ] 計時器暫停功能

---

## 開發指令快速參考

```bash
# 本地測試
python timer.py

# 本地打包
pyinstaller --onefile --console timer.py

# Git 操作
git add .
git commit -m "feat: add new feature"
git push

# 發布新版本
git tag v1.0.0
git push origin v1.0.0
```

---

## 相依套件說明

### keyboard (0.13.5)
- 用途：偵測與註冊全域熱鍵
- 主要功能：
  - `keyboard.read_event()` - 偵測按鍵
  - `keyboard.add_hotkey()` - 註冊熱鍵
  - `keyboard.remove_hotkey()` - 移除熱鍵

### pyinstaller (6.11.1)
- 用途：打包成獨立執行檔
- 打包參數：
  - `--onefile` - 單一執行檔
  - `--console` - 顯示命令列視窗

### 標準庫模組
- `threading` - 計時器與背景監聽
- `winsound` - Windows 系統音效
- `json` - 設定檔儲存
- `os`, `sys` - 檔案路徑處理

---

## 版本歷史

### v0.0.1 - 初始版本
- 基礎計時器功能
- 固定熱鍵（Page Up/Down）
- 使用外部音效檔

### v0.0.2 - 設定系統
- 可自訂熱鍵
- 本地設定記憶
- 改用系統音效

### v0.0.3 - 互動增強
- 時間到後可調整時間
- 執行中可輸入 `/setup`

---

## 給未來開發者的建議

1. **修改設定流程**：主要邏輯在 `setup_config()` 和 `command_listener()`
2. **修改計時邏輯**：主要在 `start_timer()` 和 `on_timeout()`
3. **修改熱鍵系統**：注意 `register_hotkeys()` 和 `unregister_hotkeys()` 的配對
4. **測試建議**：
   - 測試首次啟動流程
   - 測試設定檔載入
   - 測試熱鍵衝突處理
   - 測試 `/setup` 指令
   - 測試打包後的執行檔

---

最後更新：2025-12-28
