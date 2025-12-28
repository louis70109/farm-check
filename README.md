# Timer 計時器程式

這是一個可自訂熱鍵的計時器程式，時間到會播放系統音效提醒。

## 功能

- 🎯 **可自訂熱鍵** - 首次啟動時可以按實際按鍵來設定啟動/停止鍵
- 💾 **記憶設定** - 設定會儲存在本地，下次啟動只會詢問是否要重新設定
- 🔔 **系統音效** - 使用 Windows 系統警告音，不需要外部音效檔
- ⏱️ **可調整倒數時間** - 預設 130 秒，可在設定時自訂

## 使用方式

1. 首次啟動時，程式會請你：
   - 按下想要用來「開始/重置」計時的按鍵
   - 按下想要用來「停止」計時的按鍵
   - 輸入倒數秒數（或按 Enter 使用預設值 130 秒）

2. 設定完成後，程式會記住你的選擇

3. 下次啟動時會顯示現有設定，詢問是否要重新設定（輸入 `y` 重設，或直接按 Enter 使用現有設定）

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

   已經包含在專案中的 `.github/workflows/build.yml` 會在你推送 tag 時自動打包。

3. **觸發自動打包**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **下載執行檔**

   - 到 GitHub 專案頁面
   - 點選右側的 "Releases"
   - 下載 `timer.exe`

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
