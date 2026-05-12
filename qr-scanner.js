/**
 * Fallback QR Code Scanner - Shows camera feed when external libraries fail
 * Uses native getUserMedia API
 * Since we can't reliably load QR decoding libraries, this shows the camera
 * and lets users manually verify they're showing the right code
 */

class Html5Qrcode {
    constructor(elementId) {
        this.elementId = elementId;
        this.videoElement = null;
        this.stream = null;
        this.isScanning = false;
        this.successCallback = null;
        this.config = null;
    }

    start(constraints, config, successCallback, errorCallback) {
        return new Promise((resolve, reject) => {
            this.successCallback = successCallback;
            this.config = config || {};

            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                const err = new Error('Camera not supported on this device');
                errorCallback(err);
                reject(err);
                return;
            }

            const container = document.getElementById(this.elementId);
            if (!container) {
                reject(new Error('Container not found'));
                return;
            }

            // Clear container
            container.innerHTML = '';

            // Create video element
            this.videoElement = document.createElement('video');
            this.videoElement.setAttribute('playsinline', 'true');
            this.videoElement.setAttribute('autoplay', 'true');
            this.videoElement.setAttribute('muted', 'true');
            this.videoElement.setAttribute('webkit-playsinline', 'true');
            this.videoElement.style.width = '100%';
            this.videoElement.style.height = '300px';
            this.videoElement.style.objectFit = 'cover';
            this.videoElement.style.borderRadius = '10px';
            this.videoElement.style.display = 'block';

            container.appendChild(this.videoElement);

            // Request camera access
            navigator.mediaDevices.getUserMedia(constraints)
                .then(stream => {
                    this.stream = stream;
                    this.videoElement.srcObject = stream;
                    this.isScanning = true;
                    console.log('[QR] Camera started successfully');
                    resolve();
                })
                .catch(err => {
                    console.error('[QR] Camera error:', err);
                    errorCallback(err);
                    reject(err);
                });
        });
    }

    stop() {
        return new Promise((resolve) => {
            this.isScanning = false;
            if (this.stream) {
                this.stream.getTracks().forEach(track => {
                    track.stop();
                });
                this.stream = null;
            }
            if (this.videoElement) {
                this.videoElement.srcObject = null;
            }
            console.log('[QR] Camera stopped');
            resolve();
        });
    }

    clear() {
        const container = document.getElementById(this.elementId);
        if (container) {
            container.innerHTML = '';
        }
        if (this.videoElement) {
            this.videoElement = null;
        }
    }
}

// Make it available globally
if (typeof window !== 'undefined') {
    window.Html5Qrcode = Html5Qrcode;
    window.html5QrcodeLoaded = true;
    console.log('[QR] Fallback QR Scanner initialized');
}

