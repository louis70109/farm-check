# ringer 桌面版（GPUI）

以 [GPUI](https://crates.io/crates/gpui)（Zed 編輯器使用的 Rust GUI 框架）重新實作的桌面版計時器，對應 Python 版 `timer.py` 的計時核心功能。

## 功能

- 倒數秒數與隨機偏移（±N 秒），每次啟動重新隨機
- 每 5 次啟動隨機平移基準時間（與 Python 版相同的防偵測機制）
- 進度條、剩餘時間（MM:SS）、實際倒數資訊
- 時間到播放系統提示音（Windows；其他系統不發聲）
- 倒數秒數與偏移可用按鈕微調，所有變更即時儲存
- 開始/重置、停止熱鍵可自訂（點「變更」後按下按鍵，Esc 取消）
- 繁體中文 / English，右上角可即時切換，語言設定會儲存

### 尚未移植的功能

以下 Python 版功能目前**不在**桌面版內：

- 全域熱鍵（GPUI 只會在視窗有焦點時收到按鍵）
- 自動點擊 MapleRoyals 視窗、視窗選擇、任務列閃爍預覽
- 自動切換視窗（Alt+Esc 巨集）
- 系統匣圖示、網頁介面
- 執行中輸入 `/setup`（改為視窗內的設定區）

## 設定檔

與 Python 版共用 `timer_config.json`，位置為執行檔所在資料夾。桌面版只讀寫它負責的欄位，其他欄位（例如 Python 版的 `selected_window_hwnds`）會原樣保留。

```json
{
  "trigger_key": "page up",
  "stop_key": "page down",
  "countdown_seconds": 130,
  "random_offset_seconds": 0,
  "language": "zh_TW"
}
```

## 建置

需要穩定版 Rust 工具鏈（`rustup` 安裝）。

```bash
cd desktop
cargo run --release     # 直接執行
cargo test              # 單元測試（計時邏輯、設定檔、翻譯）
cargo build --release   # 產出 target/release/ringer(.exe)
```

### Linux 需要的系統套件

Debian / Ubuntu：

```bash
sudo apt-get install -y libxkbcommon-dev libxkbcommon-x11-dev libwayland-dev \
  libxcb1-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev \
  libfontconfig-dev libfreetype-dev libvulkan1 mesa-vulkan-drivers
```

Windows 不需要額外套件，GPUI 會使用 DirectX。

## 注意事項

- `vendor/xattr/` 是 `xattr 0.2.3` 的本地修補版：上游在新版 `libc` 中已移除 Linux 的 `ENOATTR` 常數，而 `rustix 1.x` 要求新版 `libc`。修補只把該常數改為 `ENODATA`（Linux 上數值相同），不影響其他行為。
- 目前只在 Linux（Xvfb + 軟體 Vulkan）上實際啟動與操作過；Windows 版本尚未在本環境編譯驗證，請在 Windows 上執行 `cargo build --release` 確認。
