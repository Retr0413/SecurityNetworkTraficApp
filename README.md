Network Traffic Classification & Analysis System
本システムは、Docker 上で MySQL と Flask (Webアプリ) を起動し、scapy を用いてネットワークトラフィックをキャプチャし、その結果をデータベースに保存すると同時に、学習済みの PyTorch モデルを使用してリアルタイムに通信を判別（例: Non-Tor, NonVPN, VPN, Tor など）するためのシステムです。
さらに、オフラインの .pcap ファイルを解析するスクリプトを用意し、トラフィックを統計的に分析したり、ポートスキャン等の簡易的な侵入検知を試すことも可能です。

1. 機能概要
リアルタイムネットワークキャプチャ

packet_capture.py が scapy を用いてネットワークインターフェース上のパケットをキャプチャし、5秒おきに MySQL データベースへ保存します。
学習済みモデルによる通信分類

PyTorch で事前学習された network_traffic_model.pth をロードし、データベースに保存されたパケットに対して自動的にラベル付与。
Tor や VPN を異常とみなす場合は、is_abnormal=True などのフラグを付与して可視化が可能。
Webフロントエンド

Docker 起動後、ブラウザで http://localhost:5000/ にアクセスすると、最近のパケットログが表示される。
各パケットのソースIP、宛先IP、プロトコル、パケットサイズ、ラベル（モデル判定結果）などを閲覧可能。
オフライン .pcap 解析

offline_pcap_analysis.py により、既存の .pcap ファイルを読み込み、統計分析やポートスキャン検知を行い、オプションでデータベースへ保存→モデル判定を行うことができる。
2. ディレクトリ構成
lua
コードをコピーする
SECURITYNETWORKTRAFFICAPP/
├─ app/
│  ├─ main.py
│  ├─ model/
│  │  ├─ model.py
│  │  └─ network_traffic_model.pth
│  ├─ routes/
│  │  ├─ api.py
│  │  └─ frontend.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ index.html
│  │  └─ logs.html
│  └─ utils/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ db.py
│     ├─ preprocessing.py
│     └─ ...
├─ scripts/
│  ├─ capture_traffic.sh
│  ├─ process_logs.py
│  └─ zeek_processing.sh
├─ db_operations.py
├─ docker-compose.yml
├─ Dockerfile
├─ packet_capture.py
├─ offline_pcap_analysis.py
├─ requirements.txt
└─ README.md   <-- 本ファイル
app/ : Flaskアプリケーションのソース。DBやモデル読み込みなどを含む
packet_capture.py : scapyを用いたリアルタイムキャプチャ + DB保存 + モデル判定
offline_pcap_analysis.py : オフラインの.pcap解析・DB保存 + モデル判定（オプション）
db_operations.py : DB接続・レコードの保存、未処理レコードの取得、ラベル更新など
docker-compose.yml : Docker Compose構成（MySQL, Flask, そして場合によってはcaptureサービス）
Dockerfile : FlaskやPythonモジュールのビルド設定
network_traffic_model.pth : 学習済みPyTorchモデルファイル
3. 起動手順
ビルド & コンテナ起動

bash
コードをコピーする
docker-compose up --build
db (MySQL) と web (Flask) が起動し、Flaskはポート5000で待機
capture サービスがある場合は同時に起動し、パケットキャプチャを自動開始する（docker-compose.yml の capture セクションを参照）
Web UI の確認

ブラウザで http://localhost:5000/ にアクセスすると、最近のパケットログとラベル、異常フラグなどが表示される
ログ表示

別のターミナルで docker-compose logs -f web や docker-compose logs -f capture を実行するとログをモニタリング可能
停止

bash
コードをコピーする
docker-compose down
4. オフライン解析 (任意)
既に存在する .pcap ファイルを解析したい場合は、以下のように実行：
bash
コードをコピーする
python offline_pcap_analysis.py /path/to/file.pcap 100
指定した .pcap を読み込み、統計情報やポートスキャン検出などを行い、結果をコンソールに表示
DBに保存する設定が有効な場合、レコードを保存後にモデル判定を実行し、label / is_abnormal カラムを更新
5. 学習済みモデルについて
app/model/network_traffic_model.pth には、事前に学習済みのPyTorchモデルが格納されていると仮定
モデルは model.py 内で読み込まれ、「Non-Tor / NonVPN / VPN / Tor」 といったクラス分類を行う
本システムでは Tor や VPN を「異常」とみなすロジックを packet_capture.py や offline_pcap_analysis.py の中で実装（例: is_abnormal = True）
6. カスタマイズ方法
ネットワークインターフェース指定

packet_capture.py 内で iface = "eth0" を他のインターフェース名に変更する
Dockerでホストネットワークを使用する場合、docker-compose.yml の network_mode: "host" や cap_add: [NET_ADMIN] が必要
モデル構造・特徴量

model.py の TrainedModel クラスや preprocessing.py の preprocess_features を学習時に合わせて編集
DB スキーマ変更

TrafficLog テーブルにさらに多くのカラムを追加可能
db_operations.py 内の保存・更新ロジックを調整
フロントエンド拡張

index.html を編集し、ページネーションやグラフ表示を加える
Chart.js などを導入して通信状況の可視化を行う
7. トラブルシューティング
MySQL に接続できない

ログに sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) ... Connection refused が出たら、DB がまだ起動中の可能性がある
docker-compose.yml の depends_on: condition: service_healthy などで対処
scapy がインターフェースを見つけられない

Docker上でインターフェース名が eth0 でないか、ホストネットワークを使う必要がある
cap_add: [NET_ADMIN] を Docker Compose で設定
モデルがロードできない

network_traffic_model.pth が誤って削除されていないか、正しいパスか確認
学習時と同じ PyTorch バージョンを使用しているかチェック
Tor/VPNを正しく検知できない

特徴量やモデルの精度に依存する。学習時のデータセットと特徴エンジニアリングを再確認
8. ライセンス・謝辞
本システムのライセンスは、プロジェクトの要件に合わせて設定してください (MIT License など)。
scapy, Flask, MySQL, PyTorch, などオープンソースライブラリに感謝します。
9. 今後の拡張
IDSへの発展: ポートスキャン、DoS検知、その他攻撃パターンを拡充
可視化ダッシュボード: KibanaやGrafana連携など
マイグレーションツール: Alembic等でDBスキーマ管理
スケールアウト: 大規模トラフィックに対応するためのバッチ処理やキューシステム導入
