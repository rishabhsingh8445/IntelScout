from fastapi import Header, HTTPException

def get_current_user(x_user_id: str = Header(..., description="The Clerk User ID")):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    return x_user_id
