import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)

# Configuration - REPLACE THESE VALUES
TARGET_CHANNEL_ID = 1352506574459113553  # Replace with your channel ID
BOT_TOKEN = 'MTM4MDk2MjcwNjg3MzY0NzI0NA.GSXgkV.DHKXKkdASob5Y0r1sA6NHc-onDgar1yePhfAbY'  # Replace with your actual bot token
TEMP_FOLDER = "database"

# Ensure temp directory exists
os.makedirs(TEMP_FOLDER, exist_ok=True)

async def download_media(url: str, format_type: str) -> str:
    """Download media from URL and return file path"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(TEMP_FOLDER, f'%(title)s_{format_type}.%(ext)s'),
            'restrictfilenames': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format_type == 'mp3' else [],
            'merge_output_format': 'mp4',
            'extract_flat': False,
            'noplaylist': True,
            'ignoreerrors': False,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'force-ipv4': True,
            'cookiefile': 'cookies.txt'
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:  # Playlist or similar
                info = info['entries'][0]
            
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3' and not filename.endswith('.mp3'):
                filename = os.path.splitext(filename)[0] + '.mp3'
            return filename
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

def cleanup_files(*files):
    """Safely remove files if they exist"""
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

def is_tiktok_url(url: str) -> bool:
    """Check if the URL is from TikTok"""
    return 'tiktok.com' in url.lower()

def is_youtube_url(url: str) -> bool:
    """Check if the URL is from YouTube"""
    return 'youtube.com' in url.lower() or 'youtu.be' in url.lower()

@bot.command()
async def download(ctx, url: str = None):
    """Download media from YouTube or TikTok (both MP3 and MP4)"""
    # Check if URL is provided
    if url is None:
        embed = discord.Embed(
            title="❌ Command Usage",
            description="Please provide a valid URL after the command.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Correct Usage",
            value="`-download <youtube-or-tiktok-url>`",
            inline=False
        )
        embed.add_field(
            name="Examples",
            value="YouTube: `-download https://youtu.be/example`\nTikTok: `-download https://tiktok.com/example`",
            inline=False
        )
        await ctx.send(embed=embed)
        return

    mp4_path, mp3_path = None, None
    processing_msg = None
    
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            embed = discord.Embed(
                title="❌ Invalid URL",
                description="Please provide a valid URL starting with http:// or https://",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if URL is from supported platforms
        if not is_youtube_url(url) and not is_tiktok_url(url):
            embed = discord.Embed(
                title="❌ Unsupported Platform",
                description="This bot only supports YouTube and TikTok URLs.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Send processing message
        processing_msg = await ctx.send("⏳ Waiting #1...")
        
        # Get target channel by ID
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            await processing_msg.edit(content="❌ Target channel not found! Please check the channel ID.")
            return
        
        # Get video info for title
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Downloaded Media')
            platform = "TikTok" if is_tiktok_url(url) else "YouTube"
        
        # Download both MP3 and MP4 regardless of platform
        await processing_msg.edit(content="⏳ Waiting MP4...")
        mp4_path = await download_media(url, 'mp4')
        
        await processing_msg.edit(content="⏳ Waiting MP3...")
        mp3_path = await download_media(url, 'mp3')
        
        # Verify files exist before sending
        if not os.path.exists(mp4_path):
            raise Exception("MP4 file failed to download")
        if not os.path.exists(mp3_path):
            raise Exception("MP3 file failed to download")
        
        # Prepare embed
        embed = discord.Embed(
            title=f"🎬 {platform}: {title}",
            description=f"Requested by {ctx.author.mention}",
            color=discord.Color.blue() if is_tiktok_url(url) else discord.Color.red()
        )
        embed.add_field(name="Original URL", value=f"[Click Here]({url})", inline=False)
        embed.set_footer(text="Downloaded using yt-dlp")
        
        # Check file sizes (Discord has 25MB upload limit for non-nitro)
        mp4_size = os.path.getsize(mp4_path) / (1024 * 1024)  # in MB
        mp3_size = os.path.getsize(mp3_path) / (1024 * 1024)  # in MB
        
        if mp4_size > 25 or mp3_size > 25:
            embed.add_field(
                name="⚠️ Note", 
                value="One or more files were too large to upload (Discord limit: 25MB).",
                inline=False
            )
            await target_channel.send(embed=embed)
        else:
            await target_channel.send(
                embed=embed,
                files=[
                    discord.File(mp4_path, filename="video.mp4"),
                    discord.File(mp3_path, filename="audio.mp3")
                ]
            )
        
        await processing_msg.edit(content="✅ Successfully!")
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if "HTTP Error 403" in str(e):
            error_msg = "❌ The platform is blocking this download. Try again later."
        elif "Unsupported URL" in str(e):
            error_msg = "❌ Unsupported URL. Please provide a valid YouTube or TikTok URL."
        elif "Private video" in str(e):
            error_msg = "❌ This video is private and cannot be downloaded."
        elif "Copyright" in str(e):
            error_msg = "❌ This video cannot be downloaded due to copyright restrictions."
        
        if processing_msg:
            await processing_msg.edit(content=error_msg)
        else:
            await ctx.send(error_msg)
    finally:
        # Clean up files safely
        cleanup_files(mp4_path, mp3_path)

@download.error
async def download_error(ctx, error):
    """Handles errors for the download command"""
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing URL",
            description="You need to provide a URL to download.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Correct Usage",
            value="`-download <youtube-or-tiktok-url>`",
            inline=False
        )
        embed.add_field(
            name="Examples",
            value="YouTube: `-download https://youtu.be/example`\nTikTok: `-download https://tiktok.com/example`",
            inline=False
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ An unexpected error occurred: {str(error)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `-help` to see available commands.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Run the bot
bot.run(BOT_TOKEN)

