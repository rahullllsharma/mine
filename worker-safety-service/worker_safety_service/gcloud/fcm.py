from typing import Optional

import firebase_admin  # type:ignore
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError  # type: ignore
from google.oauth2.service_account import Credentials

from worker_safety_service.config import Settings

from .fcm_cred import FIREBASE_APP_CREDENTIALS

settings = Settings()


class FirebaseMessagingService:
    _credentials: Optional[Credentials] = None
    _initialized = False

    def __init__(self) -> None:
        if not FirebaseMessagingService._initialized:
            self._credentials = credentials.Certificate(FIREBASE_APP_CREDENTIALS)
            firebase_admin.initialize_app(credential=self._credentials)
            FirebaseMessagingService._initialized = True

    async def send_message(
        self, token: str, title: str, body: str, data: dict | None = None
    ) -> str:
        """
        Send a notification to a device.

        :param token: Device registration token.
        :param title: Notification title.
        :param body: Notification body.
        :param data: Additional data (optional).
        :return: Response from FCM.
        """
        # Build the notification message
        notification = messaging.Notification(title=title, body=body)

        # Build the message object
        message = messaging.Message(
            notification=notification,
            token=token,
            data=data if data else {},
        )

        try:
            response: str = messaging.send(message)

            if response.startswith("projects/"):
                return response
            else:
                raise ValueError("Unexpected response format: " + response)
        except FirebaseError as e:
            # Handle Firebase-specific errors
            return f"Failed to send message: {str(e)}"
        except Exception as e:
            # Handle any other errors
            return f"An error occurred: {str(e)}"
