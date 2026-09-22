# 操作動画の更新

`kotori/support-ja.html` と `kotori/support.html` の操作動画一覧は、`build_guides.py` で生成する。既存の文章・FAQ は生成範囲の外にあり、ページ内で編集できる。

1. 実際に収録した動画・ポスター・字幕を `kotori/assets/guides/1.1.3/ja/` に置く。
2. `manifest.json` を同じ場所に置き、`python3 Tools/build_guides.py` を実行する。
3. `python3 Tools/build_guides.py --check` と `python3 _partials/sync.py --check` で生成物を確認する。
4. モバイルとデスクトップで動画の開始、字幕、折りたたみ、検索、キーボード操作を確認する。

各動画の `id` を基に、`<id>.mp4`、`<id>.jpg`、`<id>.ja.vtt`、`<id>.en.vtt` を参照する。ファイルが欠けている場合は生成を中止する。動画はクリック後に読み込み、ポスターのみ遅延読み込みする。JavaScript がなくても手順を読んだり、動画ファイルを直接開いたりできる。

動画は機能画面を開いた後から始まるため、`build_guides.py` の `ENTRY_POINTS` に日英の「開く場所」を記載する。画面名は実際のアプリと照合する。実演の範囲に説明が必要な動画は、同ファイルの `SCOPE_NOTES` も更新する。

manifest の形式：

```json
{
  "app_version": "1.1.3",
  "ui_language": "ja",
  "clips": [
    {
      "id": "01-quick-entry",
      "title_ja": "ひとことで記帳",
      "title_en": "Record an expense in a sentence",
      "duration": 32.5,
      "bytes": 1234567,
      "steps": [{"time": 0.0, "ja": "操作手順", "en": "An instruction"}],
      "source_take": "original-recording-reference"
    }
  ]
}
```

`duration` は秒、`bytes` は実際の MP4 のサイズ、`steps[].time` は動画の先頭からの秒数。`source_take` は制作記録として保持し、公開ページには表示しない。必要な場合だけ、動画に `group` (`record` / `organize` / `review` / `data`) を追加して分類を指定できる。

ページ共通のナビゲーション・適用バージョンは引き続き `_partials/` が真相源。新しい動画を公開する際は、アプリの公開バージョンとサイトのブランチをそろえる。
