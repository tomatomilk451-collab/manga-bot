import os
import logging
from datetime import datetime
import tweepy
import time

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 環境変数からキー取得
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN]):
    logger.error("環境変数が足りません！GitHub Secretsに設定してください。")
    exit(1)

# Tweepy v2 クライアント
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

# API v1.1 (画像アップロード用)
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

def post_manga_thread():
    """
    16枚の漫画画像をスレッド形式で投稿
    """
    
    # images フォルダ内の画像ファイル
    image_folder = "images"
    image_files = [
        os.path.join(image_folder, f"page_{i:02d}.jpg") 
        for i in range(1, 17)
    ]
    
    # ファイルの存在確認
    missing_files = [f for f in image_files if not os.path.exists(f)]
    if missing_files:
        logger.error(f"画像ファイルが見つかりません: {missing_files}")
        logger.info("利用可能なファイル:")
        if os.path.exists(image_folder):
            for f in os.listdir(image_folder):
                logger.info(f"  - {f}")
        return False
    
    total = len(image_files)
    prev_tweet_id = None
    
    logger.info(f"=== 漫画スレッド投稿開始 ({total}枚) ===")
    logger.info(f"投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        for i, image_file in enumerate(image_files, start=1):
            logger.info(f"[{i}/{total}] 処理中: {image_file}")
            
            # 画像をアップロード
            try:
                media = api.media_upload(image_file)
                logger.info(f"  ✓ 画像アップロード成功: {media.media_id}")
            except Exception as e:
                logger.error(f"  ✗ 画像アップロード失敗: {e}")
                raise
            
            # ツイートテキスト
            if i == 1:
                tweet_text = f"📖 新作漫画公開！({i}/{total})\n\n#創作漫画 #オリジナル漫画"
            else:
                tweet_text = f"({i}/{total})"
            
            # ツイート投稿
            try:
                if prev_tweet_id:
                    response = client.create_tweet(
                        text=tweet_text,
                        media_ids=[media.media_id],
                        in_reply_to_tweet_id=prev_tweet_id
                    )
                else:
                    response = client.create_tweet(
                        text=tweet_text,
                        media_ids=[media.media_id]
                    )
                
                prev_tweet_id = response.data['id']
                logger.info(f"  ✓ ツイート投稿成功: https://twitter.com/i/web/status/{prev_tweet_id}")
                
            except Exception as e:
                logger.error(f"  ✗ ツイート投稿失敗: {e}")
                raise
            
            # API制限対策: 待機
            if i < total:
                time.sleep(3)
        
        # 最後に通販リンクを追加
        final_text = (
            "💖 続きは通販で読めます！\n"
            "📕 https://example.com\n\n"
            "#同人誌 #通販 #オリジナル"
        )
        
        try:
            final_response = client.create_tweet(
                text=final_text,
                in_reply_to_tweet_id=prev_tweet_id
            )
            logger.info(f"  ✓ 最終ツイート投稿成功: https://twitter.com/i/web/status/{final_response.data['id']}")
        except Exception as e:
            logger.error(f"  ✗ 最終ツイート投稿失敗: {e}")
            # 最終ツイートが失敗しても漫画は投稿済みなのでエラーにしない
        
        logger.info("=== 漫画スレッド投稿完了！ ===")
        return True
        
    except tweepy.TweepyException as e:
        logger.error(f"Tweepyエラー: {e}")
        if hasattr(e, 'response'):
            logger.error(f"レスポンス: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Bot起動")
    logger.info("=" * 50)
    
    success = post_manga_thread()
    
    if success:
        logger.info("✅ 全ての処理が正常に完了しました")
        exit(0)
    else:
        logger.error("❌ 処理中にエラーが発生しました")
        exit(1)
