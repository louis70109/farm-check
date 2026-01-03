# Timer 計時器程式

這是一個可自訂熱鍵的計時器程式，時間到會播放系統音效提醒。

## 功能

- 🎯 **可自訂熱鍵** - 首次啟動時可以按實際按鍵來設定啟動/停止鍵
- 💾 **記憶設定** - 設定會儲存在本地，下次啟動只會詢問是否要重新設定
- 🔔 **系統音效** - 使用 Windows 系統警告音，不需要外部音效檔
- ⏱️ **可調整倒數時間** - 預設 130 秒，可在設定時自訂
- 📊 **即時進度條** - 顯示倒數進度、完成百分比和剩餘時間
- 🎲 **隨機時間偏移** - 設定 ±N 秒的隨機時間差，模擬人類操作避免被偵測

## 使用方式

1. 首次啟動時，程式會請你：
   - 按下想要用來「開始/重置」計時的按鍵
   - 按下想要用來「停止」計時的按鍵
   - 輸入倒數秒數（或按 Enter 使用預設值 130 秒）
   - 設定隨機時間偏移（例如輸入 5 表示 ±5 秒，可避免被遊戲偵測）

2. 設定完成後，程式會記住你的選擇

3. 計時器執行時會顯示即時進度條：
   ```
   [████████████████░░░░░░░░░░░░░░]  53.2% | 01:01 remaining
   ```

4. 下次啟動時會顯示現有設定，詢問是否要重新設定（輸入 `/setup` 重設，或直接按 Enter 使用現有設定）

## 隨機時間偏移說明

為了避免被遊戲系統偵測為自動化腳本，程式支援隨機時間偏移功能：

- **作用**：每次計時器啟動時，實際倒數時間會在設定值的 ±N 秒範圍內隨機變化
- **範例**：
  - 基礎時間：130 秒
  - 偏移設定：5 秒
  - 實際執行時間：125~135 秒之間隨機
- **顯示**：程式會顯示本次實際時間和偏移量
  ```
  [RESET] Timer started: 127s (base: 130s, offset: -3s)
  ```
- **安全性**：每次重新啟動計時器都會重新隨機，避免固定規律

## 本地打包成 EXE

### 前置需求

- Python 3.8 以上
- Windows 作業系統（因為使用 winsound 和 keyboard 套件）

### 步驟

1. **安裝相依套件**
   ```bash
   pip install -r requirements.txt
   ```

2. **打包成單一執行檔**
   ```bash
   pyinstaller --onefile --console timer.py
   ```

   參數說明：
   - `--onefile`: 打包成單一 exe 檔
   - `--console`: 顯示命令列視窗（設定按鍵時需要）

3. **找到執行檔**

   打包完成後，exe 檔會在 `dist/timer.exe`

4. **執行**

   直接執行 `dist/timer.exe` 即可，首次啟動會進行設定

## 使用 GitHub Actions 自動打包

### CI/CD 流程

專案已配置 GitHub Actions 進行自動化測試和建構：

1. **自動測試**：每次推送 tag 時，會先執行完整測試套件
2. **測試必須通過**：只有當所有測試通過後，才會進行建構
3. **自動建構**：測試通過後，自動打包 Windows 執行檔
4. **自動發布**：建構完成後，自動創建 GitHub Release

### 步驟

1. **將專案推到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的使用者名稱/你的專案名稱.git
   git push -u origin main
   ```

2. **建立 GitHub Actions 設定檔**

   已經包含在專案中的 `.github/workflows/build.yml` 會在你推送 tag 時自動執行：
   - **Test Job**: 運行所有測試（51個測試案例）
   - **Build Job**: 測試通過後才執行建構

3. **觸發自動打包**
   ```bash
   # 確保本地測試通過
   python validate_tests.py
   
   # 創建版本標籤
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. **查看建構進度**
   - 到 GitHub 專案頁面
   - 點選 "Actions" 標籤
   - 查看測試和建構狀態

5. **下載執行檔**

   - 到 GitHub 專案頁面
   - 點選右側的 "Releases"
   - 下載 `timer.exe`

### 本地測試

在推送到 GitHub 前，建議先在本地運行測試：

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 運行測試
python validate_tests.py

# 或使用 pytest 直接運行
pytest tests/ -v --cov=timer --cov-report=html

# 查看覆蓋率報告
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Pre-commit Hook（可選）

安裝 pre-commit hook 以在提交前自動運行測試：

```bash
# 安裝 pre-commit
pip install pre-commit

# 設置 hook
pre-commit install

# 現在每次 git commit 都會自動運行測試
```

## 重新設定

有三種方式可以更改設定：

1. **方法一（推薦）**：程式執行中輸入 `/setup` 立即重新設定
2. **方法二**：啟動程式時輸入 `y` 進入重新設定
3. **方法三**：刪除執行檔旁的 `timer_config.json`，下次啟動會重新設定

## 時間調整

除了重新設定外，每次計時結束時也會詢問是否要調整倒數時間，可以快速修改而不用重設按鍵。

## 設定檔位置

- 執行 `.py` 檔：設定檔在當前目錄 `timer_config.json`
- 執行 `.exe` 檔：設定檔在 exe 同目錄下 `timer_config.json`

## 注意事項

- 本程式僅支援 Windows
- **需要管理員權限來註冊全域熱鍵**
- 設定按鍵時，請選擇不會與其他程式衝突的按鍵
- 某些特殊按鍵（如 Fn、Windows 鍵）可能無法被偵測
