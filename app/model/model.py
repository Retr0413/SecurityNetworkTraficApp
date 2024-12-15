import torch
import torch.nn as nn
class TrainedModel(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_classes=4):
        super(TrainedModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = x.squeeze(1) 
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

class NetworkTrafficModel:
    def __init__(self, model_path):
        self.class_names = ["Non-Tor", "NonVPN", "VPN", "Tor"]
        self.model = self._load_model(model_path)
        self.model.eval()

    def _load_model(self, model_path):
        model = TrainedModel(input_size=3, hidden_size=64, num_classes=4)
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict)
        return model

    def predict(self, features):
        with torch.no_grad():
            input_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0) 
            outputs = self.model(input_tensor)
            pred_idx = outputs.argmax(dim=1).item()
            return self.class_names[pred_idx]
