"""Database helper for Supabase PostgreSQL operations"""
import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    return create_client(url, key)

def get_user_by_index(student_index: str):
    """Get user by student index"""
    supabase = get_supabase_client()
    response = supabase.table("users").select("*").eq("student_index", student_index).execute()
    return response.data[0] if response.data else None

def create_user(student_index: str, password_hash: str, name: str):
    """Create new user"""
    supabase = get_supabase_client()
    response = supabase.table("users").insert({
        "student_index": student_index,
        "password_hash": password_hash,
        "name": name
    }).execute()
    return response.data[0] if response.data else None

def get_admin(username: str):
    """Get admin by username"""
    supabase = get_supabase_client()
    response = supabase.table("admin").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None

def get_active_ground_truth():
    """Get active ground truth file"""
    supabase = get_supabase_client()
    response = supabase.table("ground_truth").select("*").eq("is_active", True).order("upload_date", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

def create_submission(user_id: int, filename: str, rmse: float):
    """Create submission record"""
    supabase = get_supabase_client()
    response = supabase.table("submissions").insert({
        "user_id": user_id,
        "filename": filename,
        "rmse": rmse
    }).execute()
    return response.data[0] if response.data else None

def get_user_submissions(user_id: int):
    """Get all submissions for a user"""
    supabase = get_supabase_client()
    response = supabase.table("submissions").select("*").eq("user_id", user_id).order("submission_date", desc=True).execute()
    return response.data

def get_user_best_score(user_id: int):
    """Get best RMSE score for a user"""
    supabase = get_supabase_client()
    response = supabase.table("submissions").select("rmse").eq("user_id", user_id).order("rmse", desc=False).limit(1).execute()
    return response.data[0]["rmse"] if response.data else None

def get_leaderboard():
    """Get leaderboard with best scores"""
    supabase = get_supabase_client()
    # Note: This uses a PostgreSQL view created in the setup
    response = supabase.table("leaderboard_view").select("*").order("best_rmse", desc=False).execute()
    return response.data

def create_ground_truth(filename: str, file_data: str):
    """Create new ground truth record and deactivate old ones"""
    supabase = get_supabase_client()
    
    # Deactivate all existing ground truths
    supabase.table("ground_truth").update({"is_active": False}).neq("id", 0).execute()
    
    # Insert new ground truth
    response = supabase.table("ground_truth").insert({
        "filename": filename,
        "file_data": file_data,
        "is_active": True
    }).execute()
    return response.data[0] if response.data else None

def get_column_settings():
    """Get column configuration"""
    supabase = get_supabase_client()
    
    id_col_response = supabase.table("settings").select("setting_value").eq("setting_key", "id_column").execute()
    value_col_response = supabase.table("settings").select("setting_value").eq("setting_key", "value_column").execute()
    
    id_col = id_col_response.data[0]["setting_value"] if id_col_response.data else "id"
    value_col = value_col_response.data[0]["setting_value"] if value_col_response.data else "value"
    
    return {"id_column": id_col, "value_column": value_col}

def set_column_settings(id_col: str, value_col: str):
    """Save column configuration"""
    supabase = get_supabase_client()
    
    # Upsert ID column setting
    supabase.table("settings").upsert({
        "setting_key": "id_column",
        "setting_value": id_col
    }, on_conflict="setting_key").execute()
    
    # Upsert value column setting
    supabase.table("settings").upsert({
        "setting_key": "value_column",
        "setting_value": value_col
    }, on_conflict="setting_key").execute()

def get_statistics():
    """Get platform statistics"""
    supabase = get_supabase_client()
    
    users_count = supabase.table("users").select("id", count="exact").execute()
    submissions_count = supabase.table("submissions").select("id", count="exact").execute()
    
    return {
        "total_students": users_count.count,
        "total_submissions": submissions_count.count
    }
