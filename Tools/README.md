# バージョン別サイトと操作動画の更新

## 編集する場所

バージョンの一覧、既定のバージョン、編集中のバージョンは `_versions/kotori/versions.json` に集約する。`latest` は既定の公開内容、`working` は現在編集する版を表す。現在は `latest: 1.1.2`、`working: 1.1.3`。1.1.3 はプレビューとして扱い、既定の入口へ自動昇格させない。

- `_versions/kotori/v<version>/`：各版の9ページのHTMLと、当時のCSS・JavaScript・画像・フォント。
- `_versions/kotori/v<version>/_partials/`：各版で固定したナビゲーションとフッター。
- `_partials/kotori/`：`working` だけに適用する編集中のナビゲーションとフッター。
- `_versions/kotori/version-ui.css` と `version-ui.js`：全版共通の小さなバージョン切替。
- `kotori/assets/guides/1.1.3/{ja,en}/`：言語別の実際の操作動画、ポスター、字幕、manifest。容量の大きい動画は各版へコピーせず、ここに一組ずつ保持する。

`kotori/*.html`、`kotori/main/`、`kotori/v*/` は生成物なので直接編集しない。1.1.3 の本文・FAQ・幅などを直す場合は `_versions/kotori/v1.1.3/` を編集する。操作動画カードの生成範囲外にある本文とFAQは、その版のHTML内で編集できる。

## 生成と確認

```sh
python3 _partials/sync.py --write
python3 Tools/build_guides.py
python3 Tools/build_versions.py
python3 _partials/sync.py --check --all
python3 Tools/build_guides.py --check
python3 Tools/build_versions.py --check
```

`sync.py` の既定対象は `working` だけ。過去の版を明示して確認する場合は `--check --version 1.1.0` を使う。過去の版は必ずその版の `_partials/` を使うので、現在のナビゲーションやバージョン番号で履歴を上書きしない。明示した版を同期するときだけ `--write --version <version>` を指定する。

`build_versions.py` は標準ライブラリだけで動作し、9ページすべてを各入口へ生成する。ローカルリンク、ページ内アンカー、画像、CSS内のフォント参照も確認する。`--check` は生成せず、真相源との不一致を検出する。Git、外部サービス、サーバー側のルーティングは生成・配信に不要。

| 入口 | 内容 |
| --- | --- |
| `/kotori/` とその各ページ | `latest` の完全なサイト |
| `/kotori/main/` とその各ページ | 同じ `latest` の完全なサイト |
| `/kotori/v1.0.0/` などとその各ページ | 指定した版の完全なサイト |
| `/kotori/v1.1.3/` | 1.1.3 のプレビュー |

ナビゲーション、言語切替、canonical、hreflang、通常の画像やCSSは閲覧中の版にとどまる。版の切替は同じページ・言語へ移動し、移動先に存在する場合だけ現在のアンカーを引き継ぐ。JavaScriptが無効でも版の切替と各ページは利用できる。新しい版を追加するときは完全な9ページと対応するアセットを用意し、registryへ追記して生成する。最新の正式版を変更するのは公開判断後に `latest` を更新したときだけ。

## 履歴の根拠

- 1.0.0：ウェブサイトのGit `d9fe639`。当時の `05-report.jpg` を含む実際のmainの最終スナップショット。
- 1.1.0：正式公開タグの `4638bd3`。未公開草稿 `d7a6321` は使わない。
- 1.1.1：独立したウェブサイトのスナップショットが存在しないため、1.1.0の内容とアセットを基に再構成。適用バージョンだけを変更し、Appの正式タグ `v1.1.1` にある日英の `fastlane/metadata/*/release_notes.txt` の4項目を追記する。画面の更新内容欄にも再構成であることを明記する。
- 1.1.2：ウェブサイトのGit `b97b94e` の内容。
- 1.1.3：現在のプレビュー。改修後の操作動画と幅を揃えたガイド。

1.0.1 は公開版として作らない。予定されていた内容は1.1.0に統合済み。各版の詳細な出典もregistryに残す。公開日をGitの日付から推定して追加しない。

## 操作動画の更新

`Tools/build_guides.py` は `_versions/kotori/v1.1.3/support-ja.html` と `support.html` の操作動画カードだけを生成する。

1. 実際に収録した動画・ポスター・日英字幕を `kotori/assets/guides/1.1.3/{ja,en}/` に置く。
2. 各言語の `manifest.json` を同じ場所に置く。
3. `python3 Tools/build_guides.py`、続けて `python3 Tools/build_versions.py` を実行する。
4. 日英の画面をそろえた最終確認では `python3 Tools/build_guides.py --check --require-english` を使う。
5. モバイルとデスクトップで動画、字幕、折りたたみ、検索、キーボード操作、版・言語切替、ページ幅を確認する。

各動画の `id` から `<id>.mp4`、`<id>.jpg`、`<id>.ja.vtt`、`<id>.en.vtt` を参照する。不足があれば生成を中止する。動画はクリック後に読み込み、ポスターだけ遅延読み込みする。JavaScriptがなくても手順と動画ファイルへのリンクを利用できる。英語の実画面の録画がまだない間は日本語動画を使い、英語ページにも日本語の画面であることを明記する。

動画は機能画面を開いた後から始まるため、`build_guides.py` の `ENTRY_POINTS` に日英の「開く場所」を記載する。実演範囲に説明が必要な動画は `SCOPE_NOTES` も更新する。入力音声の認識や共有の完了など、録画にない結果を完了したように書かない。

manifest の形式：

```json
{
  "app_version": "1.1.3",
  "ui_language": "ja",
  "clips": [
    {
      "id": "01-quick-entry",
      "title_ja": "ひとことで記録",
      "title_en": "Record an expense in a sentence",
      "duration": 32.5,
      "bytes": 1234567,
      "steps": [{"time": 0.0, "ja": "操作手順", "en": "An instruction"}],
      "source_take": "original-recording-reference"
    }
  ]
}
```

`duration` は秒、`bytes` は実際のMP4のサイズ、`steps[].time` は動画の先頭からの秒数。`source_take` は制作記録で、ページには表示しない。分類を明示する場合だけ動画へ `group` (`record` / `organize` / `review` / `data`) を追加できる。

### ショートカット動画の追加

既存の `01-quick-entry` から `17-voice-and-sharing-entry` までの17本は、元の順序ですべて残す。実際に収録して素材がそろったら、次の順序で末尾へ追加できる。

1. `18-shortcuts-tap`：ショートカットアプリでタップして実行する。
2. `19-shortcuts-home-screen`：自分用のショートカットをホーム画面に追加して実行する。
3. `20-shortcuts-siri-name`：自分用のショートカットを作り、Siriに呼びかけやすい短い名前を付ける。タイトルは「Siriに呼びかける名前を決める」／「Choose a short name for Siri」とする。

18だけ、18と19、18〜20の順次追加に対応する。途中を抜かす、並べ替える、元の17本を減らす構成は拒否する。追加する各動画には、日本語画面と英語画面の両方の収録が必要。日英manifestのID一覧が一致しない場合や、追加分があるのに英語manifestがない場合は、生成も `--check` も失敗する。旧17本だけの構成では、従来どおり英語manifestがない場合の日本語動画への切り替えを維持する。

3本とも既定の分類は「記録する」。`ENTRY_POINTS` にはiPhoneの「ショートカット」アプリを入口として登録してある。20は自分用のショートカットの作成と名称変更を紹介する設定動画とし、Siriからの実行やマイクによる音声認識は含まない。本文ではAppleの案内に沿ったSiriの呼び出し方を説明できるが、この収録で実行を確認したとは書かない。

### 動画ごとのアプリ版と収録環境

各clipに `app_version`、`app_build`、`source_commit`、`runtime` を指定できる。指定した値は、その動画についてだけmanifestのトップレベルの値に優先する。省略した項目はトップレベルの値を引き継ぐ。追加収録が別ビルドの場合は、この4項目を各clipに明記し、旧動画の出典を表すトップレベルの情報は書き換えない。

カードには、その動画の実際の `app_version` と画面言語を表示する。現在の対象版は引き続き1.1.3。日英の同じ動画では、継承後のアプリ版・ビルド・ソースコミットが一致することを検査する。旧manifestにないビルド情報を推測して補完はしない。`runtime` は各言語の実際の収録環境を記録するため、日英で異なっていてもよい。

### 日本語の用語チェック

記録操作には、App の文言マスターの `tab.chat`、`input.text`、記録アクション名と同じ「記録」を使う。画面名は「記録」画面と書く。日本語で「記帳」は使わない。中国語の文言にはこの制約を適用しない。

`build_guides.py` は日英両方の manifest 内の日本語タイトル・手順と日本語字幕を検査する。`build_versions.py` は全版の日本語ページを検査する。違反があると生成と `--check` のどちらも失敗する。元の録画や撮影情報は変更せず、字幕の時刻を保ったまま文言を修正する。既存版にも用語の訂正を反映するが、機能・日付・公開状態は変えない。

### 1.1.3 以降のガイド構成

1.1.3 以降は操作動画を中心に案内し、独立した文章の操作ガイドとそのページ内リンクは設けない。動画カード内の手順、よくある質問、お問い合わせは残す。機能紹介ページからは該当する動画カードへリンクする。以前の版の本文は変更せず、新しい版はこの構成を引き継ぐ。
