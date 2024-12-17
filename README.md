ネットワークトラフィック分類システム 要件定義書
1. 概要
本システムは、リアルタイムまたは近リアルタイムで取得したネットワークトラフィック（パケット情報）を機械学習モデル（PyTorchで学習済み）によって分類し、通信が「Non-Tor」「NonVPN」「VPN」「Tor」のいずれに該当するかを判別するシステムである。
Docker環境上でFlaskアプリケーション（Web UI & API）とMySQLデータベースを起動し、別プロセスまたは別コンテナでScapyによるパケットキャプチャを行い、その結果をDBに保存、モデル判定結果をラベル付けし、フロントエンド画面で可視化することを想定している。

2. 使用用途
セキュリティ教育: 学習者がリアルなネットワークトラフィックを観察し、VPNやTorなど特殊な通信を識別するモデルを理解できる。
ネットワーク管理・監視: 管理者が、自組織内ネットワークで発生するTor通信やVPN接続を検知し、適切な対策を取る参考にする。
研究・開発のベース: ネットワーク異常検知や侵入検知システム（IDS）への応用、トラフィック解析技術の検証プラットフォームとして利用可能。
3. 対象範囲
入力対象: ネットワークインターフェース（例: eth0）上を流れるIPパケット
出力: MySQLデータベース上へのパケットメタ情報の保存、および通信種別（Non-Tor, NonVPN, VPN, Tor）のラベル付与
UI: FlaskアプリケーションによるWeb UIで最近のパケット情報と分類結果を閲覧可能
4. システム構成
Docker構成:

dbサービス: MySQLデータベース
webサービス: FlaskベースのWebアプリケーション(API + フロントエンド)
ホストまたは別サービスでpacket_capture.pyを実行
Flaskアプリ:

/ エンドポイント: 最近50件のパケットログと分類結果表示
/api/predict (任意): モデル推論API（今回はログから自動処理のため直接呼ばない場合もある）
DBスキーマ (traffic_logテーブル):

id (INT, PK)
timestamp (VARCHAR)
src_ip (VARCHAR)
dst_ip (VARCHAR)
protocol (INT)
packet_length (INT)
ttl (INT)
flags (VARCHAR)
src_port (INT)
dst_port (INT)
label (VARCHAR) → モデル判定後に付与
processed (BOOLEAN) → 未処理/処理済みフラグ
モデル:

PyTorchで事前学習済み
network_traffic_model.pthに格納
入力: 数値特徴量（protocol, packet_length, ttlなど）
出力: 4クラス分類（Non-Tor, NonVPN, VPN, Tor）
パケットキャプチャ (packet_capture.py):

scapyを用いて指定インターフェース上のパケットを取得
取得したパケットメタ情報をDBに5秒おきに保存
別スレッドで未処理パケットをDBから取得、model.pyのモデルで判定後、DBを更新
5. 要件
機能要件
パケット収集機能:
Scapyでネットワークインターフェース上のIPパケットをリアルタイム収集。

データ保存機能:
取得したパケット情報（時刻、IP、ポート、protocol等）を定期的にMySQLデータベースに保存。

モデル判定機能:
保存されたパケットデータに対して学習済みモデルを用いて通信種別を判定し、DBにラベル更新。

表示機能:
Flaskフロントエンドで最近のパケット一覧と判定結果を表示。

API機能:
必要に応じてAPIを拡張し、外部から判定結果やログ参照が可能。

非機能要件
パフォーマンス:
小規模トラフィックであればリアルタイム（数秒単位）の処理が可能。大量トラフィックの場合はスケールアウトや別途調整が必要。

拡張性:
特徴量・モデルを変更することで、異なる通信種別や攻撃検知モデルへ容易に拡張可能。

可用性:
Docker上で構築し、コンテナ再起動により簡易的な冗長性確保。

運用要件
事前条件:

DockerおよびDocker Composeが動作するLinux環境
学習済みモデルnetwork_traffic_model.pthファイルの用意
起動手順:

bash
コードをコピーする
docker-compose up --build
python3 packet_capture.py
ブラウザで http://localhost:5000/ にアクセス。

停止手順:
Ctrl+Cでpacket_capture.py停止、docker-compose downでコンテナ停止。

データ初期化:
DBのデータを初期化するにはdocker-compose down -vでボリューム削除。

6. 想定シナリオ
ネットワーク管理者が学内ネットワークでTor通信が行われていないか監視する。
システム起動後、Web UIでパケットログを確認、Torラベルが付与された場合、対策を検討。

教育目的でセキュリティ研修受講者に対してVPN/Torを含むサンプルトラフィックを流し、受講者はWeb UIで結果を確認する。
受講者はモデル判定ロジックや特徴量を学習。
