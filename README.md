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
Flask (Web) はポート 5000 にて起動。

capture サービスがあればパケットキャプチャも自動実行。

✅ Web UI 確認
text
コピーする
編集する
http://localhost:5000/
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
指定 .pcap ファイルを解析。

統計表示 + ポートスキャン検知。

DB保存 + モデル分類も可能。

🧠 5. 学習済みモデルの仕様
モデルファイル: app/model/network_traffic_model.pth

ラベル: Non-Tor, NonVPN, VPN, Tor

異常とみなす: VPN, Tor → is_abnormal=True

ロジック実装箇所: packet_capture.py, offline_pcap_analysis.py

⚙️ 6. カスタマイズ
🛜 ネットワークインターフェース
packet_capture.py の iface = "eth0" を適切な名前に変更。

Docker使用時: network_mode: "host" や cap_add: [NET_ADMIN] を追加。

🧩 モデル構造・特徴量
編集対象: model.py, preprocessing.py

🗃️ DB構成
テーブル拡張: TrafficLog にカラム追加。

編集対象: db_operations.py

🖼️ フロントエンド
ページ編集: templates/index.html

グラフ導入: Chart.js など可
