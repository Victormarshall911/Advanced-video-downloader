const videoUrlInput = document.getElementById('videoUrl');
const getInfoBtn = document.getElementById('getInfoBtn');
const videoInfoSection = document.getElementById('videoInfo');
const downloadOptionsSection = document.getElementById('downloadOptions');
const progressSection = document.getElementById('progressSection');
const completeSection = document.getElementById('completeSection');
const downloadBtn = document.getElementById('downloadBtn');
const playlistUrlInput = document.getElementById('playlistUrl');
const downloadPlaylistBtn = document.getElementById('downloadPlaylistBtn');
const newDownloadBtn = document.getElementById('newDownloadBtn');
const downloadFileBtn = document.getElementById('downloadFileBtn');

let currentDownloadFilename = '';

getInfoBtn.addEventListener('click', async () => {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    getInfoBtn.disabled = true;
    getInfoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    try {
        const response = await fetch('/api/video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayVideoInfo(data);
            videoInfoSection.style.display = 'block';
            downloadOptionsSection.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error fetching video info: ' + error.message);
    } finally {
        getInfoBtn.disabled = false;
        getInfoBtn.innerHTML = '<i class="fas fa-info-circle"></i> Get Info';
    }
});

function displayVideoInfo(data) {
    document.getElementById('thumbnail').src = data.thumbnail;
    document.getElementById('videoTitle').textContent = data.title;
    document.getElementById('uploader').textContent = data.uploader;
    document.getElementById('views').textContent = formatNumber(data.view_count);
    document.getElementById('duration').textContent = formatDuration(data.duration);
    
    const chaptersInfo = document.getElementById('chaptersInfo');
    if (data.chapter_count > 0) {
        chaptersInfo.innerHTML = `
            <h4><i class="fas fa-list"></i> ${data.chapter_count} Chapters Found</h4>
            <p style="color: var(--text-secondary); font-size: 14px;">
                All chapters will be merged into one video file
            </p>
            <ul style="margin-top: 10px; padding-left: 20px; color: var(--text-secondary); font-size: 13px;">
                ${data.chapters.slice(0, 5).map(ch => 
                    `<li>${ch.title}</li>`
                ).join('')}
                ${data.chapter_count > 5 ? `<li>... and ${data.chapter_count - 5} more</li>` : ''}
            </ul>
        `;
    } else {
        chaptersInfo.innerHTML = '<p style="color: var(--text-secondary);">No chapters in this video</p>';
    }
}

downloadBtn.addEventListener('click', async () => {
    const url = videoUrlInput.value.trim();
    const quality = document.getElementById('quality').value;
    const format = document.getElementById('format').value;
    const subtitles = document.getElementById('subtitles').checked;
    const audioOnly = document.getElementById('audioOnly').checked;
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting Download...';
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                quality,
                format,
                subtitles,
                audioOnly
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            downloadOptionsSection.style.display = 'none';
            progressSection.style.display = 'block';
            pollDownloadStatus(data.download_id);
        } else {
            alert('Error: ' + data.error);
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Video';
        }
    } catch (error) {
        alert('Error starting download: ' + error.message);
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Video';
    }
});

function pollDownloadStatus(downloadId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/download-status/${downloadId}`);
            const data = await response.json();
            
            if (data.success) {
                clearInterval(interval);
                showDownloadComplete(data.filename);
            } else if (data.error) {
                clearInterval(interval);
                alert('Download failed: ' + data.error);
                resetInterface();
            } else {
                document.getElementById('progressText').textContent = 'Downloading and processing video...';
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 2000);
}

function showDownloadComplete(filename) {
    currentDownloadFilename = filename;
    progressSection.style.display = 'none';
    completeSection.style.display = 'block';
    document.getElementById('downloadedFileName').textContent = `File: ${filename}`;
}

downloadFileBtn.addEventListener('click', () => {
    window.location.href = `/api/download-file/${currentDownloadFilename}`;
});

newDownloadBtn.addEventListener('click', () => {
    resetInterface();
});

downloadPlaylistBtn.addEventListener('click', async () => {
    const url = playlistUrlInput.value.trim();
    
    if (!url) {
        alert('Please enter a playlist URL');
        return;
    }
    
    if (!confirm('This will download all videos in the playlist. Continue?')) {
        return;
    }
    
    downloadPlaylistBtn.disabled = true;
    downloadPlaylistBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
    
    try {
        const response = await fetch('/api/playlist-download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Successfully downloaded ${data.video_count} videos from playlist: ${data.playlist_title}`);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error downloading playlist: ' + error.message);
    } finally {
        downloadPlaylistBtn.disabled = false;
        downloadPlaylistBtn.innerHTML = '<i class="fas fa-download"></i> Download Playlist';
    }
});

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function resetInterface() {
    videoInfoSection.style.display = 'none';
    downloadOptionsSection.style.display = 'none';
    progressSection.style.display = 'none';
    completeSection.style.display = 'none';
    downloadBtn.disabled = false;
    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Video (All Chapters Merged)';
    videoUrlInput.value = '';
}