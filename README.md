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
- 生存10点/秒、Waveクリア500点、Waveごとのノーダメージ500点。最大6,500点。
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
