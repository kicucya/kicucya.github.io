# バージョン別サイトと操作動画の更新

## 更新范围与录制时机

官网更新的长期内容规则统一维护在 App 仓的 `docs/map/release/website.md`；本页维护源文件、生成命令和素材接入。
每轮先对照 App 版本差异与官网现状，列出保留、改文案、剪辑、重录、新增或下架项，并核对已有验收与取消决定。
新录或重录必须等少佐确认功能验收通过；短操作可用说明或 FAQ，已取消项不再计为欠项。批量更新按功能积累和内容过时情况触发，不设固定周期。

## 編集する場所

バージョンの一覧、既定のバージョン、編集中のバージョンは `_versions/kotori/versions.json` に集約する。`latest` は現在公開されている最新の App バージョンに対応し、`working` は開発中の版を表す。現在は `latest: 1.2.0`、`working: 1.2.2`。各版の App は `/kotori/v<version>/` の対応するサイトを開く。開発中の版のサイトも公開できるが、それだけで既定の入口や App の公開状態を変更しない。26/09/27 に少佐が再確認したこのルールを現行の基準とし、App の公開前に既定の版だけを先行して切り替える以前の運用は適用しない。公開ページのバージョン表示にはプレビュー表記を付けない。

- `_versions/kotori/v<version>/`：各版の9ページのHTMLと、当時のCSS・JavaScript・画像・フォント。
- `_versions/kotori/v<version>/_partials/`：各版で固定したナビゲーションとフッター。
- `_partials/kotori/`：`working` だけに適用する編集中のナビゲーションとフッター。
- `_versions/kotori/version-ui.css` と `version-ui.js`：全版共通の小さなバージョン切替。
- `kotori/assets/guides/1.1.3/{ja,en}/`：言語別の実際の操作動画、ポスター、字幕、manifest。容量の大きい動画は各版へコピーせず、ここに一組ずつ保持する。

`kotori/*.html`、`kotori/main/`、`kotori/v*/` は生成物なので直接編集しない。現在の本文・FAQ・幅などを直す場合は `_versions/kotori/v1.2.2/` を編集する。操作動画カードの生成範囲外にある本文とFAQは、その版のHTML内で編集できる。

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
| `/kotori/v1.1.3/` | 公開済み App 1.1.3 のサイト |
| `/kotori/v1.2.0/` | 現在の既定の入口と同じ内容 |

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

按上述内容规则选定且已由少佐验收的用户任务，分别录制日英真实画面，补齐双语字幕、海报、实际版本／构建／源码来源，接入对应版本指南并检查播放与窄屏显示。测试或截图不能代替教程交付；发布授权遵循上面的「更新の完了範囲」。

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

1.1.3 の元の manifest では、`01-quick-entry` から `17-voice-and-sharing-entry` までの17本を元の順序ですべて残す。実際に収録して素材がそろったら、次の順序で末尾へ追加できる。

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

Place `NEW` at the upper left of feature description cards for capabilities added since 1.1.3: recurring entries in chat, exchange rates and final charges, reminders, appearance, copying entries, manual AI categorization, and the pending-count control. Weekly schedules already existed in 1.1.3; do not label them as a separate new capability. Existing calculation input, keyword management, reports, and Home Screen shortcuts are not new to 1.2.0. Keep the historical pages and the default 1.1.3 entry unchanged.

### Reminders (1.2.0)

`26-bookkeeping-reminders` briefly shows how to open reminder settings, set a time and repeat days for one reminder, and enable it. Keep this tutorial to basic setup; daily, weekday, and weekend summary variants belong in UI regression checks, not additional tutorial steps. Times and weekdays sync with iCloud; notification switches remain local, and new reminders start off. The Japanese and English recordings show the settings flow on a signed-out simulator; they do not establish cross-device CloudKit delivery. Keep the existing clips’ provenance and attach this recording’s actual build and commit to its own manifest entry. Version 1.2.0 requires its first two guides and accepts subsequent feature guides in their defined order while other features are still being recorded.

1.2.0 のホーム画面ガイド `19-shortcuts-home-screen` は、同版の manifest にある新しい日英動画を優先する。1.1.3 の同名動画・字幕・出典は変更しない。コントロールセンターでは「ショートカットを実行 → Kotori → 記録を追加」を選ぶ。どちらも追加後にシステムの入力画面から保存する流れを紹介する。


### 1.2.0 の動画差し替え（26/10/07）

1.2.0 の manifest に同じ ID の動画がある場合、その版だけで優先する。09は1.1.3の動画を29秒から切り出し、別名を選んで関連付ける操作と結果だけを残す。撮影版・ビルドは1.1.3のまま保存し、切り出した範囲と元ファイルのハッシュを `edit` に記録する。12は開始日と初回の記録日、16は給料日に合わせる集計期間、22は連動するレートと請求額、25はアプリ全体の外観に更新する。27は記録のコピーを紹介する。14と17は1.2.0のカードと検索から除外し、1.1.3の素材と本文は残す。

`RECORDING_IDS_120` は追加素材の許容順序を定義する。存在する完全な日英セットだけを読み込む。`scope_note` を動画ごとに指定すると、旧版向けの注記を上書きできる。空のオブジェクトは旧注記を表示しない指定。16は `group: review` として集計期間の案内に含める。

26/10/07に09、12、16、22、25、27の日英素材を反映し、1.2.0は24本を表示する。同日、少佐の決定によりB（28、未分類の記録を分類する動画）の収録を取りやめた。今回の更新に収録待ちはない。AI分類の機能説明は残し、動画と動画へのリンクは追加しない。失敗した試行は採用していない。

文言はAppの表示名と既存ガイドの用語を基準にした。「コピー」／Copy、長押しの説明はAppleの [日本語ガイド](https://support.apple.com/ja-jp/guide/iphone/iph1a9cae52c/ios) と [英語ガイド](https://support.apple.com/guide/iphone/select-edit-and-move-text-iph1a9cae52c/ios) で確認した。Xでは「家計簿 給料日 締め日」「家計簿 明細 コピー」「海外旅行 カード 請求額 為替レート」と英語の対応語を検索し、[日本語の「給料日から給料日」](https://x.com/Coco_kimama/status/2072728635711402212)、[英語の budget for the month / next payday](https://x.com/another_wurld/status/2107326971839443407) を用例として確認した。英語の duplicate transactions は二重計上の文脈が多く、操作名には採用していない。カードの最終請求額を表す英語の完全一致検索では適切な個人投稿が見つからず、製品の既存表現と実際の画面を優先した。

新しい動画には実際のApp 1.2.0、build 1528、製品ソース `a581ff598aa976f1bd803a12338aa7ae30f02313` を動画単位で記録する。録画後の字幕時刻の確認内容とポスターの選択理由も残す。既存のmanifestの先頭にある古い動画の出典は書き換えない。原片、XCTestの結果、比較用の画像は収録ごとの一時ディレクトリに保存する。

### 1.2.0 の紹介・動画更新（26/10/13）

少佐が機能の確認を終え、A–Hと毎日の支出通知の動画を承認した範囲。05・06は現在のカテゴリ編集と保存、07は使用中の財布の名前変更、11は対象の財布と予算アラート、25は写真のチャットアイコン、26は通知の共通入口を含む日英の新しい録画へ差し替える。29は毎日の支出通知を設定し、実際のバナーから当日の明細を開く新規動画。1.2.0は日英それぞれ25テーマになる。

チャットのお知らせは文字のメッセージで、タップして明細を開く機能はない。明細への操作はバナーとiOSの通知を案内する。ショートカットの財布はFAQと19・24の補足に追加し、既存の動画を使う。予算の対象財布、事前・見込み・超過の通知、写真のアイコンを日英の機能紹介とFAQにも反映する。今回の29は、以前取りやめた28のAI分類動画とは別のテーマ。14・17・18・28を復活させない。

新しい7本の撮影元はApp 1.2.0、build 1556、製品ソース `791e1a06f595e1802e0c5ee7abd1420fa64cdbb2`。日英とも専用のiPhone 17 Pro MaxシミュレータとiOS 27.0を使用し、各clipに実際の端末名、成功take、撮影方法のハッシュ、字幕の確認とポスター選択を記録する。古い動画の出典を表すmanifest全体の情報は維持する。

トップページの財布・予算画像を更新し、支出のお知らせと写真のチャットアイコンを追加する。画像は実際の録画またはXCTestのスクリーンショットから縮小したもの。財布は07、予算は11、アイコンは25、チャットのお知らせは29の別途実行した画面を使う。元のUIを書き換えたり、結果を合成したりしない。

機能紹介からFAQへ進むリンクは、該当する回答を自動で開く。スマートフォンの固定ナビゲーションに質問が隠れない位置へ移動する。更新したガイド用CSS・JavaScriptは内容のハッシュをURLに付け、以前のキャッシュと区別する。過去のページに出る差分は、版の切り替えメニューが持つ1.2.0の新しいアンカー情報だけで、本文と動画は変えない。

用語はAppの文言マスターと既存ガイドを基準にし、[Zaimの予算通知](https://content.zaim.net/manuals/show/63)、[Spendeeの予算案内](https://help.spendee.com/article/131-budget-my-money)、[Appleの写真調整](https://support.apple.com/ja-jp/guide/iphone/iph0f3ebb1dd/ios)を確認した。Xでは「家計簿 1日の上限 通知」「予算オーバー」「spending alerts」「daily spending limit」「アイコン トリミング」と英語の写真選択・切り抜き表現を検索。[1日の上限という個人の用例](https://x.com/karpador3cat/status/2107720189647442142)、[spending alertsというサービス側の用例](https://x.com/IFTTT/status/2050991275583979578)、[アイコンのトリミングという個人の用例](https://x.com/coconoka__/status/2109865398284005511)を参考にした。家計簿の毎日の到達通知や写真アイコンに完全に一致する個人投稿は十分に見つからず、隣接する表現と区別して扱った。英語のdaily spending limitはカードの利用制限にも使われるため、ことりでは記録額に対するお知らせだと説明する。

### 個別の背景設定ガイド更新（26/10/14）

少佐の再収録指示により、1.2.0 の25だけを新しい日英の動画へ差し替える。確認したAppの範囲は前回の `791e1a06f595e1802e0c5ee7abd1420fa64cdbb2` から `a4ceaab9cdd282c7641060b8a255f799d400378d`。背景操作の変更は `84c2c0f4` に含まれる。カラー背景、写真の選択と調整、写真に重ねる色と不透明度の即時プレビュー、チャットアイコン、保存後の各画面を紹介する。背景欄の「デフォルト」と、写真の0%・100%の見え方はFAQで説明する。

撮影元はApp 1.2.0 build 1558、製品ソース `a4ceaab9cdd282c7641060b8a255f799d400378d`。日英の専用iPhone 17 Pro Max、iOS 27.0（24A434）を使用。撮影時に未コミットだった収録手順は、clipの `recording_script` にメソッドのハッシュを残す。原片を先頭からデコードして字幕時刻を補正し、元の時刻も保存する。ポスターは保存後の記録画面から選択する。

日英の機能紹介、背景FAQ、トップページの外観画像も更新する。画像は同じ成功したXCTestからの実画面を縮小したもの。旧版・既定の1.1.3・他の動画は維持し、14・17・18・28は復活させない。1.2.0は25テーマのまま。これは背景UI変更への追随で、新しい `NEW` は増やさない。今回の交付範囲はローカルの `app-1.2.0`。

用語はAppの表示とAppleの[日本語の不透明度説明](https://support.apple.com/ja-jp/guide/keynote-ipad/tancd12cd752/ipados)・[英語の説明](https://support.apple.com/guide/keynote/change-object-transparency-tancd12cd752/mac)に合わせた。Xでは[カラーレイヤーを重ねて不透明度を調整する個人の用例](https://x.com/kanaboshi0513/status/1899358311260250131)と[solid color overlayの個人の用例](https://x.com/ju1fy/status/2102234024140030025)を確認。写真編集の隣接した文脈であり、ことりの操作そのものの用例とは扱わない。英語のphoto overlayだけでは別の写真を重ねる意味にもなるため、重ねる対象が色であると明記した。


### 1.2.1 官网补齐与发布（26/10/17）

网站基线为 `e237b274b7b3c2a3eb7d8579729ea5835e9d69c0`；核对 App 范围为正式 `v1.2.0`（`a2ddfe4d`）至 `Dev@5a92c33b`。产品差异仅为预算锁位置、数值确认后自动上锁、锁定后金额仍可编辑；App 行为依据 `docs/map/product/budget-and-recurring.md` 与 26/10/16 的预算回归结果。发布授权为少佐本轮“把1.2.1官网补齐发布”。

| 用户任务／页面 | 处理与依据 |
| --- | --- |
| 打开对应版本官网与 App 用法 | 从 1.2.0 建立完整九页独立源码、资源和版本入口，`working` 改为 1.2.1；不从过审推定 App 已公开，`latest` 保持 1.1.3。 |
| 预算分配和锁定 | 11-budget 改为日英文字步骤，保留钱包范围、总预算、预警和保存说明，明确分类名左侧的小锁、确认自动上锁、数字仍可编辑及手动解锁。短操作无需录制；旧预算视频与首页预算截图仅从 1.2.1 的展示中移除。 |
| 功能介绍、FAQ 与 NEW | 更新预算介绍和锁定 FAQ，链接直达步骤；按最新已上线的 1.1.3 保留适用的 NEW 标签，预算交互修正不单独标为新增功能。 |
| 其余教程与截图 | 核对 App 差异后继续复用，1.2.1 共 25 项指南（24 段视频、1 项文字步骤）；媒体保留原 1.1.3／1.2.0 的真实来源，不改拍摄版号。取消的 14／17／18／28 不恢复。 |

`text-guides.json` 是当前版本短操作说明的源码，只能替换已有指南 ID，必须提供日英标题、步骤及适合混合图文／视频的指南列表介绍与数量标签。`Tools/build_guides.py` 继续统一生成卡片、搜索和锚点，文字卡不输出旧视频、海报、时长或拍摄来源；无此文件的历史版本保持原生成结果。

本次术语依 App 的 `budget.*` 显示与 Apple 的[日语数值输入说明](https://support.apple.com/ja-jp/119889)、[英语数值输入说明](https://support.apple.com/en-us/119889)、[日语滑条说明](https://support.apple.com/ja-jp/guide/numbers-iphone/tanc8e2eb44e/ios)、[英语滑条说明](https://support.apple.com/guide/iphone/use-voiceover-gestures-iph3e2e2281/27/ios/27)、[日语锁图标说明](https://support.apple.com/ja-jp/102537)、[英语锁图标说明](https://support.apple.com/en-us/102537)核对。仅复用数值キーボード／numeric keyboard、スライダ／slider、カギのアイコン／lock icon 等操作表达；预算行为来自本产品源码，不从这些相邻产品推定。当前宿主未提供 Grok／X 搜索能力，本轮只使用网页证据。详细取证与验证产物保存在本次独立临时目录。

### 默认入口切换至 1.2.0（26/10/17）

按少佐本轮明确指示“默认入口改1.2.0”，将 `latest` 从 1.1.3 切换为 1.2.0，并重新生成 `/kotori/` 与 `/kotori/main/`。`working` 继续为 1.2.1，各版独立页面和媒体来源不变。本次指示只确认官网入口，不据此改写 App Store 发布状态或推定上线日期。

### 1.2.1 build 1593 UI 更新（26/10/25）

App 基线固定为 `6b8589a6b5ac0b4b96445262d4a414a62903a1be`，1.2.1（1593）；与上一轮 App 参考 `5a92c33b` 比较。少佐确认当前 UI 看起来没有问题后，按本轮授权录制、更新并发布官网。默认入口继续为 1.2.0，网站更新不证明 App Store 或 TestFlight 发布状态。

- 新录日英 05 分类编辑、06 分类显隐排序、07 钱包创建／改名、10 报表／饼图／预算明细、16 月度起点设置、25 外观；新增 30 记录设置／历史范围／闲聊。均使用独立 iPhone 17 Pro Max 模拟器、iOS 27.0（24A434）和合成本地数据；每段保留实际产品源码、构建、原片哈希、成功 take、字幕和海报来源。
- 1.2.1 媒体叠加层位于 `kotori/assets/guides/1.2.1/{ja,en}/`，只在对应版本替换同 ID。20 的画面保持原录制来源，仅修正已经搬迁的入口字幕；19、20 的当前入口是「その他 → 記録 → 記録を追加 / Siri」／「More → Recording → Record Entry / Siri」。
- 11 预算继续使用文字步骤；当前预算和报表截图重新拍摄。记录设置／历史、饼图详情和外观等图片只更新 1.2.1 的 `assets/screens`，来源清单为同目录 `refresh-1593.json`。
- 输入、转账、周期、关键词、汇率、提醒、导入导出、复制的现有正常操作流程仍适用；保留原拍摄版本，不将内部修复或底层同步机制包装成新功能。共享钱包改名、历史分类和错误反馈通过介绍与 FAQ 说明，本轮本地录像不证明 CloudKit 投递。
- 取消的 14／17／18／28 不恢复。1.2.1 共有 26 项指南（25 段视频、1 项文字）；旧版本正文与素材保持不变，生成的版本切换栏仅更新新指南锚点。旧版 NEW 标记移除，新记录显示设置使用 NEW。

用语证据沿用 App 现行文案与既有「記録」裁决，并参考 Apple 的[按期间查找历史](https://support.apple.com/ja-jp/118212)、[隐藏与删除的区别](https://support.apple.com/ja-jp/108091)和 YNAB 的[报表与分类明细说明](https://www.ynab.com/blog/ynab-reports-and-data)。这些来源只支持邻近操作用语，功能事实由本产品源码和真实录制确认。Grok CLI 已尝试，但因未登录未能完成 X 搜索，未将其记作有效证据。

商店草稿和对外更新日志在 App 仓 `fastlane/drafts/1.2.1-1593/`，不属于官网发布内容；本轮不向 ASC 上传，也不发布更新日志。

### 1.2.1 build 1623 截图定向更新（26/10/28）

按少佐「更新变化过的121截图」及同范围 Main 发布授权执行。固定产品源码为 `215562fb4e4a49e6cd49a886b4ae5ed94aededc0`，App 1.2.1（1623）。与现有 1593 图片逐项比较后，只替换首页引用的 14 张过时截图：日文 01、03、04、05、05-detail、06、07、25、29；英文 01、25、29、30-recording-settings、30-history-options。其余截图保留。

截图由 mini 的 agents 后台会话复用已登记无账号 iPhone 17 Pro（iOS 27.0）执行 XCTest；使用合成账本及仓库 misty-lake 夹具，不展示测试员照片或真实用户数据。真实截图原尺寸为 1206×2622，网页图片仅等比缩小为 660×1435；未绘制、重排或补写 UI。逐图来源、哈希、尺寸、语言及实际源码见 `assets/screens/refresh-1623.json`。明暗产物分别保留，当前网页沿用浅色画面。

首轮照片准备漏了现有隔离库门控，实际生成默认背景；这些图片未被作为外观图片采用。修正的仅是本次临时截图 harness，重新执行两条受影响的截图路径。首轮有效的默认背景聊天截图继续使用。原始 XCTest 的明暗各四项均通过；首轮汇总脚本对主测试类名称的规范化不一致，原始结果与说明分别保留，没有改写失败标记冒充成功。

英日功能介绍及背景 FAQ 的术语机械同步到 App 已确定的 `appearance.opacity`：日文「カラーオーバーレイの強さ」、英文「Color overlay strength」。未新增译文，0%／100% 的既有说明保持。旧视频里的操作步骤和旧标签仍按其真实拍摄来源保留，本轮不修改视频、封面、字幕或商店素材。

`latest` 仍为 1.2.0；1.2.0 及更早版本源文件、默认站点和历史媒体不变。本次仅发布 1.2.1 图片与直接关联文字，不代表 App Store 上线、TestFlight 上传或新功能发布。原始截图、XCTest、harness patch 和验证回执在 `/tmp/kotori-web-121-1623/`；mini 工作区分别为 `/Users/agents/Workspaces/kotori/website-121-1623-20261027/` 和 `/Users/agents/Workspaces/kotori/website-121-1623-photo-20261027/`。

日文 `02-siri.jpg` 后续补查已定位：原流程在进入页面 1.2 秒后截图，截到了系统 SiriTipView 加载占位。等待 20 秒后，原生提示语在打开 Shortcuts 前即已恢复，明暗均确认；最终流程等待真实提示语出现，并通过现有关闭按钮清除合成预算横幅。第 15 张已补拍并接入，连同首批 `d36f954` 的 14 张，本轮共更新 15 张；原生提示语与网页最终像素均通过检查。没有复制证书、修改产品代码或扩展账号权限。专项证据见 `/tmp/kotori-web-121-1623/siri-ready-results/`。
