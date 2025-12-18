
import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import Core Modules
from config.settings import (
    DEFAULT_KEYWORDS, DEFAULT_DAYS, DEFAULT_MAX_PAGES, 
    DEFAULT_LIMIT_PER_KEYWORD, DEFAULT_MIN_VIEWS, DEFAULT_MAX_DURATION,
    APP_VERSION, DONATE_URL, CHANNEL_URL
)
from config.key_manager import KeyManager
from core.api_client import YouTubeAPIClient

# Page Config
st.set_page_config(
    page_title=f"YouTube Shorts 爆款搜索神器 {APP_VERSION}",
    page_icon="assets/app.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS / Styles ---
st.markdown("""
<style>
    /* Card Style */
    .video-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: black;
    }
    .video-card:hover {
        border-color: #007acc;
        box-shadow: 0 8px 15px rgba(0,0,0,0.15);
    }
    .video-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .video-title:hover {
        color: #007acc;
    }
    .channel-name {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 8px;
    }
    .stats-row {
        font-size: 0.9rem;
        color: #444;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .daily-views {
        color: #2e7d32;
        font-weight: bold;
    }
    .action-btn {
        display: inline-block;
        background-color: #333;
        color: white !important;
        padding: 5px 12px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 0.85rem;
        margin-right: 5px;
        transition: 0.2s;
    }
    .action-btn:hover {
        background-color: black;
    }
    
    /* Support Buttons */
    .kofi-btn {
        background-color: #00b9fe !important;
        color: white !important;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
    .yt-btn {
        background-color: #ff0000 !important;
        color: white !important;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'results' not in st.session_state:
    st.session_state.results = []
if 'searching' not in st.session_state:
    st.session_state.searching = False

# --- Sidebar: Controls ---
with st.sidebar:
    st.header("⚙️ 設定面板")
    
    with st.expander("API 金鑰設定", expanded=True):
        api_keys_input = st.text_area(
            "輸入 API Keys (每行一個)", 
            placeholder="AIxxxxxxxxxxxxxxxxx",
            help="請輸入您的 YouTube Data API v3 金鑰"
        )
    
    with st.expander("搜尋條件", expanded=True):
        keywords = st.text_input("關鍵字 (逗號分隔)", ", ".join(DEFAULT_KEYWORDS))
        days = st.slider("發布時間 (天)", 1, 365, DEFAULT_DAYS)
        depth = st.slider("搜尋深度 (頁)", 1, 20, DEFAULT_MAX_PAGES)
        limit = st.slider("數量限制 (部)", 1, 500, DEFAULT_LIMIT_PER_KEYWORD)
    
    with st.expander("篩選規則", expanded=True):
        min_views = st.number_input("最低觀看數", 0, 100000000, DEFAULT_MIN_VIEWS, step=10000)
        max_duration = st.slider("最長時長 (秒)", 0, 60, DEFAULT_MAX_DURATION)
    
    st.markdown("---")
    st.markdown("### 支持作者")
    st.markdown(f"""
    <div style="text-align: center;">
        <a href="{DONATE_URL}" target="_blank" class="kofi-btn">☕ 請喝咖啡</a><br>
        <a href="{CHANNEL_URL}" target="_blank" class="yt-btn">📺 訂閱頻道</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: right; color: gray; font-size: 0.8rem; margin-top: 20px'>Version: {APP_VERSION}</div>", unsafe_allow_html=True)

# --- Main Area ---
st.title("🔥 YouTube Shorts 爆款搜索神器")

# Search Logic
def run_search():
    if not api_keys_input.strip():
        st.error("請先輸入 API Key！")
        return
    
    st.session_state.searching = True
    
    # Initialize Managers
    key_manager = KeyManager(file_path=None) # Don't load from file, use input
    keys = [k.strip() for k in api_keys_input.splitlines() if k.strip()]
    key_manager.set_keys(keys)
    
    api_client = YouTubeAPIClient(key_manager)
    
    settings = {
        "keywords": [k.strip() for k in keywords.split(',') if k.strip()],
        "days": days,
        "max_pages": depth,
        "limit": limit,
        "min_views": min_views,
        "max_duration": max_duration
    }
    
    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_kw = len(settings['keywords'])
    
    for idx, kw in enumerate(settings['keywords']):
        status_text.text(f"正在搜尋: {kw}...")
        results = api_client.fetch_and_filter(kw, settings, lambda x, y: None) # No callback for now
        all_results.extend(results)
        progress_bar.progress(int((idx + 1) / total_kw * 100))
        
    st.session_state.results = all_results
    st.session_state.searching = False
    status_text.text("搜尋完成！")
    
    # Check Celebration
    has_viral = any(int(v.get('statistics', {}).get('viewCount', 0)) >= 10000000 for v in all_results)
    if has_viral:
        st.balloons()
        st.success("哇！發現千萬流量級別的超級爆款！🔥")

# Action Bar
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🚀 開始找爆款", type="primary", disabled=st.session_state.searching):
        run_search()

# Results Display
results = st.session_state.results

if results:
    st.subheader(f"找到 {len(results)} 部爆款影片")
    
    # Sort Options
    sort_opt = st.selectbox("排序方式", ["總觀看數量 (High to Low)", "日均觀看數 (High to Low)"])
    if "總觀看" in sort_opt:
        results.sort(key=lambda x: int(x['statistics'].get('viewCount', 0)), reverse=True)
    else:
        results.sort(key=lambda x: x.get('_daily_views', 0), reverse=True)

    # Display Cards
    # Using columns for responsive grid
    # Streamlit columns are not auto-wrapping, so we iterate
    
    # On mobile, we might want 1 column. On desktop, maybe 2 or 3?
    # Streamlit handles stacking automatically if we just print them one by one, 
    # but for grid view we need manual chunking. Let's stick to list view for best compatibility.
    
    for vid in results:
        snippet = vid.get('snippet', {})
        stats = vid.get('statistics', {})
        vid_id = vid.get('id')
        
        title = snippet.get('title', 'No Title')
        channel = snippet.get('channelTitle', 'Unknown')
        view_count = int(stats.get('viewCount', 0))
        daily = int(vid.get('_daily_views', 0))
        duration = vid.get('_formatted_duration', '00:00')
        rating = vid.get('_rating', '')
        thumb = snippet.get('thumbnails', {}).get('medium', {}).get('url')
        
        url = f"https://www.youtube.com/watch?v={vid_id}"
        channel_id = snippet.get('channelId')
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        
        # Render HTML Card
        st.markdown(f"""
        <div class="video-card">
            <div style="display: flex; gap: 15px;">
                <div style="flex: 0 0 160px;">
                    <img src="{thumb}" style="width: 100%; border-radius: 4px;">
                </div>
                <div style="flex: 1;">
                    <a href="{url}" target="_blank" class="video-title">{title}</a>
                    <div class="channel-name">{channel}</div>
                    <div class="stats-row">
                        <span>👀 {view_count:,} {rating}</span>
                        <span>⏱️ {duration}</span>
                    </div>
                    <div class="daily-views">🔥 日均: {daily:,}/天</div>
                    <div style="margin-top: 10px;">
                        <a href="{url}" target="_blank" class="action-btn">▶ 觀看影片</a>
                        <a href="{channel_url}" target="_blank" class="action-btn">🏠 頻道首頁</a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif not st.session_state.searching:
    st.info("👈 請在左側設定 API Key 與搜尋條件，然後點擊「開始找爆款」！")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666;">
    Generated by YouTube Shorts 爆款搜索神器 | Developed by GuanDa AI Studio<br>
    <br>
    <a href="{DONATE_URL}" target="_blank">☕ 贊助開發者</a> • 
    <a href="{CHANNEL_URL}" target="_blank">📺 免費訂閱教學</a>
</div>
""", unsafe_allow_html=True)

# Ko-fi Widget (Optional, might conflict with Streamlit iframes but we can try injecting)
# Streamlit components usually needed for script injection, but st.components.v1.html works for iframe.
# Script injection is harder. For now we use the links.
