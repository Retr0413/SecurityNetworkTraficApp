import torch
import torch.nn as nn

class DummyModel(nn.Module):
    def __init__(self, num_classes=4, input_size=128):
        super(DummyModel, self).__init__()
        self.fc = nn.Linear(input_size, num_classes)
    def forward(self, x):
        return self.fc(x)
    
class NetworkTrafficModel:
    def __init__(self, model_path):
        self.class_names = ["Non-Tor", "NonVPN", "Tor", "VPN"]
        self.model = self._load_model(model_path)
        self.model.eval()

    def _load_model(self, model_path):
        model = DummyModel(num_classes=4, input_size=128)
        return model

    def predict(self, feature):
        with torch.no_grad():
            input_tensor = torch.FloatTensor(feature).unsqueeze(0).unsqueeze
            output = self.model(input_tensor)
            pred_idx = output.argmax(dim=1).item()
            return self.class_names[pred_idx]