import yt_dlp
import os
from pathlib import Path
import json
import uuid

class AdvancedYouTubeDownloader:
    def __init__(self, output_dir='downloads'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                chapters = []
                if info.get('chapters'):
                    for i, chapter in enumerate(info['chapters'], 1):
                        chapters.append({
                            'number': i,
                            'title': chapter.get('title', f'Chapter {i}'),
                            'start_time': chapter.get('start_time', 0),
                            'end_time': chapter.get('end_time', 0)
                        })
                
                return {
                    'success': True,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'thumbnail': info.get('thumbnail'),
                    'chapters': chapters,
                    'chapter_count': len(chapters),
                    'description': info.get('description', '')[:300] + '...' if info.get('description') else ''
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_with_options(self, url, quality='best', format_type='mp4', 
                             include_subtitles=False, audio_only=False,
                             download_id=None):
        """
        Download with custom quality and format options
        Returns the filename of the downloaded file
        """
        
        if download_id is None:
            download_id = str(uuid.uuid4())
        
        filename_template = f'{download_id}_%(title)s.%(ext)s'

        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, filename_template),
            'embedchapters': True,
            'quiet': False,
            'no_warnings': False,
        }
        
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if quality == 'best':
                ydl_opts['format'] = f'bestvideo[ext={format_type}]+bestaudio[ext=m4a]/best[ext={format_type}]/best'
            elif quality == 'worst':
                ydl_opts['format'] = 'worst'
            else:
                height = quality.replace('p', '')
                ydl_opts['format'] = f'bestvideo[height<={height}][ext={format_type}]+bestaudio/best'
            
            ydl_opts['merge_output_format'] = format_type
        
        if include_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en']
            ydl_opts['embedsubtitles'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if audio_only:
                    filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                else:
                    filename = ydl.prepare_filename(info)
                
                return {
                    'success': True,
                    'filename': os.path.basename(filename),
                    'filepath': filename,
                    'title': info.get('title')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_playlist(self, playlist_url, merge_chapters=True):
        """Download entire YouTube playlist"""
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': os.path.join(self.output_dir, '%(playlist)s/%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'embedchapters': merge_chapters,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=True)
                return {
                    'success': True,
                    'playlist_title': info.get('title'),
                    'video_count': len(info.get('entries', []))
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }