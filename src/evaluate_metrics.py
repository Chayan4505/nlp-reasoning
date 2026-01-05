
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import sys
import os
from .config import RESULTS_CSV, TRAIN_CSV

def evaluate_metrics(ground_truth_path=TRAIN_CSV, predictions_path=RESULTS_CSV):
    """
    Calculates classification metrics (Accuracy, Precision, Recall, F1) 
    by comparing predictions against ground truth.
    """
    
    if not os.path.exists(ground_truth_path):
        print(f"Error: Ground truth file not found at {ground_truth_path}")
        return

    if not os.path.exists(predictions_path):
        print(f"Error: Predictions file not found at {predictions_path}")
        return

    print("Loading data...")
    truth_df = pd.read_csv(ground_truth_path)
    pred_df = pd.read_csv(predictions_path)
    
    # Merge on Story ID
    # Note: 'id' in train.csv vs 'Story ID' in results.csv
    # We normalized this in run_inference, but let's be safe.
    
    # Map 'consistent' -> 1, 'contradict' -> 0 in truth
    truth_df['label_int'] = truth_df['label'].map({'consistent': 1, 'contradict': 0})
    
    # Rename for merge if needed
    if 'id' in truth_df.columns:
        truth_df.rename(columns={'id': 'Story ID'}, inplace=True)
        
    merged = pd.merge(truth_df, pred_df, on='Story ID', how='inner')
    
    if len(merged) == 0:
        print("No overlapping stories found between Ground Truth and Predictions.")
        return

    y_true = merged['label_int']
    y_pred = merged['Prediction']
    
    print("\n" + "="*40)
    print(f"EVALUATION RESULTS (n={len(merged)})")
    print("="*40)
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    
    print(f"Accuracy:  {acc:.2%}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("-" * 20)
    print("Confusion Matrix:")
    print(f"TN: {cm[0][0]} | FP: {cm[0][1]}")
    print(f"FN: {cm[1][0]} | TP: {cm[1][1]}")
    print("="*40)

if __name__ == "__main__":
    evaluate_metrics()
