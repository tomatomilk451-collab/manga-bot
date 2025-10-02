# 🤖 漫画自動投稿Bot

X (Twitter) に漫画をスレッド形式で自動投稿するBotです。

## ✨ 特徴

- ✅ 画像付きスレッド投稿(最大何ページでもOK)
- ✅ GitHub Actionsで完全無料運用
- ✅ 定期自動投稿(毎週・毎日など自由に設定可能)
- ✅ 手動実行も可能
- ✅ 複数作品対応(フォルダを追加するだけ)
- ✅ 投稿履歴を自動記録

## 📁 フォルダ構成

```
manga-bot/
├── .github/
│   └── workflows/
│       └── post_manga.yml    # 自動実行設定
├── manga/                     # ← ここに作品を入れる
│   ├── work1/                 # 作品1
│   │   ├── page_01.jpg
│   │   ├── page_02.jpg
│   │   └── ...
│   ├── work2/                 # 作品2(将来追加用)
│   │   └── ...
│   └── work3/                 # 作品3(将来追加用)
│       └── ...
├── post_manga.py              # メインスクリプト
├── post_history.json          # 投稿履歴(自動生成)
└── README.md                  # このファイル
```

## 🚀 セットアップ手順

### 1. リポジトリの準備

このリポジトリをクローンまたはフォーク

### 2. 画像ファイルの配置

`manga/work1/` フォルダを作成し、漫画画像を配置:

```
manga/
└── work1/
    ├── page_01.jpg
    ├── page_02.jpg
    ├── page_03.jpg
    └── ...
```

**注意:**
- ファイル名は `page_01.jpg`, `page_02.jpg` のように連番にする
- 拡張子は `.jpg`, `.jpeg`, `.png` が使用可能
- 各画像は5MB以下推奨
- ページ数は何枚でもOK

### 3. X (Twitter) API キーの取得

1. [Twitter Developer Portal](https://developer.twitter.com/) にアクセス
2. プロジェクトとアプリを作成
3. 以下のキーを取得:
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret
   - Bearer Token

### 4. GitHub Secrets の設定

リポジトリの `Settings` → `Secrets and variables` → `Actions` で以下を追加:

| Name | 説明 |
|------|------|
| `API_KEY` | Twitter API Key |
| `API_SECRET` | Twitter API Secret Key |
| `ACCESS_TOKEN` | Twitter Access Token |
| `ACCESS_SECRET` | Twitter Access Token Secret |
| `BEARER_TOKEN` | Twitter Bearer Token |

### 5. 自動実行スケジュールの設定(任意)

`.github/workflows/post_manga.yml` の以下の部分を編集:

```yaml
schedule:
  - cron: '0 12 * * 0'  # 毎週日曜日 12:00 UTC (日本時間 21:00)
```

**よく使うスケジュール例:**

```yaml
# 毎日 12:00 UTC (日本時間 21:00)
- cron: '0 12 * * *'

# 毎週金曜日 3:00 UTC (日本時間 12:00)
- cron: '0 3 * * 5'

# 毎月1日 0:00 UTC (日本時間 9:00)
- cron: '0 0 1 * *'

# 毎週月・水・金 12:00 UTC (日本時間 21:00)
- cron: '0 12 * * 1,3,5'
```

**注意:** GitHub ActionsはUTC時間なので、日本時間から-9時間してください

## 🎮 使い方

### 手動実行

1. リポジトリの `Actions` タブを開く
2. 左サイドバーから `Post Manga Thread` を選択
3. `Run workflow` → `Run workflow` をクリック
4. 数分待つと投稿完了！

### 自動実行

設定したスケジュールで自動的に実行されます。

### ログの確認

`Actions` タブ → 実行履歴 → ログを確認できます

## 📚 複数作品を追加する方法

新しい作品を追加する場合は、`manga/` フォルダに新しいフォルダを作成するだけ:

```
manga/
├── work1/              # 既存の作品
│   └── ...
├── my_new_manga/       # ← 新しい作品を追加
│   ├── page_01.jpg
│   ├── page_02.jpg
│   └── ...
└── another_work/       # ← さらに追加
    └── ...
```

コードの変更は不要！自動的にランダムで選択されます。

## 🔧 カスタマイズ

### ツイート本文を変更

`post_manga.py` の以下の部分を編集:

```python
# 最初のツイート
tweet_text = f"📖 新作漫画公開！({i}/{total})\n\n#創作漫画 #オリジナル漫画"

# 最後のツイート(通販リンク)
final_text = (
    "💖 続きは通販で読めます！\n"
    "📕 https://example.com\n\n"  # ← ここを自分のURLに変更
    "#同人誌 #通販開始"
)
```

### ハッシュタグを変更

お好きなハッシュタグに変更してください:

```python
tweet_text = f"📖 新作漫画公開！\n\n#あなたのタグ #好きなタグ"
```

## ⚠️ 注意事項

### API制限について

- **X API Free プラン**: 月1,500ツイートまで
- **16枚の漫画スレッド**: 1回の投稿で17ツイート消費(画像16枚+通販リンク)
- **投稿可能回数**: 月約88回まで

### 推奨設定

- 週1回投稿: 月4回(余裕あり)
- 週2回投稿: 月8回(余裕あり)
- 毎日投稿: 月30回(ギリギリ)

## 🐛 トラブルシューティング

### ❌ 画像が見つかりません

- ファイル名が `page_01.jpg` の形式になっているか確認
- `manga/work1/` の中に画像があるか確認
- 大文字小文字が合っているか確認

### ❌ 401 Unauthorized

- GitHub Secrets が正しく設定されているか確認
- APIキーが有効か確認

### ❌ 429 Too Many Requests

- API制限に達しています
- 投稿間隔を空けてください

### ログを確認する方法

1. `Actions` タブを開く
2. 実行履歴から該当の実行をクリック
3. `Post manga thread` をクリック
4. ログが表示されます

## 📊 投稿履歴

投稿履歴は `post_history.json` に自動保存されます:

```json
{
  "work1": {
    "post_count": 3,
    "last_posted": "2024-10-02 21:00:00",
    "posts": [
      {
        "date": "2024-09-15 21:00:00",
        "first_tweet_url": "https://twitter.com/i/web/status/..."
      }
    ]
  }
}
```

## 📝 今後の拡張予定

- [ ] 特定の曜日に特定の作品を投稿
- [ ] 新作優先モード
- [ ] 反応が良かった作品の再投稿
- [ ] 投稿結果の通知機能

## 📄 ライセンス

このプロジェクトはMITライセンスです。自由に使ってください！

## 🤝 貢献

バグ報告や機能リクエストは Issue でお願いします！

---

**作成者:** あなたの名前
**連絡先:** あなたのTwitterアカウント
