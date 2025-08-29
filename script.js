// Global variables
let currentImage = null;
let processedImage = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    
    // Handle window resize to adjust container heights
    window.addEventListener('resize', function() {
        if (currentImage) {
            const originalPreview = document.getElementById('originalPreview');
            const highResPreview = document.getElementById('highResPreview');
            
            if (originalPreview && originalPreview.complete) {
                adjustContainerHeight(originalPreview, 'original');
            }
            if (highResPreview && highResPreview.complete) {
                adjustContainerHeight(highResPreview, 'processed');
            }
        }
    });
});

// Setup event listeners
function setupEventListeners() {
    // File input change handler
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageUpload);
    }
    
    // Choose Files button - only this should trigger file selection
    const chooseFilesBtn = document.querySelector('.upload-btn');
    if (chooseFilesBtn) {
        chooseFilesBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (imageInput) {
                imageInput.click();
            }
        });
    }
    
    // Download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadProcessedImage);
    }
    
    // GIF buttons
    const createGifBtn = document.getElementById('createGifBtn');
    if (createGifBtn) {
        createGifBtn.addEventListener('click', createGif);
    }
    
    const downloadGifBtn = document.getElementById('downloadGifBtn');
    if (downloadGifBtn) {
        downloadGifBtn.addEventListener('click', downloadGif);
    }
    
    // Character buttons
    const characterBtns = document.querySelectorAll('.character-btn');
    characterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            selectCharacter(btn);
        });
    });
}

// Handle image upload
function handleImageUpload(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showStatus('Please select a valid image file.', 'error');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showStatus('Image file is too large. Please select an image smaller than 10MB.', 'error');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            currentImage = e.target.result;
            displayOriginalImage();
            showPreviewSection();
            showStatus('Image uploaded! Processing...', 'info');
            
            // Auto-process the image after a short delay to ensure original image is loaded
            setTimeout(processImage, 1000);
        };
        reader.onerror = function() {
            showStatus('Error reading image file. Please try again.', 'error');
        };
        reader.readAsDataURL(file);
    }
    // Reset input
    e.target.value = '';
}

// Display original image
function displayOriginalImage() {
    const originalPreview = document.getElementById('originalPreview');
    if (originalPreview) {
        originalPreview.src = currentImage;
        // Adjust container height based on image size
        originalPreview.onload = function() {
            adjustContainerHeight(originalPreview, 'original');
        };
    }
}

// Show preview section
function showPreviewSection() {
    const previewSection = document.getElementById('previewSection');
    
    if (previewSection) previewSection.style.display = 'block';
}

// Process image
function processImage() {
    if (!currentImage) {
        showStatus('Please upload an image first.', 'error');
        return;
    }
    
    showStatus('Processing image...', 'info');
    
    // Show loading animation
    showLoadingAnimation();
    
    // Send to backend - always use high-res upscale
    // Use different endpoints for local development vs production
    const apiEndpoint = window.location.port === '8080' ? '/process-image' : 'https://pixelartsmoother.onrender.com/process-image';
    fetch(apiEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: currentImage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            processedImage = data.processedImage;
            displayProcessedImage();
            showStatus('Processing complete!', 'success');
            
            // Enable download button
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) downloadBtn.disabled = false;
        } else {
            showStatus('Processing failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('Processing failed. Please try again.', 'error');
    })
    .finally(() => {
        // Hide loading animation
        hideLoadingAnimation();
    });
}

// Display processed image
function displayProcessedImage() {
    if (!processedImage) return;
    
    const highResPreview = document.getElementById('highResPreview');
    
    if (highResPreview) {
        highResPreview.src = processedImage;
        // Adjust container height based on processed image size
        highResPreview.onload = function() {
            adjustContainerHeight(highResPreview, 'processed');
        };
    }
}

// Download processed image
function downloadProcessedImage() {
    if (!processedImage) {
        showStatus('No processed image to download.', 'error');
        return;
    }
    
    const link = document.createElement('a');
    link.href = processedImage;
    link.download = 'processed_pixel_art.png';
    link.click();
    showStatus('Download started!', 'success');
}

// Select character for GIF
function selectCharacter(btn) {
    // Remove active class from all buttons
    document.querySelectorAll('.character-btn').forEach(b => b.classList.remove('active'));
    
    // Add active class to clicked button
    btn.classList.add('active');
    
    // Enable create GIF button
    const createGifBtn = document.getElementById('createGifBtn');
    if (createGifBtn) createGifBtn.disabled = false;
}

// Create GIF
function createGif() {
    const activeBtn = document.querySelector('.character-btn.active');
    if (!activeBtn) {
        showStatus('Please select a character first.', 'error');
        return;
    }
    
    const character = activeBtn.dataset.character;
    showStatus('Creating GIF...', 'info');
    
    // Show loading state on the button
    const createGifBtn = document.getElementById('createGifBtn');
    if (createGifBtn) {
        const btnText = createGifBtn.querySelector('.btn-text');
        const btnLoading = createGifBtn.querySelector('.btn-loading');
        if (btnText && btnLoading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
        }
        createGifBtn.disabled = true;
    }
    
    // Use different endpoints for local development vs production
    const gifEndpoint = window.location.port === '8080' ? '/create-gif' : 'https://pixelartsmoother.onrender.com/api/create-gif';
    fetch(gifEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            character: character
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('GIF created successfully!', 'success');
            
            // Enable download GIF button
            const downloadGifBtn = document.getElementById('downloadGifBtn');
            if (downloadGifBtn) {
                downloadGifBtn.disabled = false;
                downloadGifBtn.dataset.gifData = data.gifData;
            }
        } else {
            showStatus('GIF creation failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showStatus('GIF creation failed. Please try again.', 'error');
    })
    .finally(() => {
        // Reset button state
        if (createGifBtn) {
            const btnText = createGifBtn.querySelector('.btn-text');
            const btnLoading = createGifBtn.querySelector('.btn-loading');
            if (btnText && btnLoading) {
                btnText.style.display = 'flex';
                btnLoading.style.display = 'none';
            }
            createGifBtn.disabled = false;
        }
    });
}

// Download GIF
function downloadGif() {
    const downloadGifBtn = document.getElementById('downloadGifBtn');
    if (!downloadGifBtn || !downloadGifBtn.dataset.gifData) {
        showStatus('No GIF to download.', 'error');
        return;
    }
    
    const link = document.createElement('a');
    link.href = downloadGifBtn.dataset.gifData;
    link.download = 'pixel_art_animation.gif';
    link.click();
    showStatus('GIF download started!', 'success');
}

// Show loading animation
function showLoadingAnimation() {
    const highResLoader = document.getElementById('highResLoader');
    const highResPreview = document.getElementById('highResPreview');
    
    if (highResLoader && highResPreview) {
        highResPreview.style.display = 'none';
        highResLoader.style.display = 'flex';
        
        // Set a minimum height for the loading animation
        const container = highResLoader.closest('.image-container');
        if (container) {
            container.style.height = '200px';
        }
    }
}

// Hide loading animation
function hideLoadingAnimation() {
    const highResLoader = document.getElementById('highResLoader');
    const highResPreview = document.getElementById('highResPreview');
    
    if (highResLoader && highResPreview) {
        highResLoader.style.display = 'none';
        highResPreview.style.display = 'block';
    }
}

// Adjust container size to fit image optimally
function adjustContainerHeight(img, type) {
    const container = img.closest('.image-container');
    if (!container) return;
    
    // Get the natural dimensions of the image
    const imgWidth = img.naturalWidth;
    const imgHeight = img.naturalHeight;
    
    // Get the available container width (accounting for padding/borders)
    const containerWidth = container.offsetWidth - 20;
    
    // Calculate the maximum height available (considering viewport and other elements)
    const viewportHeight = window.innerHeight;
    const maxAvailableHeight = Math.min(600, viewportHeight * 0.6); // Use 60% of viewport height max
    
    // Calculate the optimal size to fit the image
    const aspectRatio = imgHeight / imgWidth;
    
    // Calculate height needed for the image to fit the container width
    let targetHeight = containerWidth * aspectRatio;
    
    // If the calculated height is too tall, scale down to fit
    if (targetHeight > maxAvailableHeight) {
        const scaleFactor = maxAvailableHeight / targetHeight;
        targetHeight = maxAvailableHeight;
        // Adjust the image display to maintain aspect ratio
        img.style.width = (containerWidth * scaleFactor) + 'px';
        img.style.height = 'auto';
    } else {
        // Reset image styling to use container's natural sizing
        img.style.width = '100%';
        img.style.height = 'auto';
    }
    
    // Ensure minimum height for small images
    targetHeight = Math.max(150, targetHeight);
    
    // Set the container height
    container.style.height = targetHeight + 'px';
}

// Show status message
function showStatus(message, type) {
    // Remove existing status message
    const existingStatus = document.querySelector('.status-message');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create new status message
    const statusDiv = document.createElement('div');
    statusDiv.className = `status-message ${type}`;
    statusDiv.textContent = message;
    document.body.appendChild(statusDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (statusDiv.parentNode) {
            statusDiv.remove();
        }
    }, 3000);
}
