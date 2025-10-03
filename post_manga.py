# 漫画自動投稿 GitHub Actions ワークフロー
name: Post Manga Thread

on:
  # 定期実行: 毎週日曜日 12:00 UTC (日本時間 21:00)
  schedule:
    - cron: '0 12 * * 0'
  
  # 手動実行も可能にする
  workflow_dispatch:

jobs:
  post-manga:
    runs-on: ubuntu-latest
    
    steps:
    # リポジトリをチェックアウト
    - name: 📥 Checkout repository
      uses: actions/checkout@v3
    
    # Python環境をセットアップ
    - name: 🐍 Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    # 必要なライブラリをインストール
    - name: 📦 Install dependencies
      run: |
        pip install tweepy==4.14.0
    
    # 漫画投稿スクリプトを実行
    - name: 🚀 Post manga thread
      env:
        API_KEY: ${{ secrets.API_KEY }}
        API_SECRET: ${{ secrets.API_SECRET }}
        ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
        ACCESS_SECRET: ${{ secrets.ACCESS_SECRET }}
        BEARER_TOKEN: ${{ secrets.BEARER_TOKEN }}
      run: |
        python post_manga.py
    
    # ログファイルをアップロード(デバッグ用)
    - name: 📋 Upload logs
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: bot-logs
        path: '*.log'
        retention-days: 30
    
    # 投稿履歴を保存
    - name: 💾 Save post history
      if: success()
      uses: actions/upload-artifact@v4
      with:
        name: post-history
        path: 'post_history.json'
        retention-days: 90
