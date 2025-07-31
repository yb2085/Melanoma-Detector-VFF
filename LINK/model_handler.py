# LINK/model_handler.py
import os
import sys
import torch
import timm
from PIL import Image
from torchvision import transforms

# Configuration des chemins
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../MODELE')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pth')
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MelanomaDetector:
    """
    Classe permettant de charger un modèle de détection de mélanome et d'effectuer des prédictions sur des images.

    Attributes:
        model (torch.nn.Module): Modèle de deep learning chargé et prêt à l'emploi.
        transform (torchvision.transforms.Compose): Transformations à appliquer aux images avant prédiction.
    """

    def __init__(self):
        """
        Initialise le détecteur de mélanome en chargeant le modèle et les transformations.
        """
        self.model = self._load_model()
        self.transform = self._get_transforms()
        
    def _load_model(self):
        """
        Charge le modèle pré-entraîné à partir des fichiers de configuration et des poids sauvegardés.

        Returns:
            torch.nn.Module: Le modèle chargé, prêt pour l'inférence.
        """
        # Récupération des paramètres depuis model_info.txt
        with open(os.path.join(MODEL_DIR, 'model_info.txt'), 'r') as f:
            params = {line.split(':')[0].strip(): line.split(':')[1].strip() 
                     for line in f if ':' in line}
        
        # Construction dynamique du modèle
        model = timm.create_model(
            params['Model'],
            pretrained=False,
            num_classes=int(params['Classes'])
        )
        
        # Chargement des poids entraînés
        state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state_dict)
        model = model.to(DEVICE)
        model.eval()
        
        return model

    def _get_transforms(self):
        """
        Définit les transformations à appliquer aux images pour qu'elles soient compatibles avec le modèle.

        Returns:
            torchvision.transforms.Compose: Pipeline de transformations d'images.
        """
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_path):
        """
        Effectue une prédiction sur une image donnée et retourne la classe prédite ainsi que la confiance associée.

        Args:
            image_path (str): Chemin vers l'image à analyser.

        Returns:
            tuple: (pred_class, confidence_percent)
                - pred_class (int): Classe prédite (0 = mélanome, 1 = bénin).
                - confidence_percent (float): Pourcentage de confiance de la prédiction.
        """
        from PIL import Image
        import torch

        # Chargement et transform
        img = Image.open(image_path).convert('RGB')
        tensor = self.transform(img).unsqueeze(0).to(DEVICE)

        # Inférence
        with torch.no_grad():
            output = self.model(tensor)
            probs = torch.softmax(output, dim=1)
            pred  = torch.argmax(probs, dim=1).item()
            conf  = probs[0, pred].item() * 100

        return pred, conf


# Exemple d'utilisation
if __name__ == "__main__":
    detector = MelanomaDetector()
    result = detector.predict("test_image.jpg")
    print(result)
