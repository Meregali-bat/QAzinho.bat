import discord
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont, ImageOps

async def new_member(member):
    channel = discord.utils.get(member.guild.text_channels, name='hora_do_café')
    if channel:
        # Download the user's avatar
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as response:
                avatar_bytes = await response.read()

        # Open the avatar image
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        # Resize the avatar to fit the background
        avatar_size = (100, 100)
        avatar = avatar.resize(avatar_size)

        # Create a circular mask
        mask = Image.new("L", avatar_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_size, fill=255)

        # Apply the mask to the avatar
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # Create a new image with a white border around the circular avatar
        border_size = 4
        border_avatar_size = (avatar_size[0] + 2 * border_size, avatar_size[1] + 2 * border_size)
        border_avatar = Image.new("RGBA", border_avatar_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(border_avatar)
        draw.ellipse((0, 0) + border_avatar_size, fill=(255, 255, 255, 255))
        border_avatar.paste(avatar, (border_size, border_size), avatar)

        # Open the background image
        bg_image = Image.open('./Assets/background2.png')

        # Calculate the position to center the avatar on the background
        bg_width, bg_height = bg_image.size
        avatar_width, avatar_height = border_avatar.size
        position = (
            (bg_width - avatar_width) // 2,
            (bg_height - avatar_height) // 2
        )

        # Paste the avatar with border onto the background
        bg_image.paste(border_avatar, position, border_avatar)

        # Add text to the image
        draw = ImageDraw.Draw(bg_image)
        font = ImageFont.truetype("arial.ttf", 20)
        text = f'Bem-vindo, {member.name}, novo suporte do grupo W2A!'
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (
            (bg_width - text_width) // 2,
            position[1] + avatar_height + 10
        )
        draw.text(text_position, text, (255, 255, 255), font=font)

        # Save the image to a BytesIO object
        with io.BytesIO() as image_binary:
            bg_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await channel.send(file=discord.File(fp=image_binary, filename='welcome.png'))