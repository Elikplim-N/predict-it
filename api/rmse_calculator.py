"""RMSE calculation utility for CSV predictions"""
import pandas as pd
import numpy as np
from io import StringIO
from typing import Tuple, Optional

def find_value_column(df: pd.DataFrame, preferred_name: str) -> Optional[str]:
    """Auto-detect numeric column if configured column doesn't exist"""
    # First try configured name
    if preferred_name in df.columns:
        return preferred_name
    
    # Try common variations
    common_names = ['prediction', 'value', 'output', 'target', 'y', 'predictions', 'values', 'outputs']
    for name in common_names:
        if name.lower() in [c.lower() for c in df.columns]:
            # Find case-insensitive match
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
    
    # Last resort: use last numeric column
    for col in reversed(df.columns):
        try:
            pd.to_numeric(df[col], errors='coerce').sum()
            return col
        except:
            pass
    
    return None

def find_id_column(df: pd.DataFrame, preferred_name: str) -> Optional[str]:
    """Auto-detect ID column if configured column doesn't exist"""
    # First try configured name
    if preferred_name in df.columns:
        return preferred_name
    
    # Try common ID column names
    common_names = ['id', 'index', 'sample_id', 'sample', 'record_id', 'idx']
    for name in common_names:
        if name.lower() in [c.lower() for c in df.columns]:
            for col in df.columns:
                if col.lower() == name.lower():
                    return col
    
    # Use first column if it looks like ID
    if len(df.columns) > 1:
        return df.columns[0]
    return None

def calculate_rmse(
    prediction_csv: str,
    ground_truth_csv: str,
    id_column: str = "id",
    value_column: str = "value"
) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculate RMSE between prediction and ground truth CSVs
    
    Args:
        prediction_csv: CSV string content of predictions
        ground_truth_csv: CSV string content of ground truth
        id_column: Name of ID column (for alignment)
        value_column: Name of value column to compare
    
    Returns:
        Tuple of (rmse_value, error_message)
        If successful, returns (float, None)
        If error, returns (None, error_string)
    """
    try:
        # Read CSVs from string content
        pred_df = pd.read_csv(StringIO(prediction_csv))
        truth_df = pd.read_csv(StringIO(ground_truth_csv))
        
        # Auto-detect columns
        pred_value_col = find_value_column(pred_df, value_column)
        if not pred_value_col:
            return None, f"Could not find numeric column for values. Available columns: {', '.join(pred_df.columns)}"
        
        truth_value_col = find_value_column(truth_df, value_column)
        if not truth_value_col:
            return None, f"Could not find numeric column in ground truth. Available columns: {', '.join(truth_df.columns)}"
        
        # Try to align by ID column if found
        pred_id_col = find_id_column(pred_df, id_column)
        if pred_id_col:
            truth_id_col = find_id_column(truth_df, id_column)
            if truth_id_col and pred_id_col in pred_df.columns and truth_id_col in truth_df.columns:
                try:
                    pred_df = pred_df.sort_values(pred_id_col).reset_index(drop=True)
                    truth_df = truth_df.sort_values(truth_id_col).reset_index(drop=True)
                except:
                    pass
        
        # Convert to numeric arrays
        predictions_array = pd.to_numeric(pred_df[pred_value_col], errors='coerce').values
        truth_array = pd.to_numeric(truth_df[truth_value_col], errors='coerce').values
        
        # Remove NaN values
        mask = ~(np.isnan(predictions_array) | np.isnan(truth_array))
        predictions_array = predictions_array[mask]
        truth_array = truth_array[mask]
        
        if len(predictions_array) == 0:
            return None, "No valid numeric values found in CSV files"
        
        if len(predictions_array) != len(truth_array):
            return None, f"Row count mismatch: {len(predictions_array)} predictions vs {len(truth_array)} ground truth values"
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((predictions_array - truth_array) ** 2))
        return float(rmse), None
        
    except Exception as e:
        return None, f"Error processing CSV: {str(e)}"
