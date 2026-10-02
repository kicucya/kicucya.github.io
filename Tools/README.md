# バージョン別サイトと操作動画の更新

## 編集する場所

バージョンの一覧、既定のバージョン、編集中のバージョンは `_versions/kotori/versions.json` に集約する。`latest` は現在公開されている最新の App バージョンに対応し、`working` は開発中の版を表す。現在は `latest: 1.1.3`、`working: 1.2.0`。各版の App は `/kotori/v<version>/` の対応するサイトを開く。開発中の版のサイトも公開できるが、それだけで既定の入口や App の公開状態を変更しない。26/09/27 に少佐が再確認したこのルールを現行の基準とし、App の公開前に既定の版だけを先行して切り替える以前の運用は適用しない。公開ページのバージョン表示にはプレビュー表記を付けない。

- `_versions/kotori/v<version>/`：各版の9ページのHTMLと、当時のCSS・JavaScript・画像・フォント。
- `_versions/kotori/v<version>/_partials/`：各版で固定したナビゲーションとフッター。
- `_partials/kotori/`：`working` だけに適用する編集中のナビゲーションとフッター。
- `_versions/kotori/version-ui.css` と `version-ui.js`：全版共通の小さなバージョン切替。
- `kotori/assets/guides/1.1.3/{ja,en}/`：言語別の実際の操作動画、ポスター、字幕、manifest。容量の大きい動画は各版へコピーせず、ここに一組ずつ保持する。

`kotori/*.html`、`kotori/main/`、`kotori/v*/` は生成物なので直接編集しない。現在の本文・FAQ・幅などを直す場合は `_versions/kotori/v1.2.0/` を編集する。操作動画カードの生成範囲外にある本文とFAQは、その版のHTML内で編集できる。

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
| `/kotori/v1.1.3/` | 公開済み App 1.1.3 のサイト（既定の入口と同じ内容） |

ナビゲーション、言語切替、canonical、hreflang、通常の画像やCSSは閲覧中の版にとどまる。版の切替は同じページ・言語へ移動し、移動先に存在する場合だけ現在のアンカーを引き継ぐ。JavaScriptが無効でも版の切替と各ページは利用できる。新しい版を追加するときは完全な9ページと対応するアセットを用意し、registryへ追記して生成する。新しい App バージョンの公開が確認されたら、その版の `status` と `latest` を合わせて更新する。開発版サイトの公開だけでは `latest` を変更しない。App内の操作ガイドはインストール中の版に対応する `/kotori/v<version>/` を使うため、既定の入口と分けて維持する。

## 更新の完了範囲

バージョン別サイトの内容更新と既定の入口の切り替えは別に扱う。対応する `app-<version>` にコミットし、同じ範囲のウェブサイトの統合・push が許可されていれば、`main` への統合、push、公開ページの確認まで完了する。同じ許可を重ねて求めない。内容やルールの修正依頼だけから公開の許可を推定しない。下書きまたはローカルプレビューだけと明示された場合は公開しない。ウェブサイトの公開に App リポジトリの統合・push、TestFlight へのアップロード、App Store への審査提出は含まれない。

## 履歴の根拠

- 1.0.0：ウェブサイトのGit `d9fe639`。当時の `05-report.jpg` を含む実際のmainの最終スナップショット。
- 1.1.0：正式公開タグの `4638bd3`。未公開草稿 `d7a6321` は使わない。
- 1.1.1：独立したウェブサイトのスナップショットが存在しないため、1.1.0の内容とアセットを基に再構成。適用バージョンだけを変更し、Appの正式タグ `v1.1.1` にある日英の `fastlane/metadata/*/release_notes.txt` の4項目を追記する。画面の更新内容欄にも再構成であることを明記する。
- 1.1.2：ウェブサイトのGit `b97b94e` の内容。
- 1.1.3：公開済み App に対応する既定のサイト。App の公開は26/09/26に少佐が確認済み（App リポジトリの `docs/release/history.md`）。正確な公開時刻は推定しない。

1.0.1 は公開版として作らない。予定されていた内容は1.1.0に統合済み。各版の詳細な出典もregistryに残す。公開日をGitの日付から推定して追加しない。

## 操作動画の更新

ユーザー向けの新機能には、日本語と英語の実画面による操作動画を必ず用意する。両言語の字幕、ポスター、実際の収録版・ビルド・ソース情報をそろえ、対応する版のガイドへ追加して再生とモバイル表示を確認する。Appのテストやスクリーンショットだけで動画の追加を済ませたことにはしない。公開に関する許可は上記の「更新の完了範囲」に従う。

`Tools/build_guides.py` は registry の `working` 版の `support-ja.html` と `support.html` の操作動画カードを生成する。`--version 1.1.3` のように過去の版を明示できる。1.2.0以降はホーム画面のショートカットとSiriの準備を先頭に表示する。manifestの収録順・元の動画・撮影版は変更しない。

1. 実際に収録した動画・ポスター・日英字幕を `kotori/assets/guides/1.1.3/{ja,en}/` に置く。
2. 各言語の `manifest.json` を同じ場所に置く。
3. `python3 Tools/build_guides.py`、続けて `python3 Tools/build_versions.py` を実行する。
4. 日英の画面をそろえた最終確認では `python3 Tools/build_guides.py --check --require-english` を使う。
5. モバイルとデスクトップで動画、字幕、折りたたみ、検索、キーボード操作、版・言語切替、ページ幅を確認する。

各動画の `id` から `<id>.mp4`、`<id>.jpg`、`<id>.ja.vtt`、`<id>.en.vtt` を参照する。不足があれば生成を中止する。各ファイルの内容から作ったハッシュを URL の `?v=` に付け、再収録や字幕修正の後に古い素材がキャッシュから使われるのを防ぐ。素材を変更したら両方の生成コマンドを実行する。変更したファイルだけ URL が変わることは `python3 Tools/test_guide_media_cache.py` で確認できる。動画はクリック後に読み込み、ポスターだけ遅延読み込みする。JavaScriptがなくても手順と動画ファイルへのリンクを利用できる。英語の実画面の録画がまだない間は日本語動画を使い、英語ページにも日本語の画面であることを明記する。

`build_guides.py` の `ENTRY_POINTS` に、動画の開始画面へ進むための日英の「開く場所」を記載する。App に移動先を開くボタンがある場合は、そのボタンから実演を始める。ホーム画面のガイドは3つのプリセットを長押しして追加する流れを使い、自分用のショートカット作成は Siri の短い名前を設定するガイドに限る。1.1.3以降では、削除済みの動画18や独立した「文章で確認する」の導線を戻さない。実演範囲に説明が必要な動画は `SCOPE_NOTES` も更新する。入力音声の認識や共有の完了など、録画にない結果を完了したように書かない。

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

`duration` は秒、`bytes` は実際のMP4のサイズ、`steps[].time` は動画の先頭からの秒数。`source_take` は制作記録で、ページには表示しない。分類を明示する場合だけ動画へ `group` (`control-center` / `record` / `organize` / `review` / `data`) を追加できる。

### ショートカット動画の追加

既存の `01-quick-entry` から `17-voice-and-sharing-entry` までの17本は、元の順序ですべて残す。実際に収録して素材がそろったら、次の順序で末尾へ追加できる。

1. `19-shortcuts-home-screen`：Kotoriの「その他 → 記録を追加 / Siri」で、既存のショートカットボタンをタップするところから始める。直接開いたKotoriのページで、3つのプリセットのうち使いたい記録方法を長押しして、ホーム画面に追加する。次回からは追加したアイコンをタップして記録する。ショートカットの作成・編集やアイコンのカスタマイズは案内に含めない。タイトルは「アプリを開かずに記録：ホーム画面のショートカット」／「Record without opening the app: Home Screen shortcut」とする。
2. `20-shortcuts-siri-name`：自分用のショートカットを作り、Siriに呼びかけやすい短い名前を付ける。タイトルは「アプリを開かずに記録：Siriで使う準備」／「Record without opening the app: Set up a Siri phrase」とする。

19だけ、19と20の順次追加に対応する。18のショートカットアプリ内で実行する動画は公開対象から外した。途中を抜かす、並べ替える、元の17本を減らす構成は拒否する。追加する各動画には、日本語画面と英語画面の両方の収録が必要。日英manifestのID一覧が一致しない場合や、追加分があるのに英語manifestがない場合は、生成も `--check` も失敗する。旧17本だけの構成では、従来どおり英語manifestがない場合の日本語動画への切り替えを維持する。

2本とも既定の分類は「記録する」。`ENTRY_POINTS` は19をKotori内の「その他 → 記録を追加 / Siri」、20をiPhoneの「ショートカット」アプリとして登録する。20は自分用のショートカットの作成と名称変更を紹介する設定動画とし、Siriからの実行やマイクによる音声認識は含まない。本文ではAppleの案内に沿ったSiriの呼び出し方を説明できるが、この収録で実行を確認したとは書かない。

### 動画ごとのアプリ版と収録環境

1.2.0 の `23-control-center-pending` はコントロールセンターの分類で、`24-control-center-record` の次に表示する。コントロールセンターでKotoriの未確認コントロールを追加し、横に広げて件数を表示する。タップして内容を確認し、一括確認後に件数が減る実際の流れを日英それぞれのシステム画面で収録する。アプリを開かずに入力する新しいコントロールは、この動画の対象に含まない。

1.2.0 の `22-exchange-rates` はレポートの動画の直後に表示する。レポートから外貨の記録を日付ごとに確認し、すべての記録とレート未設定の記録を切り替える。通貨で絞り込み、1件ずつレートやカードの最終請求額を入力できる。共通のレートを使う記録には一括入力を使う。素材は `kotori/assets/guides/1.2.0/{ja,en}/` に追加し、先に収録した動画21の出典は変更しない。

1.2.0 の追加動画 `21-chat-recurring` は `kotori/assets/guides/1.2.0/{ja,en}/` の独立した manifest と素材を使う。「固定費・定期収入を登録する」の直後に「チャットで固定費・定期収入を追加する」を表示する。記録画面から毎月の家賃を送り、開始時期に「来月から」を選び、確認して登録したあと、固定費・定期収入の一覧で確認する。1.1.3 以前のガイドには追加しない。日英両方の実画面を収録し、既存動画の出典と既定の公開バージョンは維持する。

各clipに `app_version`、`app_build`、`source_commit`、`runtime` を指定できる。指定した値は、その動画についてだけmanifestのトップレベルの値に優先する。省略した項目はトップレベルの値を引き継ぐ。追加収録が別ビルドの場合は、この4項目を各clipに明記し、旧動画の出典を表すトップレベルの情報は書き換えない。

カードには、その動画の実際の `app_version` と画面言語を表示する。1.2.0の案内でも既存動画の撮影版1.1.3をそのまま表示する。日英の同じ動画では、継承後のアプリ版・ビルド・ソースコミットが一致することを検査する。旧manifestにないビルド情報を推測して補完はしない。`runtime` は各言語の実際の収録環境を記録するため、日英で異なっていてもよい。

### 日本語の用語チェック

記録操作には、App の文言マスターの `tab.chat`、`input.text`、記録アクション名と同じ「記録」を使う。画面名は「記録」画面と書く。日本語で「記帳」は使わない。中国語の文言にはこの制約を適用しない。

`build_guides.py` は日英両方の manifest 内の日本語タイトル・手順と日本語字幕を検査する。`build_versions.py` は全版の日本語ページを検査する。違反があると生成と `--check` のどちらも失敗する。元の録画や撮影情報は変更せず、字幕の時刻を保ったまま文言を修正する。既存版にも用語の訂正を反映するが、機能・日付・公開状態は変えない。

### 1.1.3 以降のガイド構成

1.1.3 以降は操作動画を中心に案内し、独立した文章の操作ガイドとそのページ内リンクは設けない。動画カード内の手順、よくある質問、お問い合わせは残す。機能紹介ページからは該当する動画カードへリンクする。以前の版の本文は変更せず、新しい版はこの構成を引き継ぐ。

### Control Center recording (1.2.0)

The final decision on 26/09/28 supersedes the native recording control: Kotori keeps only its pending-count control. Guide `23-control-center-pending` remains applicable. Guide `24-control-center-record` must show adding the system Shortcuts control, choosing Kotori’s existing Record Entry action, and using it. It must not ask for a personal shortcut with the fixed name `Kotori`, or present a native Kotori recording control. The Home Screen guide must also show adding and using the shortcut. Record the replacement flows separately in Japanese and English; keep the original recordings’ provenance until their actual replacements exist.

On 26/09/28, commit 7c73fba replaced guide 24 and the 1.2.0 Home Screen guide with separate Japanese and English recordings of the system Shortcuts flows, including actual entry and saving. The withdrawn native-control recording is no longer the current guide. Commit 39d5111 corrected player sizing to preserve the video aspect ratio. Control Center remains the first entry method in the 1.2.0 introduction, followed by Home Screen.

### New-feature labels (1.2.0)

Place `NEW` at the upper left of feature description cards for capabilities added since 1.1.3: recurring entries in chat and weekly schedules, exchange rates and final charges, reminders, appearance, and the pending-count control. Existing calculation input, keyword management, reports, and Home Screen shortcuts are not new to 1.2.0. Keep the historical pages and the default 1.1.3 entry unchanged.

### Reminders (1.2.0)

`26-bookkeeping-reminders` briefly shows how to open reminder settings, set a time and repeat days for one reminder, and enable it. Keep this tutorial to basic setup; daily, weekday, and weekend summary variants belong in UI regression checks, not additional tutorial steps. Times and weekdays sync with iCloud; notification switches remain local, and new reminders start off. The Japanese and English recordings show the settings flow on a signed-out simulator; they do not establish cross-device CloudKit delivery. Keep the existing clips’ provenance and attach this recording’s actual build and commit to its own manifest entry. Version 1.2.0 requires its first two guides and accepts subsequent feature guides in their defined order while other features are still being recorded.

1.2.0 のホーム画面ガイド `19-shortcuts-home-screen` は、同版の manifest にある新しい日英動画を優先する。1.1.3 の同名動画・字幕・出典は変更しない。コントロールセンターでは「ショートカットを実行 → Kotori → 記録を追加」を選ぶ。どちらも追加後にシステムの入力画面から保存する流れを紹介する。
