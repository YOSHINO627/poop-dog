# POOP DOG

公開URL: https://poop-dog.vercel.app/  
GitHub: https://github.com/YOSHINO627/poop-dog

2026-09-08にGitHub登録・Vercel本番公開を完了。`main`への変更でGitHub ActionsとVercelの自動デプロイが実行されます。Vercel Teamは `YOSHINO627`（URL slug: `yoshino-627`）、Projectは `poop-dog` です。

Python + Pyxelで実装した256×144の横スクロール回避アクション。ブラック＋クリームのカニンヘンダックスを操作し、HP3を引き継ぎながら30秒×5Waveを生存します。

ゲームロジックは `src/` のPythonだけです。PC版はPyxel、Web版は同じPythonをPyodide + Pyxel WASMで実行します。Vercelは静的ファイルのみ配信し、サーバーでPythonやPyxelを実行しません。JSは起動・入力・PNG変換・localStorageだけを担当します。

## 1. 作成ファイル

```text
poop-dog/
├── main.py                     # PC/Web共通のPyxelアダプター
├── index.html / style.css       # 起動画面、説明、タッチUI
├── app.js                      # Web起動とブラウザI/O
├── manifest.json               # ブラウザへプリロードするPython/素材一覧
├── src/
│   ├── __init__.py
│   ├── game.py                 # ゲーム状態、進行と調整
│   ├── player.py               # 物理とアニメーション状態
│   ├── hazard.py / poop.py     # Hazard契約、Poopと生成factory
│   ├── collision.py            # 矩形と交差判定
│   ├── platform.py / stage.py  # 地形と配置データ読み込み
│   ├── camera.py
│   ├── wave_manager.py
│   ├── score_manager.py
│   ├── bridge.py               # 任意のWebホストへの接続
│   ├── renderer.py             # Pyxel描画とスプライト反映
│   └── config.py               # バランスと16色パレット
├── assets/
│   ├── default_player.png      # 64×16 RGBA
│   ├── default_player.json     # 同じ画像の明示的なパレット番号
│   ├── palette.json            # build時にconfig.pyから生成
│   └── stage.json              # ステージ配置
├── tools/
│   ├── build.mjs               # 静的dist出力、manifest生成
│   ├── serve.mjs               # ローカル静的HTTP配信
│   └── make_sprite.py          # 手描きピクセルデータから素材を再生成
├── tests/
│   ├── test_game.py            # ゲーム回帰テスト
│   └── web.test.mjs            # ブラウザI/O契約テスト
├── .github/workflows/ci.yml
├── package.json / requirements.txt
├── vercel.json / .gitignore
├── QA.md
└── README.md
```

`game.pyxres` は不要なため使用していません。スプライトをPNGとパレット番号のJSONで管理し、背景はPyxelの描画関数で描いています。`dist/` は生成物なのでGitへ登録しません。

## 2. 実装済み機能

- TITLE / PLAYING / WAVE_CLEAR / GAME_OVER / GAME_CLEAR、STARTとRETRY。
- 1152pxステージ、追従カメラ、端の制限、左右移動、4フレームアニメーションと反転。
- 重力・ジャンプ・落下・着地・足場・スロープ。空中で再ジャンプ不可。
- 芝生・フェンス・木・ベンチ・タイヤ・木箱・ドッグウォーク・台・スロープ・ハードル。
- ステージ全域からPoop生成。通常の茶色は遮蔽物で消滅。Wave 2から炎の付いた赤い貫通Poopが混ざり、ベンチ・足場・スロープを通り抜けます。接触ダメージは共通でHP-1、地面または画面外で削除。
- HP3、被弾でHP-1、30tickの無敵と点滅、HPのWave間持ち越し。
- 30秒×5Wave、3秒の停止インターバル、データによる難易度上昇。
- 生存10点/秒、Waveクリア500点、Waveごとのノーダメージ500点。最大19,500点。
- BESTの即時更新、localStorage永続化、保存拒否時のメモリ内フォールバック。
- iPhone用Pointer Eventsマルチタッチ、pointer capture、cancel/blur時の押しっぱなし解除。
- 64×16 PNG読み込み、署名とサイズ検証、15色への最近傍変換、透明色予約、不正入力時維持。

## 3. 未実装・未完了

要求されたMVPのコードは実装済みで、GitHub登録・Vercel本番公開も完了しました。iPhone実機SafariとPCネイティブ版の実操作確認は未実施です。ブラウザ確認と自動テストの範囲はQA.mdを参照してください。

## 4. PCネイティブ版のローカル起動

Python 3.10以上を用意し、このフォルダーで実行します。

```sh
python -m venv .venv
# Windows PowerShell
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

macOS/Linuxは `.venv/bin/python` を使います。スプライトを再生成するときだけ `python -m pip install pillow` と `python tools/make_sprite.py` が必要です。通常起動にPillowは不要です。ネイティブ版BESTは同一プロセス内で保持され、終了後の永続化はWeb版のみです。

## 5. Web版のローカル起動

Node.js 22以上。追加npm依存パッケージはありません。

```sh
npm run build
npm run serve
```

`http://localhost:8765` を開き「ゲームを起動」→「START」。ビルド後の静的ファイルを配るだけです。PythonのHTTPサーバーを使う場合は `python -m http.server 8765 --directory dist` でも構いません。`index.html` をfile://で直接開かないでください。

初回起動ではjsDelivrからPyodide 0.29.0とPyxel 2.5.10のWASMを読み込みます。インターネット接続が必要です。ソース変更後は `npm run build` とページ再読み込みを行ってください。

## 6. PCでの確認方法

1. 起動後にTITLE、犬、HP3とBESTを確認し、START / Enter / Spaceで開始。
2. A/←、D/→、W/↑/Spaceを使用。ジャンプは押下の立ち上がりだけを受け付けます。
3. ベンチの下へ移動するとPoopが天板で消え、ジャンプすると天板に乗れます。
4. 右へ進んでカメラ、スロープ、端の制限を確認。
5. 被弾・点滅・GAME OVER・RETRY後のリセットを確認。
6. 30秒生存しWAVE CLEARの3秒停止、HP持ち越しと加点を確認。
7. ページを閉じて再訪しBESTが残ることを確認。

```sh
python -m unittest discover -s tests -v
npm run test:web
npm run build
```

ロジックテストはPyxelをimportしないため、GUIのないCIでも実行できます。WebテストはDOM・画像デコードを模した契約テストです。実機ブラウザテストの代わりではありません。

## 7. iPhoneでの確認方法

VercelのHTTPS URLをSafariで開くのが基本です。ローカルでは同じWi-Fiに接続し `http://<PCのLAN IP>:8765` を開きます（PCのファイアウォールで接続許可が必要な場合があります）。

横画面にして起動→START。左下LEFT/RIGHTと右下JUMPを操作し、RIGHT+JUMPとLEFT+JUMPをそれぞれ2本指で確認してください。片方を離してももう片方の入力が残ること、Safariを背面にした際に進行が止まること、復帰時に押しっぱなしにならないことを確認します。ランドスケープ時はゲームを優先し、画像選択UIは縦画面で表示します。

## 8. GitHub登録方法

このフォルダー単体をリポジトリルートにします。既存の親アプリとは分離してください。

```sh
git init -b main
git add .
git commit -m "Implement POOP DOG with Python and Pyxel Web"
git remote add origin https://github.com/YOUR_ACCOUNT/poop-dog.git
git push -u origin main
```

GitHubで空のリポジトリを作成し、URLの `YOUR_ACCOUNT` を置き換えます。`.vendor`、`.venv`、生成物や資格情報は除外済みです。GitHub Actionsがpush/PR時にテストと静的ビルドを実行します。

## 9. Vercelデプロイ方法

1. VercelでAdd New → ProjectからGitHubの `poop-dog` をImport。
2. Framework Preset: **Other**、Root Directory: **.**。
3. Build Command: **npm run build**、Output Directory: **dist**。
4. 環境変数は不要。Deployを実行し、発行されたHTTPS URLをPCとiPhoneで確認。

親リポジトリの一部として登録する場合のみRoot Directoryを `poop-dog` にします。CLIを利用するなら認証後にこのフォルダーで `npx vercel`、本番公開は `npx vercel --prod`。デプロイ設定はvercel.jsonに含まれています。Python API/Functionsは一切ありません。

## 10. PNGスプライト仕様

64×16pxのPNG、最大1MB。左から16×16pxずつ **待機 / 歩行1 / 歩行2 / ジャンプ**。右向きで描き、足は各フレームの下端付近に揃えてください。アップロード画像はサーバーへ送らず、File APIとCanvasで端末内処理します。ファイル名やローカルパスをPythonでopenしません。

透明度128未満は透明色15へ変換、それ以上は不透明な15色からRGB距離最小の色へ変換します。半透明グラデーションは保持せず、二値透明になります。真っ黒はパレットの濃い黒に近似されます。不正なPNG・異なる寸法・破損画像はエラー表示し、現在のスプライトを維持します。アップロード画像はページを閉じるとリセットされ、RETRYでは保持します。

## 11. config.pyで変更できる項目

解像度、FPS、ステージ幅・地面高、開始位置、犬サイズ・速度、重力・ジャンプ速度・落下上限、当たり判定、アニメーション速度、HP、無敵と点滅周期、Wave/インターバル時間、各種スコア、Poop寸法・開始Y・エフェクト寿命、16色パレット、各Waveの生成間隔・最小/最大速度・最大同時数・貫通Poopの生成確率（piercing_chance）。

現在は30FPSの固定tick方式です。速度はpx/tick、生成間隔はtick単位。FPS変更時は速度と生成間隔も調整してください。`npm run build` がWeb用パレットを同期します。ステージ配置は `assets/stage.json` で編集します。犬の見た目と16×16フレーム仕様や5Wave固定のWeb文言を変える場合は、それらも合わせて編集してください。

## 12. Bird / Ball / OtherDogの追加方法

`Hazard` を継承するクラスを `src/bird.py` などへ追加し、`alive`、`hitbox`、`update(platforms)`、`draw(renderer)` を実装します。固有の描画はRendererに追加してください。生成factoryで種類を選び、`Game(storage, hazard_factory=...)` に渡します。Gameの接触・HP処理は共通契約を使うため変更不要です。必要になった時点でWaveデータに種類や出現比率を加えます。

## 13. 既知の制約

- iPhone実機Safari、PCネイティブ操作は未検証です。Vercel本番の静的配信は確認済みです。
- 初回起動のCDNダウンロード量と速度、端末メモリにより待ち時間が生じます。オフライン起動には対応していません。
- 一方向足場です。犬は下から通過して上に着地できます。木・フェンスは背景です。通常Poopは描画上の背もたれではなく足場天面で消えます。赤い貫通Poopは足場を無視します。
- Wave 1はベンチ下で防げます。Wave 2以降は赤い貫通Poopを左右移動で避ける必要があります。
- 低速端末ではゲーム内30秒が実時間より長くなる場合があります。背面/フォーカス喪失時は意図的に停止します。
- WebのBESTは同じブラウザ・同じオリジン単位。別端末との同期や不正スコア対策はありません。
- テストは最終実装に対する機能単位の回帰検証です。27個の独立したコミットを逐次作成したものではありません。

参照: [Pyxel 2.5.10公式Web起動コード](https://github.com/kitao/pyxel/blob/v2.5.10/wasm/pyxel.js)、[Vercel静的ビルド設定](https://vercel.com/docs/builds/configure-a-build)。

## 2026-09-09: 貫通Poop

Wave 1: 0%、Wave 2: 15%、Wave 3: 20%、Wave 4: 25%、Wave 5: 30%の確率で、通常のPoopの代わりに出現。赤＋金色の炎で識別できます。総生成数・速度・接触ダメージ・無敵時間・基本スコアは既存ルールを共用します。

## 2026-09-09: 貫通Poopの落下位置

強力なうんちの約70%はベンチ・台・タイヤ・木箱・ドッグウォーク・スロープ・ハードルの上から、約30%はそれらに重ならない場所から落下します。木やフェンスは背景なので対象外です。通常Poopは従来どおり全域で一様ランダム。config.pyのPIERCING_OBJECT_BIASで調整できます。比率は1個ごとの抽選確率であり、短時間の個数比を保証するものではありません。

## フローラル：回復アイテム

肛門絞り後のフローラルな香りに由来する、うす紫にきらめく風のアイテム。全Waveで12〜18秒おきに画面内のランダムな位置の上空から落下します。同時に最大1個。風なので足場を通り抜け、地面で消えます。触れるとHPを1回復（最大3）。満タンでも取得して消えます。Wave間の自動回復はなく、被弾済みのWaveは回復してもノーダメージボーナスの対象になりません。致命的な被弾と同時の場合はGAME OVERを優先します。config.pyのFLORAL_*で頻度・落下速度・揺れ・回復量などを調整できます。


## カリカリ：スコアアイテム

クリーム色の縁がある薄茶色の餌。画面内のランダムなX座標の地面・足場上に0.5〜1秒おきに出現します。12秒で消え、同時に最大16個。取得で30点。直前の取得から5秒以内（ちょうど5秒も含む）の間隔で5個連続取得すると、通常の150点に加えて100点、頭上に2秒間「Delicious!」を表示します。5個達成後は再び0個から数えます。5秒超の空白、Wave終了、RETRYでコンボをリセット。ポーズ中は時間停止。回復・被弾ではコンボは切れません。基本スコア最大19,500点に餌とコンボの点数が上乗せされ、BESTにも保存されます。config.pyのKIBBLE_*で頻度・寿命・サイズ・点数・コンボ条件を変更できます。


## 3レベルとトモダチ・流星群

全3レベル、各5Wave（各30秒）。Wave間・レベル間は3秒停止し、HPとスコアを持ち越します。Level 3 / Wave 5でGAME CLEAR。基本ノーダメージ合計19,500点＋カリカリ点です。

- Level 1：通常うんち、Wave 2から強力な貫通うんち。
- Level 2：さらに白いトイプードル1体。地面を歩いてプレイヤーへ近づきます。
- Level 3：さらにクリーム色＋濃い輪郭・水色の首輪のコーギー1体。地面を横断し、ジャンプで飛び越えると約34px走り過ぎて減速ドリフトし、プレイヤー側へUターン。端でもドリフトして折り返します。トモダチは地面を走り、ジャンプや足場で回避可能。接触1ダメージ、接触しても消えず、既存の1秒無敵を共有します。各Wave開始時に安全な距離へ再配置します。
- Level 3のWave 4・5：5秒おきに画面内へ幅21pxの巨大うんち。遮蔽物で消え、接触は1ダメージ。
- 各レベルでまれに流星群：18〜26秒ごとの抽選で55%、1.5秒の予告後に3秒間、高速の通常うんちが集中。尾を引く見た目で識別でき、遮蔽物で防げます。生成数はWaveの上限内。

設定はconfig.pyのLEVELS、POODLE_*、CORGI_*、GIANT_*、METEOR_*。追加モジュールはfriend.pyとrain_events.py。すべてのイベント時間はゲーム内時間で、ポーズとWave間は停止します。


## デバッグモード

https://poop-dog.vercel.app/?debug=1 を開きゲームを起動すると、LEVEL 1〜3・WAVE 1〜5の選択欄を利用できます。「選択地点から開始」でHP3・スコア0・敵・アイテム・タイマー・カメラ・コンボをリセットし、その地点の敵とイベント設定で開始します。RETRYも最後に選んだ地点から再開します。ゲーム画面にDEBUG / NO BESTを表示し、デバッグ中はBESTを更新・保存しません。通常モードへ戻るリンクで通常URLへ移動します。URLにdebug=1がない場合は操作UIを隠し、Python側もデバッグ指示を受け付けません。通常の難易度・操作・進行は変更しません。


## スマホ操作と拡大表示

タッチ端末は横持ちで左右に操作専用エリア、縦持ちで画面下に操作エリアを表示します。ゲーム画面にはボタンを重ねません。「拡大／戻る」でプレイ状態を維持して表示を切り替えます。対応ブラウザはFullscreen APIを使い、非対応・許可されない場合はページ内拡大に切り替えます。iPhoneでSafariのバーを省く場合は共有メニューからホーム画面へ追加してWebアプリとして開いてください。ホーム画面起動用のAppleメタタグを設定済みです。オフライン対応は追加していません。

検証：Webテスト9件成功。デスクトップブラウザでタッチ用CSSを適用した検証ページを使い、844×390・390×844で画面とキーの非重複と横はみ出しなしを確認。実機iPhone Safariでの操作・セーフエリア確認は未実施です。


## iPhone Chrome操作の修正

横画面のタイトル画像がFlexで縮まないよう固定し、小さい高さ向けにタイトルを縮小。横画面の拡大モードは左右の操作列と下部ステータス帯を省き、16:9の画面を表示可能な高さまで拡大、半透明キーを下端へ配置します。通常モードは画面外の操作キーを維持。ブラウザのアドレスバーを強制的に隠すものではありません。

タッチ入力は指ごとのTouch Eventsで管理し、Pointer Eventsとの二重入力を避けます。ボタン外への移動・指を離す・キャンセル・フォーカス喪失・回転で解除。ゲーム領域の文字選択、長押しメニュー、ドラッグ開始を抑制します。Webテスト12件成功、横844×330相当の検証ページでタイトルの非欠損と拡大のサイズ差を確認。実機Chromeの操作確認はユーザーによる確認待ちです。


## 起動タップと回転順序の修正

タッチのpreventDefaultを画面コンテナ全体からキャンバスだけへ限定し、HTMLの「ゲームを起動」のクリックを妨げないよう修正。画面外のSTART/RETRYは削除し、起動後のTITLE・GAME OVER・GAME CLEARに限り画面内に表示します。タッチでキャンバスをタップしても開始・再挑戦できます。

スマホ横画面は通常・拡大とも同一の最大表示レイアウトとし、回転の操作順で表示が変わらないよう統一。キャンバスを絶対配置して親サイズへの影響を除き、Visual Viewportの高さ変更に追従します。Webテスト13件成功。タッチCSS検証ページにて「縦で拡大→横」「その後戻る」「縦から直接横」の3手順すべて同一座標・同一サイズ、実ゲーム起動からPLAYINGまで確認。iPhone実機での再確認は未実施です。

### 伝説の木の棒
各Waveの6〜18秒に1回だけ、画面内のランダムな位置から輝く短い木の棒が落下します。取得すると10秒間、口に棒をくわえ、すべての敵からのダメージを防ぎます。遮蔽物を通過し、取り逃した棒は地面で消えます。残り時間は画面上部に表示します。Wave間と一時停止中は効果時間も停止し、RETRYで解除します。出現時刻・落下速度・効果時間はconfig.pyのSTICK_*で調整できます。

### 犬種選択
タイトル・GAME OVER・GAME CLEAR画面でDキーまたはDOGボタンを押すと犬種選択へ移動します。左右矢印/A・D/画面内の左右ボタンで切り替え、Enter・Space・JUMP・OKで決定すると元の画面へ戻ります。選択中はゲーム進行を停止し、リザルトのスコアを保持します。選択した犬種はRETRYでも引き継ぎます（ページ再読み込み時はダックスに戻ります）。

KANINCHEN DACHSHUND / POMERANIAN / CHIHUAHUA / TOY POODLE / SCHNAUZER の5犬種。全犬種で物理・当たり判定は共通です。追加のドット絵と4フレームのデータはsrc/dog_sprites.pyにあります。アップロード画像も従来どおり利用できます。編集した画像は犬種ごとに保持され、選び直しても維持されます（ページ再読み込みまで）。

### ドット絵エディター
ゲーム画面の下の「ドット絵エディター」を開いて編集します。編集用画面が開いている間はゲームが一時停止します。「現在の犬を読み込む」で選択中の犬やアップロード画像を取り込めます。色を選んでクリック・ドラッグで描画し、右クリックで消去します。ペン・消しゴム・塗りつぶし・スポイト、Undo/Redo、前フレームのコピー・左右反転に対応しています。

待機／歩行1／歩行2／ジャンプの各16×16フレームを編集し、「ゲームに反映」で現在のブラウザのプレイヤーへ適用できます。「PNGをダウンロード」で64×16の透過スプライトシートを書き出します。ゲーム内の当たり判定は変更されません。下書きはlocalStorageへ保存（利用不可ならメモリ内のみ）。他のユーザーやGitHub上の原画は変更しません。画像は犬種ごとにページ再読み込みまで保持します。既定画像に戻す場合はページを再読み込みしてください。

「ゲームに反映」はエディターを閉じてゲームへ戻ります。完了表示はPython側で反映を確認してから表示します。犬種選択中のプレビューへ適用した画像も、決定後とRETRY後に保持されます。
