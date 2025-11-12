import os
from flask import Flask, render_template, request, jsonify, send_file
from advanced_downloader import AdvancedYouTubeDownloader
from pathlib import Path
import threading
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 


downloader = AdvancedYouTubeDownloader(output_dir='downloads')


download_status = {}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        info = downloader.get_video_info(url)
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video with options"""
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'best')
        format_type = data.get('format', 'mp4')
        include_subtitles = data.get('subtitles', False)
        audio_only = data.get('audioOnly', False)
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        download_id = str(time.time())
        download_status[download_id] = {'status': 'downloading', 'progress': 0}
        
        def download_task():
            result = downloader.download_with_options(
                url=url,
                quality=quality,
                format_type=format_type,
                include_subtitles=include_subtitles,
                audio_only=audio_only,
                download_id=download_id
            )
            download_status[download_id] = result
        
        thread = threading.Thread(target=download_task)
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download started'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download-status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """Check download status"""
    status = download_status.get(download_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/api/download-file/<filename>', methods=['GET'])
def download_file(filename):
    """Download the file"""
    try:
        filepath = os.path.join('downloads', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/playlist-download', methods=['POST'])
def download_playlist():
    """Download entire playlist"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        result = downloader.download_playlist(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)