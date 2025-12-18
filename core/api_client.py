import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
from config.key_manager import KeyManager
from core.data_processor import DataProcessor

class YouTubeAPIClient:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.service = None
        self._init_service()

    def _init_service(self):
        """初始化 YouTube Service"""
        key = self.key_manager.get_current_key()
        if not key:
            self.service = None
            return
        
        try:
            self.service = build('youtube', 'v3', developerKey=key, cache_discovery=False)
        except Exception as e:
            logging.error(f"Failed to create YouTube service: {e}")
            self.service = None

    def _handle_api_error(self, error: HttpError) -> bool:
        """
        處理 API 錯誤，如果是 Quota Exceeded 則嘗試輪替 Key
        :return: True if rotated and retry is possible, False otherwise
        """
        if error.resp.status in [403, 429]:
            reason = error.error_details[0].get('reason') if error.error_details else ""
            if reason in ['quotaExceeded', 'dailyLimitExceeded']:
                logging.warning("Quota exceeded, rotating key...")
                new_key = self.key_manager.rotate_key()
                if new_key:
                    self._init_service()
                    return True
        return False

    def search_shorts(self, keyword: str, days_ago: int = 30, max_pages: int = 5) -> list[str]:
        """
        第一階段：搜尋並取得 Video IDs
        """
        if not self.service:
            self._init_service()
            if not self.service:
                logging.error("No valid API Key available.")
                return []

        # Use timezone aware UTC
        now_utc = datetime.now(timezone.utc)
        published_after = (now_utc - timedelta(days=days_ago)).replace(microsecond=0).isoformat()
        video_ids = []
        next_page_token = None
        
        for _ in range(max_pages):
            try:
                request = self.service.search().list(
                    part="id",
                    q=keyword,
                    type="video",
                    videoDuration="short",  # 鎖定短影音
                    publishedAfter=published_after,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    vid = item["id"].get("videoId")
                    if vid:
                        video_ids.append(vid)
                
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                if self._handle_api_error(e):
                    continue # Retry logic could be more complex, but for now loop continues with new key next iteration
                    # Note: Strict retry for the *same* page requires loop restructuring, but here we just try next iteration or fail
                logging.error(f"Search API Error: {e}")
                break
            except Exception as e:
                logging.error(f"Unexpected error during search: {e}")
                break
                
        return video_ids

    def get_video_details(self, video_ids: list[str]) -> list[dict]:
        """
        第二階段：取得詳細資訊 (Statistics, ContentDetails)
        """
        if not video_ids or not self.service:
            return []

        results = []
        # API 限制一次最多 50 筆
        chunk_size = 50
        
        for i in range(0, len(video_ids), chunk_size):
            chunk = video_ids[i:i + chunk_size]
            ids_str = ",".join(chunk)
            
            try:
                request = self.service.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=ids_str
                )
                response = request.execute()
                results.extend(response.get("items", []))
                
            except HttpError as e:
                if self._handle_api_error(e):
                    # Retry current chunk
                    # Minimal retry logic: re-init and try once more
                    try:
                        if self.service:
                            request = self.service.videos().list(
                                part="snippet,contentDetails,statistics",
                                id=ids_str
                            )
                            response = request.execute()
                            results.extend(response.get("items", []))
                    except:
                         logging.error(f"Retry failed for chunk {i}")
                else:
                    logging.error(f"Video Details API Error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error details fetch: {e}")
                
        return results

    def fetch_and_filter(self, keyword: str, settings: dict, progress_callback=None) -> list[dict]:
        """
        整合流程：搜尋 -> 詳情 -> 過濾 -> 封裝
        :param settings: 包含 min_views, min_duration, days_ago, max_pages 等
        """
        # Unpack settings
        days = settings.get('days', 30)
        max_pages = settings.get('max_pages', 5)
        min_views = settings.get('min_views', 100000)
        max_duration = settings.get('max_duration', 60)
        limit_per_kw = settings.get('limit', 50)
        
        if progress_callback:
            progress_callback(10, f"Searching for '{keyword}'...")

        # 1. Search
        vids = self.search_shorts(keyword, days, max_pages)
        if not vids:
            return []

        if progress_callback:
            progress_callback(50, f"Fetching details for {len(vids)} videos...")

        # 2. Details
        raw_items = self.get_video_details(vids)
        
        if progress_callback:
            progress_callback(80, "Processing and filtering data...")

        # 3. Filter & Process
        processed_videos = []
        for item in raw_items:
            if DataProcessor.filter_video(item, min_views, max_duration):
                # Enhance item with calculated stats
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                
                view_count = int(stats.get('viewCount', 0))
                pub_at = snippet.get('publishedAt', '')
                
                item['_daily_views'] = DataProcessor.calculate_daily_views(view_count, pub_at)
                item['_rating'] = DataProcessor.get_flame_rating(view_count)
                item['_duration_sec'] = DataProcessor.parse_iso_duration(item['contentDetails']['duration'])
                item['_formatted_duration'] = DataProcessor.format_duration(item['_duration_sec'])
                
                processed_videos.append(item)
                
                if len(processed_videos) >= limit_per_kw:
                    break
        
        return processed_videos
