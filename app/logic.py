import numpy as np
# import xgboost as xgb # Décommenter quand tu as un modèle entraîné

class SeverityCalculator:
    def __init__(self):
        # Poids arbitraires pour commencer (à calibrer)
        self.w_len = 0.3
        self.w_width = 0.4
        self.w_conf = 0.3
    
    def calculate_deterministic(self, length, width, ai_confidence, defect_type):
        base_score = (length * self.w_len) + (width * self.w_width * 10) 
        
        # Bonus de gravité si c'est un nid de poule
        if defect_type == "nid_de_poule":
            base_score *= 1.5
            
        # Pondérer par la confiance de l'IA (si l'IA est sûre, on garde le score)
        final_score = base_score * ai_confidence
        
        # Normalisation simple (clamp entre 0 et 100)
        return min(max(final_score, 0), 100)

    def predict_ml(self, features):
        """
        Simulation d'un appel à un modèle XGBoost ou Scikit-Learn.
        Pour l'instant, on renvoie le calcul déterministe, 
        mais c'est ici que tu chargerais 'model.json'.
        """
        # model = xgb.Booster()
        # model.load_model("severity_model.json")
        # return model.predict(features)
        return self.calculate_deterministic(*features)

calculator = SeverityCalculator()