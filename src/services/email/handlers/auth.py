from typing import List

from fastapi import BackgroundTasks

from src.models import User
from src.services.email import EmailManager, EmailType


def send_new_user(user: User, otp_password: str,
                  background_tasks: BackgroundTasks, email_manager: EmailManager,
                  email_list: List[str] = None):
    if not email_list:
        # empty or none, do nothing
        return

    email_context = {
        "name": user.name,
        "username": user.username,
        "otp_password": otp_password,
    }

    background_tasks.add_task(
        email_manager.send_email,
        EmailType.WELCOME,
        email_list,
        email_context
    )


def send_password_reset(user: User, otp_password: str,
                        background_tasks: BackgroundTasks, email_manager: EmailManager,
                        email_list: List[str] = None):
    if not email_list:
        # empty or none, do nothing
        return

    email_context = {
        "name": user.name,
        "username": user.username,
        "otp_password": otp_password,
    }

    background_tasks.add_task(
        email_manager.send_email,
        EmailType.ADMIN_PASSWORD_RESET,
        email_list,
        email_context
    )


def send_password_recover(user: User, otp_password: str,
                          background_tasks: BackgroundTasks, email_manager: EmailManager,
                          email_list: List[str] = None):
    if not email_list:
        # empty or none, do nothing
        return

    email_context = {
        "name": user.name,
        "username": user.username,
        "otp_password": otp_password,
    }

    background_tasks.add_task(
        email_manager.send_email,
        EmailType.USER_PASSWORD_RECOVER,
        email_list,
        email_context
    )
