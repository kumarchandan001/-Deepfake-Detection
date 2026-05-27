import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from typing import Dict

class MetricsCalculator:
    @staticmethod
    def compute_all(y_true: np.ndarray, y_pred_prob: np.ndarray) -> Dict[str, float]:
        y_pred_class = (y_pred_prob >= 0.5).astype(int)
        
        acc = accuracy_score(y_true, y_pred_class)
        prec = precision_score(y_true, y_pred_class, zero_division=0)
        rec = recall_score(y_true, y_pred_class, zero_division=0)
        f1 = f1_score(y_true, y_pred_class, zero_division=0)
        
        try:
            auc = roc_auc_score(y_true, y_pred_prob)
        except ValueError:
            auc = 0.5
            
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred_class, labels=[0, 1]).ravel()
        
        return {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "auc": float(auc),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
