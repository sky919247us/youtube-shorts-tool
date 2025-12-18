import isodate
from datetime import datetime, timezone
import logging
from config.settings import DEFAULT_MIN_VIEWS, DEFAULT_MAX_DURATION

class DataProcessor:
    @staticmethod
    def parse_iso_duration(duration_str: str) -> int:
        """解析 ISO 8601 時長格式為秒數"""
        try:
            td = isodate.parse_duration(duration_str)
            return int(td.total_seconds())
        except Exception:
            return 0

    @staticmethod
    def format_duration(seconds: int) -> str:
        """秒數轉為 MM:SS 格式"""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def calculate_days_ago(published_at_str: str) -> int:
        """計算發布至今的天數 (最小為 1)"""
        try:
            # Handle standard ISO format (e.g., 2023-10-01T12:00:00Z)
            pub_date = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - pub_date
            return max(1, delta.days)
        except ValueError:
            # Try parsing with microseconds if present
            try:
                pub_date = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                delta = now - pub_date
                return max(1, delta.days)
            except Exception as e:
                logging.error(f"Date parsing error for {published_at_str}: {e}")
                return 1

    @staticmethod
    def calculate_daily_views(view_count: int, published_at_str: str) -> float:
        """計算日均流量"""
        days = DataProcessor.calculate_days_ago(published_at_str)
        return view_count / days

    @staticmethod
    def get_flame_rating(view_count: int) -> str:
        """取得火焰評級"""
        if view_count >= 10_000_000:
            return "🔥🔥🔥"
        elif view_count >= 1_000_000:
            return "🔥🔥"
        elif view_count >= 500_000:
            return "🔥"
        return ""

    @staticmethod
    def filter_video(video_data: dict, min_views: int = DEFAULT_MIN_VIEWS, max_duration: int = DEFAULT_MAX_DURATION, only_shorts: bool = True) -> bool:
        """
        過濾影片邏輯
        :param video_data: 包含 'statistics' 和 'contentDetails' 的影片資料
        :param min_views: 最低觀看數
        :param max_duration: 最長時長(秒)
        :param only_shorts: 是否僅限 Shorts (<60s)
        :return: True if passed, False otherwise
        """
        stats = video_data.get('statistics', {})
        details = video_data.get('contentDetails', {})
        
        # 1. View Count Filter
        try:
            views = int(stats.get('viewCount', 0))
        except ValueError:
            views = 0
            
        if views < min_views:
            return False
            
        # 2. Duration Filter
        duration_iso = details.get('duration', 'PT0S')
        seconds = DataProcessor.parse_iso_duration(duration_iso)
        
        if seconds > max_duration:
            return False
            
        if only_shorts and seconds > 60:
            return False
            
        return True
