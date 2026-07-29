from fastapi import Depends, HTTPException, status

from app.models import User
from app.utils.oauth2 import get_current_user


def role_required(required_role: str):

    def checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action"
            )

        return current_user

    return checker