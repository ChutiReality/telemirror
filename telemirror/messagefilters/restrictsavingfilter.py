from typing import Tuple, Type

from telethon import TelegramClient, types

from ..hints import EventLike, EventMessage
from .base import MessageFilter


class RestrictSavingContentBypassFilter(MessageFilter):
    """Filter that bypasses `saving content restriction`

    Sample implementation:

    Download the media, upload it to the Telegram servers,
    and then change to the new uploaded media

    ```
    # If here is media and noforwards enabled
    if message.chat.noforwards and message.media:
        # Handle images
        if isinstance(message.media, types.MessageMediaPhoto):
            client: TelegramClient = message.client
            photo: bytes = await client.download_media(message=message, file=bytes)
            cloned_photo: types.TypeInputFile = await client.upload_file(photo)
            message.media = cloned_photo
        # Others media types set to None (remove from original message)...
        else:
            message.media = None

    return True, message
    ```
    """

    @property
    def restricted_content_allowed(self) -> bool:
        return True

    async def _process_message(
        self, message: EventMessage, event_type: Type[EventLike]
    ) -> Tuple[bool, EventMessage]:
        
        if message.media is None or (
            message.chat is None or not message.chat.noforwards
        ):
            # Forwarding allowed
            return True, message
        
        client: TelegramClient = message.client
        
        # Handle images
        if isinstance(message.media, types.MessageMediaPhoto):
            photo: bytes = await client.download_media(message = message, file = bytes)
            cloned_photo: types.TypeInputFile = await client.upload_file(photo)
            cloned_photo.name = (
                message.file.name if message.file.name else "photo.jpg"
            )
            message.media = cloned_photo
        # Others media types set to None (remove from original message)...
        else:
            message.media = None

        # Process message if not empty
        return bool(message.media or message.message), message