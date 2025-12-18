import os
import logging
import random
import json
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
    logger.error("❌ 環境変数が足りません！GitHub Secretsに設定してください。")
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

# 設定
MANGA_FOLDER = "manga"  # 漫画フォルダのパス
HISTORY_FILE = "post_history.json"  # 投稿履歴ファイル
CONFIG_FILE = "manga_config.json"  # 作品設定ファイル
IMAGES_PER_TWEET = 2  # 1ツイートあたりの画像枚数

def load_manga_config():
    """作品設定を読み込み"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ 設定ファイル読み込みエラー: {e}")
    return {}

def get_all_works():
    """
    manga/ フォルダ内の全作品を取得
    将来的に複数作品を追加した時は自動的に検出される
    """
    if not os.path.exists(MANGA_FOLDER):
        logger.error(f"❌ フォルダが見つかりません: {MANGA_FOLDER}")
        return []
    
    works = []
    for work_name in os.listdir(MANGA_FOLDER):
        work_path = os.path.join(MANGA_FOLDER, work_name)
        if os.path.isdir(work_path):
            # ページ数をカウント
            image_files = sorted([
                f for f in os.listdir(work_path) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])
            if image_files:
                works.append({
                    'name': work_name,
                    'path': work_path,
                    'images': image_files,
                    'page_count': len(image_files)
                })
                logger.info(f"📚 作品検出: {work_name} ({len(image_files)}ページ)")
    
    return works

def load_post_history():
    """投稿履歴を読み込み"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ 履歴ファイル読み込みエラー: {e}")
    return {}

def save_post_history(history):
    """投稿履歴を保存"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ 履歴ファイル保存エラー: {e}")

def select_work_to_post(works, history):
    """
    投稿する作品を選択
    現在: ランダム選択
    将来: 複数作品があれば全てから選択
    """
    if not works:
        logger.error("❌ 投稿可能な作品がありません")
        return None
    
    # ランダムに選択
    selected = random.choice(works)
    logger.info(f"🎲 選択された作品: {selected['name']}")
    
    return selected

def get_work_config(work_name, manga_config):
    """作品の設定を取得 (なければデフォルト値)"""
    if work_name in manga_config:
        return manga_config[work_name]
    
    # デフォルト設定
    logger.warning(f"⚠️ {work_name} の設定が見つかりません。デフォルト設定を使用します。")
    return {
        "title": work_name,
        "tweet_patterns": [
            "📖 同人誌公開！",
            "💕 新刊できました！",
        ],
        "hashtag_patterns": [
            "#同人誌 #nsfw",
        ],
        "shop_url": "https://example.com",
        "final_text": "💖 続きは通販で読めます！\n📕 {shop_url}\n\n#同人誌 #通販 #nsfw"
    }

def post_manga_thread(work, manga_config):
    """
    漫画をスレッド形式で投稿 (2枚ずつ)
    """
    work_name = work['name']
    image_files = work['images']
    work_path = work['path']
    total_images = len(image_files)
    
    # 作品の設定を取得
    config = get_work_config(work_name, manga_config)
    
    # ランダムに1つずつ選択
    selected_tweet = random.choice(config['tweet_patterns'])
    selected_hashtags = random.choice(config['hashtag_patterns'])
    logger.info(f"📝 選択された投稿文: {selected_tweet}")
    logger.info(f"🏷️ 選択されたハッシュタグ: {selected_hashtags}")
    logger.info(f"🔗 通販URL: {config['shop_url']}")
    
    # 総ツイート数を計算 (2枚ずつなので画像数÷2、切り上げ)
    import math
    total_tweets = math.ceil(total_images / IMAGES_PER_TWEET)
    
    logger.info(f"=" * 60)
    logger.info(f"📖 漫画スレッド投稿開始")
    logger.info(f"   作品名: {work_name}")
    logger.info(f"   総画像数: {total_images}枚")
    logger.info(f"   総ツイート数: {total_tweets}件 (2枚ずつ)")
    logger.info(f"   投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"=" * 60)
    
    prev_tweet_id = None
    posted_tweet_ids = []
    
    try:
        # 画像を2枚ずつまとめて処理
        for tweet_index in range(total_tweets):
            # 2枚ずつ取得 (最後は1枚の可能性あり)
            start_idx = tweet_index * IMAGES_PER_TWEET
            end_idx = min(start_idx + IMAGES_PER_TWEET, total_images)
            batch_files = image_files[start_idx:end_idx]
            
            current_tweet_num = tweet_index + 1
            logger.info(f"[{current_tweet_num}/{total_tweets}] 処理中 (画像{len(batch_files)}枚)")
            
            # 複数画像をアップロード
            media_ids = []
            for image_file in batch_files:
                image_path = os.path.join(work_path, image_file)
                logger.info(f"  - {image_file}")
                
                try:
                    media = api.media_upload(image_path)
                    media_ids.append(media.media_id)
                    logger.info(f"    ✓ 画像アップロード成功: {media.media_id}")
                except Exception as e:
                    logger.error(f"    ✗ 画像アップロード失敗: {e}")
                    raise
            
            # ツイートテキスト作成
            if tweet_index == 0:
                # 最初のツイート - ランダムな投稿文 + ハッシュタグ
                tweet_text = f"{selected_tweet}({current_tweet_num}/{total_tweets})\n\n{selected_hashtags}"
            else:
                # 2枚目以降 - ツイート番号のみ
                tweet_text = f"({current_tweet_num}/{total_tweets})"
            
            # ツイート投稿
            try:
                if prev_tweet_id:
                    # 返信として投稿(スレッド)
                    response = client.create_tweet(
                        text=tweet_text,
                        media_ids=media_ids,
                        in_reply_to_tweet_id=prev_tweet_id
                    )
                else:
                    # 最初のツイート
                    response = client.create_tweet(
                        text=tweet_text,
                        media_ids=media_ids
                    )
                
                tweet_id = response.data['id']
                prev_tweet_id = tweet_id
                posted_tweet_ids.append(tweet_id)
                
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                logger.info(f"  ✓ ツイート投稿成功: {tweet_url}")
                
            except Exception as e:
                logger.error(f"  ✗ ツイート投稿失敗: {e}")
                raise
            
            # API制限対策: 少し待機
            if current_tweet_num < total_tweets:
                time.sleep(3)
        
        # 最後に通販リンクを追加
        final_text = config['final_text'].format(shop_url=config['shop_url'])
        
        try:
            final_response = client.create_tweet(
                text=final_text,
                in_reply_to_tweet_id=prev_tweet_id
            )
            final_tweet_id = final_response.data['id']
            posted_tweet_ids.append(final_tweet_id)
            
            final_url = f"https://twitter.com/i/web/status/{final_tweet_id}"
            logger.info(f"  ✓ 最終ツイート投稿成功: {final_url}")
            
        except Exception as e:
            logger.error(f"  ✗ 最終ツイート投稿失敗: {e}")
            # 最終ツイートが失敗しても漫画は投稿済みなのでエラーにしない
        
        logger.info(f"=" * 60)
        logger.info(f"✅ 漫画スレッド投稿完了！")
        logger.info(f"   投稿ツイート数: {len(posted_tweet_ids)}件")
        logger.info(f"   最初のツイート: https://twitter.com/i/web/status/{posted_tweet_ids[0]}")
        logger.info(f"=" * 60)
        
        return {
            'success': True,
            'work_name': work_name,
            'tweet_ids': posted_tweet_ids,
            'first_tweet_url': f"https://twitter.com/i/web/status/{posted_tweet_ids[0]}"
        }
        
    except tweepy.TweepyException as e:
        logger.error(f"❌ Tweepyエラー: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"   レスポンス: {e.response.text}")
        return {'success': False, 'error': str(e)}
        
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

def main():
    """メイン処理"""
    logger.info("🤖 Bot起動")
    logger.info(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 作品設定を読み込み
    manga_config = load_manga_config()
    logger.info(f"📋 設定ファイル読み込み完了: {len(manga_config)}作品")
    
    # 作品一覧を取得
    works = get_all_works()
    
    if not works:
        logger.error("❌ 投稿可能な作品がありません")
        logger.info(f"💡 '{MANGA_FOLDER}' フォルダに作品フォルダと画像を配置してください")
        exit(1)
    
    logger.info(f"📚 検出された作品数: {len(works)}件")
    
    # 投稿履歴を読み込み
    history = load_post_history()
    
    # 投稿する作品を選択
    selected_work = select_work_to_post(works, history)
    
    if not selected_work:
        logger.error("❌ 作品の選択に失敗しました")
        exit(1)
    
    # 漫画スレッドを投稿
    result = post_manga_thread(selected_work, manga_config)
    
    if result['success']:
        # 投稿履歴を更新
        work_name = result['work_name']
        if work_name not in history:
            history[work_name] = {
                'post_count': 0,
                'posts': []
            }
        
        history[work_name]['post_count'] += 1
        history[work_name]['last_posted'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history[work_name]['posts'].append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'first_tweet_url': result['first_tweet_url']
        })
        
        save_post_history(history)
        
        logger.info("✅ 全ての処理が正常に完了しました")
        exit(0)
    else:
        logger.error("❌ 投稿処理中にエラーが発生しました")
        exit(1)

if __name__ == "__main__":
    main()
