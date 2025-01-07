# app/model/model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

class DeepCNN(nn.Module):
    """
    このモデルは学習時に:
      conv.0 -> Conv1d(1,128,3)
      conv.1 -> BatchNorm1d(128)
      conv.3 -> Conv1d(128,128,3)
      conv.4 -> BatchNorm1d(128)
      conv.6 -> Conv1d(128,128,3)
      conv.7 -> BatchNorm1d(128)

      fc.0 -> Linear(10112 -> 512)
      fc.3 -> Linear(512 -> 64)
      fc.6 -> Linear(64 -> 4)
    というキー構造で保存される

    ここでは ReLU 層など重みを持たない層の順番を飛ばすために、
    conv.2, conv.5, conv.8 などは存在しない => ReLU は nn.Sequential に含まれないか
    もしくは sub-layer 名を例えば '2' に設定しても state_dict には出ない(パラメータなし) ので問題ありません。
    """

    def __init__(self):
        super(DeepCNN, self).__init__()

        # conv -- nn.Sequential で sub-layer にキー "0","1","3","4","6","7" を設定
        # ただし ReLU はパラメータを持たないためキーには含まれません
        self.conv = nn.Sequential(OrderedDict([
            ("0", nn.Conv1d(in_channels=1, out_channels=128, kernel_size=3)),   # conv.0
            ("1", nn.BatchNorm1d(128)),                                        # conv.1
            # ReLUはパラメータを持たないのでキーに影響しない。名前を飛ばして"2"にReLUを入れてもOK
            ("2", nn.ReLU()),

            ("3", nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3)), # conv.3
            ("4", nn.BatchNorm1d(128)),                                         # conv.4
            ("5", nn.ReLU()),

            ("6", nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3)), # conv.6
            ("7", nn.BatchNorm1d(128)),                                         # conv.7
            ("8", nn.ReLU()),
        ]))

        # fc -- 同様に sub-layer に"0","3","6"を設定し、ReLUはキーに影響しない
        self.fc = nn.Sequential(OrderedDict([
            ("0", nn.Linear(10112, 512)),   # fc.0
            ("1", nn.ReLU()),
            ("3", nn.Linear(512, 64)),     # fc.3
            ("4", nn.ReLU()),
            ("6", nn.Linear(64, 4)),       # fc.6
        ]))

    def forward(self, x):
        """
        x: shape (batch_size, 1, input_length)
        """
        x = self.conv(x)   # (batch_size,128, input_length - 3*3 ?)
        # Flatten
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

class NetworkTrafficModel:
    def __init__(self, model_path):
        self.class_names = ["Non-Tor","NonVPN","VPN","Tor"]
        self.model = self._load_model(model_path)
        self.model.eval()

    def _load_model(self, model_path):
        model = DeepCNN()
        # Pickle警告対応 => weights_only=True など試す (PyTorch>=2.1)
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict)
        return model

    def predict(self, features):
        """
        features: np.array (shape=(input_length,)), 1D
        """
        import numpy as np
        import torch
        with torch.no_grad():
            x_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0)
            outputs = self.model(x_tensor)
            pred_idx = outputs.argmax(dim=1).item()
            return self.class_names[pred_idx]
