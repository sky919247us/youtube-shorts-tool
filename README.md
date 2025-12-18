# 🔥 YouTube Shorts 爆款搜索神器 (Viral Video Search Tool)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://youtube-shorts-tool.streamlit.app/)
![Release](https://img.shields.io/badge/Release-v20251218.1-blue)
![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

這是一個專為挖掘 **YouTube Shorts** 高流量爆款影片設計的工具。透過多重篩選與數據分析，協助創作者與行銷人員快速找到潛力內容與流量密碼。

👉 **支援雙平台模式**：免安裝網頁版 (Web) / 電腦便攜版 (Windows EXE)

---

## ⚡ 快速開始 (Quick Start)

### 方式一：線上網頁版 (Web App)
無需下載任何檔案，手機/電腦打開瀏覽器即可使用：
👉 **[點擊開啟線上版](https://youtube-shorts-tool.streamlit.app/)**

### 方式二：Windows 桌面版 (Portable EXE)
由 **GuanDa AI Studio** 發布的最新正式版，無需安裝 Python 環境，下載即用。

* **目前版本**：`20251218v.1` (正式版)
* **下載連結**：前往 **[Releases 頁面](https://github.com/sky919247us/youtube-shorts-tool/releases/tag/20251218v.1)** 下載 `YouTubeShortsSearchTool.exe`
* **使用方式**：下載後雙擊執行即可。

---

## ⚠️ 重要：關於 API Key (Must Read)

為了確保軟體長期穩定運作，本工具採取 **「自備 API Key」** 模式。

> **為什麼不內建 Key？**
> YouTube API 雖然免費，但每日有「積分上限」。若將開發者的 Key 內建供所有人共用，極短時間內就會因流量耗盡而導致全體當機。

✅ **解決方案**：
請申請您自己的 **YouTube Data API v3 Key**（完全免費）。
* **桌面版**：於軟體介面左側貼上您的 Key。
* **網頁版**：於側邊欄位輸入您的 Key。
* 大家使用各自的免費額度，最穩定、最安全！

---

## ✨ 核心功能 (Features)

* **🔥 獨家火焰評級系統**：
    * 直觀顯示流量等級，一眼識別千萬觀看爆款。
    * 🔥🔥🔥：觀看數 > 1,000 萬
    * 🔥🔥：觀看數 > 100 萬
* **📈 爆款分析儀表板**：
    * 自動計算「日均觀看數」，精準判斷影片是「萬年老片」還是「近期黑馬」。
* **🎯 精準搜尋過濾**：
    * 支援關鍵字、發佈時間範圍 (如 30 天內)、影片長度過濾。
    * 強制鎖定 Shorts 格式，排除長影片干擾。
* **🛡️ API 管理 (桌面版限定)**：
    * 支援多組 API Key 輪替機制與遮罩保護，避免單一 Key 超額。
* **💾 數據導出**：
    * 支援將搜尋結果另存為 HTML 報告，方便分享與歸檔。

---

## 🛠️ 開發者部署 (For Developers)

如果您希望修改原始碼或自行部署：

### 1. 複製專案
```bash
git clone [https://github.com/sky919247us/youtube-shorts-tool.git](https://github.com/sky919247us/youtube-shorts-tool.git)
cd youtube-shorts-tool
