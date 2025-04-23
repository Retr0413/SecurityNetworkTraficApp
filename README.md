# 🛡️ Network Traffic Classification & Analysis System

本システムは、Docker 上で MySQL と Flask (Webアプリ) を起動し、`scapy` によるネットワークトラフィックのキャプチャ、`PyTorch` を用いたリアルタイム通信分類を行うセキュリティ分析システムです。

---

## 📌 1. 機能概要

### ✅ リアルタイムネットワークキャプチャ
- `packet_capture.py` により、`scapy` を使用してパケットを取得。
- 5秒ごとに MySQL へ保存。

### ✅ 通信分類（PyTorchモデル）
- `network_traffic_model.pth` をロードして分類。
- `Tor` や `VPN` を異常とみなし、`is_abnormal=True` フラグでマーク。

### ✅ Webフロントエンド
- `http://localhost:5000/` にアクセスで最近のパケットログを表示。
- ソースIP、宛先IP、プロトコル、サイズ、ラベルを確認可能。

### ✅ オフライン解析
- `offline_pcap_analysis.py` により `.pcap` ファイルを解析。
- 統計・侵入検知を実施。DB保存＋分類も可能。

---

## 📁 2. ディレクトリ構成

```plaintext
SECURITYNETWORKTRAFFICAPP/
├── app/
│   ├── main.py
│   ├── model/
│   │   ├── model.py
│   │   └── network_traffic_model.pth
│   ├── routes/
│   │   ├── api.py
│   │   └── frontend.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── logs.html
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── db.py
│       ├── preprocessing.py
│       └── ...
├── scripts/
│   ├── capture_traffic.sh
│   ├── process_logs.py
│   └── zeek_processing.sh
├── db_operations.py
├── docker-compose.yml
├── Dockerfile
├── packet_capture.py
├── offline_pcap_analysis.py
├── requirements.txt
└── README.md
🚀 3. 起動方法
✅ コンテナのビルド & 起動
bash
コピーする
編集する
docker-compose up --build
Flask (Web) はポート 5000 にて起動

capture サービスが有効なら、自動的にパケットキャプチャも開始

✅ Web UI 確認
text
コピーする
編集する
http://localhost:5000/
ブラウザでアクセスし、通信ログを確認

✅ ログ確認
bash
コピーする
編集する
docker-compose logs -f web
docker-compose logs -f capture
✅ 停止
bash
コピーする
編集する
docker-compose down
🧪 4. オフライン .pcap 解析
bash
コピーする
編集する
python offline_pcap_analysis.py /path/to/file.pcap 100
.pcap ファイルを読み込んで統計表示・ポートスキャン検出を実施

DBに保存（オプション設定による）

モデルによる分類も可能（label, is_abnormal を更新）

🧠 5. 学習済みモデルの仕様
モデルファイル: app/model/network_traffic_model.pth

分類ラベル: Non-Tor, NonVPN, VPN, Tor

異常とみなす: VPN, Tor → is_abnormal=True

ロジック実装: packet_capture.py, offline_pcap_analysis.py

⚙️ 6. カスタマイズ
🛜 ネットワークインターフェース設定
packet_capture.py:

python
コピーする
編集する
iface = "eth0"  # 必要に応じて en0, wlan0 などに変更
docker-compose.yml:

yaml
コピーする
編集する
network_mode: "host"
cap_add:
  - NET_ADMIN
🧩 モデル構造・特徴量カスタマイズ
編集対象:

model.py: モデル構造の定義

preprocessing.py: 入力特徴量の加工処理

🗃️ DB構成変更
TrafficLog テーブルに新たなカラムを追加可能

保存・更新ロジック: db_operations.py

🖼️ フロントエンド拡張
templates/index.html を編集して以下を実装可能:

ページネーション

ラベル別フィルタリング

グラフ表示（Chart.js 等）

