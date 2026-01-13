/**
 * Hesap Paylaş - Main Application Script
 * Version: 2.0.7-force-deploy
 * Last Updated: 2026-01-11 13:45:00
 * NOTE: Service Worker disabled - Using HTTP headers for cache control only
 * BUILD: Forced Render redeploy - Timestamp marker to verify deployment
 */

// SERVICE WORKER COMPLETELY DISABLED
// Browser will use HTTP Cache-Control headers from backend
// This is more reliable than Service Worker caching
console.log('[APP] Service Worker disabled - using HTTP headers for cache control');

// If there's an existing Service Worker, unregister it
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
        registrations.forEach(registration => {
            registration.unregister();
            console.log('[APP] Service Worker unregistered');
        });
    }).catch(err => {
        console.log('[APP] Error unregistering Service Worker:', err);
    });
}

// PWA Install Prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Install button gösterilebilir
});

// Handle deep links when page loads
window.addEventListener('load', () => {
    console.log('[APP] Page loaded - checking for deep links');
    handleDeepLink();
});

// Deep Link Handler - URL parametrelerini kontrol et
function handleDeepLink() {
    const params = new URLSearchParams(window.location.search);
    // Support both formats: "123-456" (formatted) and "123456" (raw 6-digit)
    let groupCode = params.get('code') || params.get('groupCode');
    
    if (groupCode && (/^\d{3}-\d{3}$/.test(groupCode) || /^\d{6}$/.test(groupCode) || /^\d{3}-\d{3}-\d{3}$/.test(groupCode))) {
        console.log('Deep link detected with code:', groupCode);
        
        // Eğer user login'se direkt gruba katıl
        const token = localStorage.getItem('hesapPaylas_token');
        if (token) {
            // User varsa, gruba direkt katıl
            console.log('User logged in, joining group with code:', groupCode);
            joinGroupWithCode(groupCode);
        } else {
            // Login değilse, group code'u sessionStorage'e kaydet ve login sayfasına yönlendir
            sessionStorage.setItem('pendingGroupCode', groupCode);
        }
    }
}

// Grup kodunu kullanarak gruba katıl
function joinGroupWithCode(groupCode) {
    const token = localStorage.getItem('hesapPaylas_token');
    if (!token) {
        showNotification('Lütfen önce giriş yapınız');
        return;
    }
    
    const baseURL = getBaseURL();
    fetch(`${baseURL}/api/groups/join`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: groupCode })
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => ({
                ok: response.ok,
                status: response.status,
                data: data
            }));
        } else {
            return {
                ok: response.ok,
                status: response.status,
                data: { error: 'Invalid response format' }
            };
        }
    })
    .then(result => {
        if (result.ok && result.data) {
            showNotification(`✅ "${result.data.name}" grubuna başarıyla katıldınız!`);
            setTimeout(() => {
                loadActiveGroups();
                showPage('homePage');
            }, 1500);
        } else if (result.data && result.data.message) {
            // Already member or other success
            showNotification(`✅ "${result.data.name}" grubundasınız!`);
            setTimeout(() => {
                loadActiveGroups();
                showPage('homePage');
            }, 1500);
        } else {
            showNotification(result.data?.error || 'Gruba katılım başarısız');
        }
    })
    .catch(error => {
        console.error('Grup katılım hatası:', error);
        showNotification('Gruba katılım başarısız');
    });
}

// ===== API CONFIGURATION =====

// Detect environment and set API base URL
const API_BASE_URL = (() => {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Local development detection
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        // Local: Frontend runs on Live Server (usually port 5500 or 3000)
        // Backend runs on Flask (port 5000)
        // Always use backend's actual port
        console.log('[API] Local environment detected - using Flask backend on port 5000');
        return `${protocol}//${hostname}:5000/api`;
    }
    
    // Production: API is on same server/port (via nginx proxy)
    const baseUrl = port ? `${protocol}//${hostname}:${port}` : `${protocol}//${hostname}`;
    return `${baseUrl}/api`;
})();

console.log('[API] Base URL:', API_BASE_URL);

// Helper function to get base URL for API
function getBaseURL() {
    return API_BASE_URL.replace('/api', '');
}

// Helper function to get app base URL (for sharing/invitations)
function getAppURL() {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Local development: use Flask backend
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return `${protocol}//${hostname}:5000`;
    }
    
    // Production: use current domain
    return port ? `${protocol}//${hostname}:${port}` : `${protocol}//${hostname}`;
}

// ==================== Sidebar Menu Functions ====================

// Sidebar menüyü aç/kapat
function toggleSideMenu() {
    const menu = document.getElementById('sideMenu');
    const overlay = document.getElementById('sideMenuOverlay');
    
    if (menu.style.left === '-280px' || menu.style.left === '') {
        menu.style.left = '0';
        overlay.style.background = 'rgba(0,0,0,0.5)';
        overlay.style.display = 'block';
    } else {
        menu.style.left = '-280px';
        overlay.style.background = 'rgba(0,0,0,0)';
        overlay.style.display = 'none';
    }
}

// Menu öğelerine tıklandığında
function navigateToMenu(item) {
    toggleSideMenu(); // Menüyü kapat
    
    switch(item) {
        case 'groups':
            showGroupsPage();
            break;
        case 'reservations':
            alert('📅 Rezervasyonlarım sayfası yakında açılacak!');
            break;
        case 'orders':
            alert('🛒 Siparişlerim sayfası yakında açılacak!');
            break;
        case 'favorites':
            alert('⭐ Favori Yerlerim sayfası yakında açılacak!');
            break;
        case 'coupons':
            alert('🎟️ Kuponlarım sayfası yakında açılacak!');
            break;
        case 'rewards':
            alert('🏆 Ödül Puanlarım sayfası yakından açılacak!');
            break;
    }
}

const GOOGLE_CLIENT_ID = '625132087724-43j0qmqgh8kds471d73oposqthr8tt1h.apps.googleusercontent.com';

// Initialize Google Sign-In
window.addEventListener('load', () => {
    // Google Sign-In devre dışı bırakıldı
    /*
    if (window.google && window.google.accounts && window.location.hostname !== 'localhost') {
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleResponse
        });
        
        const container = document.getElementById('googleSignInContainer');
        if (container) {
            google.accounts.id.renderButton(container, {
                type: 'standard',
                size: 'large',
                text: 'signin_with',
                locale: 'tr'
            });
        }
    }
    */
});

// Handle Google Sign-In Response
function handleGoogleResponse(response) {
    const token = response.credential;
    console.log('Google token received:', token.substring(0, 20) + '...');
    
    // Backend'e token gönder
    api.googleSignup(token)
        .then(response => {
            // Save token and user
            localStorage.setItem('hesapPaylas_token', response.token);
            localStorage.setItem('hesapPaylas_user', JSON.stringify(response.user));
            app.currentUser = response.user;

            // Check for pending group code after Google login
            const pendingCode = sessionStorage.getItem('pendingGroupCode');
            if (pendingCode) {
                console.log('Processing pending group code after Google login:', pendingCode);
                sessionStorage.removeItem('pendingGroupCode');
                setTimeout(() => {
                    joinGroupWithCode(pendingCode);
                }, 500);
            }

            showPage('homePage');
        })
        .catch(error => {
            alert('Google ile giriş başarısız: ' + error.message);
        });
}

// Grup Kur/Katıl butonuna tıklandığında kullanıcı kontrolü
function checkUserAndNavigate() {
    const user = localStorage.getItem('hesapPaylas_user');
    if (user) {
        // User zaten login'se direkt grup kur sayfasına git
        showPage('groupChoicePage');
    } else {
        // User login değilse üye girişi sayfasına git
        showPage('onboardingPage');
    }
}

// Rezervasyon için kullanıcı kontrolü
function checkUserForReservation() {
    const user = localStorage.getItem('hesapPaylas_user');
    if (user) {
        // User login'se rezervasyon sayfasına git
        showPage('reservationPage');
    } else {
        // User login değilse üye girişi sayfasına git
        showPage('onboardingPage');
    }
}

// Ana sayfada profil bilgilerini güncelle
function updateHomePageProfile() {
    const user = localStorage.getItem('hesapPaylas_user');
    const profileBtn = document.getElementById('homeProfileBtn');
    const welcomeMessage = document.getElementById('homeWelcomeMessage');
    const userName = document.getElementById('homeUserName');
    const userMenu = document.getElementById('homeUserMenu');
    
    if (user) {
        try {
            const userData = JSON.parse(user);
            // Profil butonunu GİZLE (sidebar menüde var)
            if (profileBtn) profileBtn.style.display = 'none';
            
            // Hoşgeldin mesajını göster
            if (welcomeMessage && userName) {
                userName.textContent = userData.firstName || userData.name || 'Kullanıcı';
                welcomeMessage.style.display = 'block';
            }
            
            // User menu göster
            if (userMenu) userMenu.style.display = 'block';
            
        } catch (e) {
            console.error('User data parse error:', e);
        }
    } else {
        // Login yoksa profil ve menu gizle
        if (profileBtn) profileBtn.style.display = 'none';
        if (welcomeMessage) welcomeMessage.style.display = 'none';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Sayfa yüklenince profil bilgilerini güncelle
window.addEventListener('DOMContentLoaded', () => {
    updateHomePageProfile();
});

// Örnek mekanlar
// Merkez konum: 40°59'21.6"N 29°02'28.3"E (40.9893, 29.0412)
const userLocation = { lat: 40.9893, lng: 29.0412 };

const venues = {
    restaurant: [
        { name: 'Tarihi Kebapçı', phone: '+90 541 234 5678', address: 'Kızılay, Ankara', lat: 40.9910, lng: 29.0430, distance: 0.3 },
        { name: 'Modern Pizza House', phone: '+90 542 345 6789', address: 'Tunalı Hilmi Cad., Ankara', lat: 40.9875, lng: 29.0390, distance: 0.4 },
        { name: 'Lezzetli Cafe', phone: '+90 543 456 7890', address: 'Çankaya, Ankara', lat: 40.9850, lng: 29.0450, distance: 0.6 },
        { name: 'Deniz Restaurant', phone: '+90 532 111 2233', address: 'Ulus, Ankara', lat: 40.9925, lng: 29.0380, distance: 0.7 },
        { name: 'Köşe Kahvaltı', phone: '+90 533 222 3344', address: 'Bahçelievler, Ankara', lat: 40.9800, lng: 29.0500, distance: 1.2 },
        { name: 'Izgara Köfte Salonu', phone: '+90 534 333 4455', address: 'Keçiören, Ankara', lat: 41.0050, lng: 29.0300, distance: 1.8 },
        { name: 'Tatlı Dünyası', phone: '+90 535 444 5566', address: 'Etimesgut, Ankara', lat: 40.9700, lng: 29.0600, distance: 2.5 },
        { name: 'Saray Lokantası', phone: '+90 536 555 6677', address: 'Yenimahalle, Ankara', lat: 41.0100, lng: 29.0200, distance: 3.2 },
        { name: 'Ev Yemekleri', phone: '+90 537 666 7788', address: 'Mamak, Ankara', lat: 40.9600, lng: 29.0700, distance: 4.1 },
        { name: 'Burger Station', phone: '+90 538 777 8899', address: 'Batıkent, Ankara', lat: 41.0200, lng: 29.0100, distance: 4.8 },
        { name: 'Sushi Bar', phone: '+90 539 888 9900', address: 'Çayyolu, Ankara', lat: 40.9500, lng: 29.0800, distance: 5.5 },
        { name: 'Kebap Durağı', phone: '+90 531 999 0011', address: 'Gölbaşı, Ankara', lat: 40.9400, lng: 29.0900, distance: 6.8 }
    ],
    hotel: [
        { name: 'Luxor Otel', phone: '+90 541 111 2222', address: 'Kızılay Meydanı, Ankara', lat: 40.9905, lng: 29.0425, distance: 0.2 },
        { name: 'Grand Hotel', phone: '+90 542 333 4444', address: 'Çankaya, Ankara', lat: 40.9860, lng: 29.0445, distance: 0.5 },
        { name: 'Modern Suites', phone: '+90 543 555 6666', address: 'Tunalı, Ankara', lat: 40.9880, lng: 29.0385, distance: 0.4 },
        { name: 'Ankara Palace Hotel', phone: '+90 312 468 5400', address: 'Ulus, Ankara', lat: 40.9930, lng: 29.0375, distance: 0.8 },
        { name: 'Sheraton Ankara', phone: '+90 312 457 6000', address: 'Kavaklidere, Ankara', lat: 40.9840, lng: 29.0460, distance: 0.9 },
        { name: 'Hilton SA', phone: '+90 312 455 0000', address: 'Tahran Cad., Ankara', lat: 40.9820, lng: 29.0480, distance: 1.3 },
        { name: 'Divan Çukurhan', phone: '+90 312 306 6400', address: 'Çukurhan, Ankara', lat: 40.9940, lng: 29.0360, distance: 1.5 },
        { name: 'JW Marriott', phone: '+90 312 248 8888', address: 'Kızılırmak, Ankara', lat: 41.0020, lng: 29.0320, distance: 2.1 },
        { name: 'Swissotel Ankara', phone: '+90 312 409 3000', address: 'José Marti Cad., Ankara', lat: 40.9780, lng: 29.0520, distance: 2.6 },
        { name: 'Radisson Blu', phone: '+90 312 310 6060', address: 'Ulus, Ankara', lat: 40.9950, lng: 29.0350, distance: 3.0 },
        { name: 'The Green Park', phone: '+90 312 457 1000', address: 'Kavaklıdere, Ankara', lat: 40.9760, lng: 29.0540, distance: 3.5 },
        { name: 'Neva Palas Hotel', phone: '+90 312 420 8090', address: 'Sıhhiye, Ankara', lat: 40.9720, lng: 29.0580, distance: 4.2 }
    ]
};

// Harita modal'ını aç
function openMapSelection() {
    const mapModal = document.getElementById('mapModal');
    mapModal.style.display = 'flex';
}

// Harita modal'ını kapat
function closeMapModal() {
    const mapModal = document.getElementById('mapModal');
    mapModal.style.display = 'none';
}

// Haritadan seçilen konumu onayla
function confirmMapLocation() {
    const locationInput = document.getElementById('locationInput');
    const location = locationInput.value.trim();
    
    if (!location) {
        alert('Lütfen konum adresini giriniz!');
        return;
    }
    
    // Seçilen konumu kaydet
    const targetLocationInput = document.getElementById('targetLocation');
    targetLocationInput.value = location;
    
    closeMapModal();
}

// Mekan detaylarını göster (yeni sayfa)
function showVenueDetail(venue) {
    // Venue bilgilerini sakla
    window.currentVenue = venue;
    
    // Sayfa bilgilerini doldur
    document.getElementById('venueDetailName').textContent = venue.name;
    document.getElementById('venueDetailAddress').textContent = venue.address;
    document.getElementById('venuePhoneText').textContent = venue.phone;
    document.getElementById('venuePhoneButton').href = 'tel:' + venue.phone;
    
    // Mesafe ve tür bilgisi
    if (venue.distance) {
        document.getElementById('venueDetailDistance').textContent = venue.distance + ' km uzaklıkta';
    }
    
    // Tür bilgisi
    const venueType = window.reservationSelectedType === 'restaurant' ? 'Cafe / Restaurant' : 'Hotel';
    document.getElementById('venueDetailType').textContent = venueType;
    
    // Yeni sayfayı aç
    showPage('venueDetailPage');
}

// E-rezervasyon işlemi
function handleEreservation() {
    const venue = window.currentVenue;
    if (venue) {
        alert('📧 ' + venue.name + ' için e-rezervasyon sayfası yakında açılacak...');
    }
}

// Adrese navigasyon
function navigateToVenue() {
    const venue = window.currentVenue;
    if (venue && venue.lat && venue.lng) {
        // Google Maps'te navigasyon başlat (yeni sekmede)
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${venue.lat},${venue.lng}&travelmode=driving`;
        window.open(mapsUrl, '_blank');
    } else if (venue && venue.address) {
        // Adres varsa adresi kullan
        const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(venue.address)}`;
        window.open(mapsUrl, '_blank');
    }
}

// Rezervasyon arama işlemi
function handleReservationSearch() {
    const manualVenueName = document.getElementById('manualVenueName').value.trim();
    const selectedType = window.reservationSelectedType;
    
    if (manualVenueName) {
        // Manuel giriş varsa onu göster
        showVenueDetail({
            name: manualVenueName,
            phone: '+90 541 234 5678',
            address: 'Ankara'
        });
    } else if (selectedType) {
        // Seçilen türün sonuçlarını göster (her zaman 2 km çapında filtrele)
        let results = venues[selectedType];
        
        // Hedef konuma göre 2 km içindekileri göster
        results = results.filter(venue => venue.distance <= 2);
        
        if (results && results.length > 0) {
            displaySearchResults(results);
        } else {
            alert('Yakınınızda mekan bulunamadı.');
        }
    } else {
        alert('Lütfen bir mekan türü seçin veya mekan adı girin.');
    }
}

// Arama sonuçlarını göster
function displaySearchResults(results) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    
    // Mesafeye göre sırala
    const sortedResults = [...results].sort((a, b) => a.distance - b.distance);
    
    // Başlığı güncelle
    const venueType = window.reservationSelectedType === 'restaurant' ? 'Cafe / Restaurant' : 'Hotel';
    document.getElementById('searchResultsTitle').textContent = venueType + ' Arama Sonuçları (' + sortedResults.length + ')';
    
    sortedResults.forEach(venue => {
        const resultItem = document.createElement('div');
        resultItem.style.cssText = 'padding: 12px; background: white; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; transition: all 0.3s;';
        resultItem.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="margin: 0 0 4px 0; color: #333;">${venue.name}</h4>
                    <p style="margin: 0; font-size: 0.85em; color: #999;">${venue.address}</p>
                    <p style="margin: 4px 0 0 0; font-size: 0.8em; color: #4A90E2;">📍 ${venue.distance} km uzaklıkta</p>
                </div>
                <span style="font-size: 1.2em;">→</span>
            </div>
        `;
        resultItem.onmouseover = () => resultItem.style.background = '#f5f5f5';
        resultItem.onmouseout = () => resultItem.style.background = 'white';
        resultItem.onclick = () => showVenueDetail(venue);
        resultsList.appendChild(resultItem);
    });
    
    // Yeni sayfayı aç
    showPage('searchResultsPage');
}

// Seçim türünü kaydet
function setReservationType(type) {
    window.reservationSelectedType = type;
}

// API Helper Functions
const api = {
    async request(method, endpoint, data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        const token = localStorage.getItem('hesapPaylas_token');
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            
            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const result = await response.json();
                    console.error('API Error:', result);
                    throw result; // JSON'u doğrudan fırlat
                } else {
                    const error = `HTTP ${response.status}: ${response.statusText}`;
                    console.error('API Error:', error);
                    throw new Error(error);
                }
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                throw new Error('Invalid response format from server');
            }
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    signup(firstName, lastName, email, password, phone) {
        return this.request('POST', '/auth/signup', {
            firstName,
            lastName,
            email,
            password,
            phone
        });
    },

    login(email, password) {
        return this.request('POST', '/auth/login', {
            email,
            password
        });
    },

    requestPasswordReset(email) {
        return this.request('POST', '/auth/request-password-reset', {
            email
        });
    },

    resetPassword(resetToken, newPassword) {
        return this.request('POST', '/auth/reset-password', {
            resetToken,
            newPassword
        });
    },

    googleSignup(token) {
        return this.request('POST', '/auth/google', {
            token
        });
    },

    getProfile() {
        return this.request('GET', '/user/profile');
    },

    updateProfile(data) {
        return this.request('PUT', '/user/profile', data);
    },

    createGroup(name, description) {
        return this.request('POST', '/groups', {
            name,
            description
        });
    },

    getGroup(groupId) {
        return this.request('GET', `/groups/${groupId}`);
    },

    createOrder(groupId, restaurant, items) {
        return this.request('POST', '/orders', {
            groupId,
            restaurant,
            items
        });
    },

    getOrder(orderId) {
        return this.request('GET', `/orders/${orderId}`);
    }
};

// Veri Yönetimi
const app = {
    currentMode: null, // 'group' veya 'individual'
    currentUser: null,
    currentRestaurant: null,
    cart: {},
    restaurants: {},
    groupId: null
};

// ===== ONBOARDING / SIGNUP FONKSIYONLARI =====

// Google Sign-In
function signInWithGoogle() {
    console.log("Google ile giriş yapılıyor...");
    // SDK otomatik button render etmeli
}

// Facebook Sign-In
function signInWithFacebook() {
    console.log("Facebook ile giriş yapılıyor...");
    alert('Facebook OAuth entegrasyonu henüz uygulanmadı. Lütfen manuel kaydolunuz.');
}

// Apple Sign-In
function signInWithApple() {
    console.log("Apple ile giriş yapılıyor...");
    alert('Apple OAuth entegrasyonu henüz uygulanmadı. Lütfen manuel kaydolunuz.');
}

// Manuel Kaydolma
function handleManualSignup(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('signupFirstName').value.trim();
    const lastName = document.getElementById('signupLastName').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validasyon
    if (!firstName || !lastName || !phone || !email || !password) {
        alert('Lütfen tüm alanları doldurunuz!');
        return;
    }
    
    // Email validasyonu
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Geçerli bir e-posta adresi giriniz!');
        return;
    }
    
    // Telefon validasyonu (11 hane)
    const cleanPhone = phone.replace(/\D/g, '');
    if (cleanPhone.length !== 11) {
        alert('Telefon numarası 11 haneli olmalıdır (örn: 05323332222)!');
        return;
    }
    
    // Backend API'ye kayıt isteği gönder
    api.signup(firstName, lastName, email, password, phone)
        .then(response => {
            // Kayıt başarılı - giriş yap
            localStorage.setItem('hesapPaylas_token', response.token);
            localStorage.setItem('hesapPaylas_user', JSON.stringify(response.user));
            
            app.currentUser = response.user;
            
            // Formu temizle
            document.getElementById('manualSignupForm').reset();
            
            // Ana sayfaya git
            showPage('homePage');
            updateHomePageProfile();
        })
        .catch(error => {
            console.error('Signup error:', error);
            let errorMsg = 'Kayıt sırasında hata oluştu';
            const errorStr = error.message || error.toString();
            if (errorStr.includes('already exists') || errorStr.includes('Email already exists')) {
                errorMsg = 'Bu e-posta adresi zaten kayıtlı!';
            } else {
                errorMsg = errorStr;
            }
            alert(errorMsg);
        });
}

// Kayıt Tamamlama
function completeSignup(userData) {
    app.currentUser = userData;
    localStorage.setItem('hesapPaylas_user', JSON.stringify(userData));
    
    console.log("Kullanıcı kaydı tamamlandı:", userData);
    
    showPage('homePage');
}

// Kaydolmış Kullanıcı Kontrolü
function checkExistingUser() {
    const token = localStorage.getItem('hesapPaylas_token');
    const storedUser = localStorage.getItem('hesapPaylas_user');
    
    if (token && storedUser) {
        try {
            app.currentUser = JSON.parse(storedUser);
            // Token varsa API'ye authenticate et
            api.getProfile()
                .then(profile => {
                    app.currentUser = profile;
                    localStorage.setItem('hesapPaylas_user', JSON.stringify(profile));
                    showPage('homePage');
                })
                .catch(error => {
                    // Token geçersiz, logout yap
                    console.log('Token invalid:', error);
                    logout();
                });
        } catch (e) {
            logout();
        }
    } else {
        showPage('onboardingPage');
    }
}

// ===== SAYFA YÖNETİMİ =====

// ===== AUTHENTICATION FORM SWITCHING =====

function showAuthForm(formType) {
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const resetForm = document.getElementById('resetPasswordForm');
    const signupTabBtn = document.getElementById('signupTabBtn');
    const loginTabBtn = document.getElementById('loginTabBtn');
    
    if (formType === 'signup') {
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
        resetForm.style.display = 'none';
        signupTabBtn.classList.add('active');
        loginTabBtn.classList.remove('active');
    } else {
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';
        resetForm.style.display = 'none';
        signupTabBtn.classList.remove('active');
        loginTabBtn.classList.add('active');
    }
}

// Manuel Giriş
function handleManualLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        alert('E-posta ve şifre alanlarını doldurunuz!');
        return;
    }
    
    // Backend API'ye giriş isteği gönder
    api.login(email, password)
        .then(response => {
            // Giriş başarılı
            localStorage.setItem('hesapPaylas_token', response.token);
            localStorage.setItem('hesapPaylas_user', JSON.stringify(response.user));
            
            app.currentUser = response.user;
            
            // Kullanıcının aktif gruplarını kontrol et
            const token = response.token;
            // IMPORTANT: Start with button hidden - let loadActiveGroups() decide
            document.getElementById('activeGroupButton').style.display = 'none';
            
            fetch(`${API_BASE_URL}/user/groups`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => response.json())
            .then(groups => {
                // loadActiveGroups() will show/hide button based on groups
                loadActiveGroups();
                
                // Check if there's a pending group code to join (from deep link)
                const pendingCode = sessionStorage.getItem('pendingGroupCode');
                if (pendingCode) {
                    console.log('Processing pending group code from deep link:', pendingCode);
                    sessionStorage.removeItem('pendingGroupCode');
                    setTimeout(() => {
                        joinGroupWithCode(pendingCode);
                    }, 500);
                }
            })
            .catch(error => {
                console.error('Error checking groups:', error);
                // Hata durumunda balonu gizli tut - loadActiveGroups() da gizler
                document.getElementById('activeGroupButton').style.display = 'none';
                loadActiveGroups();
            });
            
            // Form alanlarını temizle
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPassword').value = '';
            
            // Ana sayfaya yönlendir
            showPage('homePage');
            updateHomePageProfile();
        })
        .catch(error => {
            console.error('Login error:', error);
            // error nesnesi hem string hem object olabilir, kontrol et
            let errorCode = '';
            if (typeof error === 'object' && error.error) {
                errorCode = error.error;
            } else if (typeof error === 'string') {
                errorCode = error;
            } else if (error.message) {
                errorCode = error.message;
            }
            if (errorCode.includes('user_not_found')) {
                alert('Sistemde böyle bir kullanıcı bulunmuyor... Üye ol sayfasına yönlendirileceksiniz...');
                showAuthForm('signup');
                showPage('onboardingPage');
            } else if (errorCode.includes('wrong_password')) {
                alert('Şifre yanlış!');
            } else {
                alert('Giriş sırasında hata oluştu: ' + errorCode);
            }
        });
}

// Şifre Sıfırlama Formu Göster
function showPasswordResetForm() {
    const loginForm = document.getElementById('loginForm');
    const resetForm = document.getElementById('resetPasswordForm');
    
    loginForm.style.display = 'none';
    resetForm.style.display = 'block';
}

// Şifre Sıfırlama İşlemi
function handlePasswordReset(event) {
    event.preventDefault();
    
    const email = document.getElementById('resetEmail').value.trim();
    const resetCodeSection = document.getElementById('resetCodeSection');
    const resetCode = document.getElementById('resetCode').value.trim();
    const newPassword = document.getElementById('newPassword').value;
    const resetToken = document.getElementById('resetToken').value;
    const submitBtn = document.getElementById('resetSubmitBtn');
    
    // Step 1: Request reset code
    if (!resetCode && !resetToken) {
        if (!email) {
            alert('E-posta adresi gereklidir!');
            return;
        }
        
        // Request password reset
        api.requestPasswordReset(email)
            .then(response => {
                alert('Sıfırlama kodu e-posta adresinize gönderilmiştir!');
                
                // Store reset token
                document.getElementById('resetToken').value = response.resetToken;
                
                // Show code input section
                resetCodeSection.style.display = 'block';
                submitBtn.textContent = 'ŞİFREYİ SIFIRLA';
                
                // For demo: show the token in console (in production, user gets it via email)
                console.log('Reset Token (for demo):', response.resetToken);
            })
            .catch(error => {
                alert('Hata: ' + (error.message || error.toString()));
            });
    }
    // Step 2: Reset password with code
    else if (resetCode && newPassword && resetToken) {
        if (!newPassword || newPassword.length < 6) {
            alert('Şifre en az 6 karakter olmalıdır!');
            return;
        }
        
        // Reset password
        api.resetPassword(resetToken, newPassword)
            .then(response => {
                alert('Şifreniz başarıyla değiştirilmiştir! Giriş yapabilirsiniz.');
                
                // Clear form
                document.getElementById('resetForm').reset();
                document.getElementById('resetToken').value = '';
                resetCodeSection.style.display = 'none';
                submitBtn.textContent = 'KOD GÖNDER';
                
                // Go back to login
                showAuthForm('login');
            })
            .catch(error => {
                alert('Hata: ' + (error.message || error.toString()));
            });
    } else {
        alert('Lütfen tüm alanları doldurunuz!');
    }
}

// Profil Sayfasına Git
// Telefon numarasını mask formatı ile göster: 0532 333 22 22 (11 hane)
function formatPhoneDisplay(phone) {
    if (!phone) return '-';
    // Sadece rakamları al
    const cleaned = phone.replace(/\D/g, '');
    // Türk telefon formatı: 0XXXX XXX XX XX (11 hane)
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{4})(\d{3})(\d{2})(\d{2})/, '$1 $2 $3 $4');
    }
    return phone;
}

// Telefon input için mask
function formatPhoneInput(value) {
    if (!value) return '';
    // Sadece rakamları al
    let cleaned = value.replace(/\D/g, '');
    // Maksimum 11 haneli
    if (cleaned.length > 11) cleaned = cleaned.slice(0, 11);
    
    // Format uygula: 0XXXX XXX XX XX
    if (cleaned.length === 0) return '';
    if (cleaned.length <= 4) return cleaned;
    if (cleaned.length <= 7) return cleaned.replace(/(\d{4})(\d{0,3})/, '$1 $2');
    if (cleaned.length <= 9) return cleaned.replace(/(\d{4})(\d{3})(\d{0,2})/, '$1 $2 $3');
    return cleaned.replace(/(\d{4})(\d{3})(\d{2})(\d{0,2})/, '$1 $2 $3 $4');
}

// Input event handler
function handlePhoneInput(input) {
    input.value = formatPhoneInput(input.value);
}

function goToProfile() {
    console.log('goToProfile called');
    
    // localStorage'dan kullanıcı bilgisini al
    const storedUser = localStorage.getItem('hesapPaylas_user');
    console.log('Stored user:', storedUser);
    
    if (!storedUser) {
        alert('Lütfen önce giriş yapınız!');
        showPage('onboardingPage');
        return;
    }
    
    let user;
    try {
        user = JSON.parse(storedUser);
        console.log('Parsed user:', user);
    } catch (e) {
        console.error('User parse error:', e);
        alert('Lütfen tekrar giriş yapınız!');
        showPage('onboardingPage');
        return;
    }
    
    // app.currentUser'ı da güncelle
    app.currentUser = user;
    
    // Profil bilgilerini doldur
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    const profilePhone = document.getElementById('profilePhone');
    const profileEmailInfo = document.getElementById('profileEmailInfo');
    
    if (profileName) profileName.textContent = `${user.firstName || ''} ${user.lastName || ''}`.trim() || 'Kullanıcı';
    if (profileEmail) profileEmail.textContent = user.email || '';
    // Telefonu mask formatı ile göster
    if (profilePhone) profilePhone.textContent = formatPhoneDisplay(user.phone || '-');
    if (profileEmailInfo) profileEmailInfo.textContent = user.email || '';

    
    console.log('Opening profile modal');
    openProfileModal();
}

// Profile Modal Functions
function openProfileModal() {
    const modal = document.getElementById('profilePage');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profilePage');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Bonus Puanlarını Güncelle
function updateBonusPoints() {
    // Demo veri - gerçek uygulamada database'ten gelecek
    const bonusPoints = (app.currentUser && app.currentUser.bonusPoints) || 2450;
    const status = calculateMemberStatus(bonusPoints);
    
    const bonusPointsEl = document.getElementById('bonusPoints');
    const statusBadgeEl = document.getElementById('statusBadge');
    const progressFillEl = document.getElementById('progressFill');
    
    if (bonusPointsEl) {
        bonusPointsEl.textContent = `${bonusPoints.toLocaleString('tr-TR')} Puan`;
    }
    
    if (statusBadgeEl) {
        statusBadgeEl.textContent = status.name;
    }
    
    // Progress bar'ı güncelle
    const progressPercentage = (bonusPoints / 5000) * 100;
    if (progressFillEl) {
        progressFillEl.style.width = Math.min(progressPercentage, 100) + '%';
    }
    
    // Seviyeler ve avantajları güncelle
    updateLevelDisplay(status);
}

// Üyelik Seviyesi Hesapla
function calculateMemberStatus(points) {
    if (points >= 5000) {
        return {
            name: 'Gold Üye',
            level: 'gold',
            icon: '🥇',
            benefits: ['%10 bonus puan', 'Özel indirim kuponları', 'Doğum günü hediyesi', 'VIP müşteri desteği']
        };
    } else if (points >= 1001) {
        return {
            name: 'Silver Üye',
            level: 'silver',
            icon: '🥈',
            benefits: ['%5 bonus puan', 'İndirim kuponları', 'Öncelikli destek']
        };
    } else {
        return {
            name: 'Bronze Üye',
            level: 'bronze',
            icon: '🥉',
            benefits: ['Standart puan kazanımı', 'Hoş geldin kuponu']
        };
    }
}

// Seviye Görüntüsünü Güncelle
function updateLevelDisplay(status) {
    const levels = document.querySelectorAll('.level');
    levels.forEach(level => {
        level.classList.remove('active');
    });
    
    const statusToIndex = { 'bronze': 0, 'silver': 1, 'gold': 2 };
    const activeIndex = statusToIndex[status.level];
    if (levels[activeIndex]) {
        levels[activeIndex].classList.add('active');
    }
    
    // Avantajları güncelle
    const benefitsList = document.querySelector('.level-benefits ul');
    if (benefitsList && status.benefits) {
        benefitsList.innerHTML = status.benefits.map(benefit => 
            `<li>✅ ${benefit}</li>`
        ).join('');
    }
}

// Profil Düzenle
function editProfile() {
    const newPhone = prompt('Yeni telefon numarası girin:', app.currentUser.phone);
    if (newPhone && newPhone.trim()) {
        app.currentUser.phone = newPhone;
        localStorage.setItem('hesapPaylas_user', JSON.stringify(app.currentUser));
        goToProfile();
        alert('Telefon numarası güncellendi!');
    }
}

// Siparişleri Görüntüle
function viewOrders() {
    alert('Siparişler sayfası yakında açılacak! 🚀');
}

// Sipariş Detayları
function viewOrderDetails(orderId) {
    const orders = [
        {
            id: 1,
            restaurant: 'Tarihi Kebapçı',
            date: '20 Aralık 2025, 19:30',
            amount: 285.50,
            items: [
                { name: 'Adana Kebap', qty: 2, price: 120 },
                { name: 'Ayran', qty: 2, price: 12 },
                { name: 'Patlıcan Salatası', qty: 1, price: 25 }
            ],
            tax: 30,
            delivery: 15,
            members: ['Siz', 'Ahmet', 'Merve']
        },
        {
            id: 2,
            restaurant: 'Modern Pizza House',
            date: '18 Aralık 2025, 18:45',
            amount: 156.00,
            items: [
                { name: 'Margarita Pizza', qty: 1, price: 80 },
                { name: 'Sodaları', qty: 2, price: 18 }
            ],
            tax: 14.50,
            delivery: 0,
            members: ['Siz', 'Ali']
        }
    ];
    
    const order = orders.find(o => o.id === orderId);
    if (order) {
        let detailsText = `
📋 ${order.restaurant}
📅 ${order.date}

🛒 Siparişler:
`;
        order.items.forEach(item => {
            detailsText += `  • ${item.name} (${item.qty} adet) - ₺${item.price}\n`;
        });
        
        detailsText += `
💰 Özet:
  Alt Total: ₺${(order.amount - order.tax - order.delivery).toFixed(2)}
  Vergi: ₺${order.tax}
  Teslimat: ₺${order.delivery}
  Toplam: ₺${order.amount}

👥 Katılımcılar: ${order.members.join(', ')}
`;
        alert(detailsText);
    }
}

// Rezervasyonları Yönet
function viewReservations() {
    alert('Rezervasyon yönetim sayfası yakında açılacak! 🚀');
}

// Kupon Sekmesi Değiştir
function switchCouponTab(tab) {
    const activeCoupons = document.getElementById('activeCoupons');
    const usedCoupons = document.getElementById('usedCoupons');
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    if (tab === 'active') {
        activeCoupons.style.display = 'grid';
        usedCoupons.style.display = 'none';
    } else {
        activeCoupons.style.display = 'none';
        usedCoupons.style.display = 'grid';
    }
}

// Ödeme Yöntemi Ekle
function addPaymentMethod() {
    alert('Yeni kart ekleme sayfası yakında açılacak! 💳');
}

// Şifre Değiştir
function changePassword() {
    const oldPassword = prompt('Eski şifrenizi girin:');
    if (!oldPassword) return;
    
    const newPassword = prompt('Yeni şifrenizi girin:');
    if (!newPassword) return;
    
    const confirmPassword = prompt('Yeni şifrenizi doğrulayın:');
    if (newPassword !== confirmPassword) {
        alert('Şifreler eşleşmiyor!');
        return;
    }
    
    alert('Şifreniz başarıyla değiştirildi! 🔐');
}

// Profile Modal Functions
function openProfileModal() {
    const modal = document.getElementById('profilePage');
    console.log('Modal element:', modal);
    console.log('Modal BEFORE - display:', modal.style.display, 'zIndex:', modal.style.zIndex);
    if (modal) {
        modal.style.display = 'flex';
        modal.style.visibility = 'visible';
        modal.style.zIndex = '9999';
        modal.style.opacity = '1';
        console.log('Modal AFTER - display:', modal.style.display, 'zIndex:', modal.style.zIndex);
        document.body.style.overflow = 'hidden';
    } else {
        console.error('profilePage modal not found!');
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profilePage');
    if (modal) {
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        document.body.style.overflow = 'auto';
    }
}

// Çıkış Yap
function logout() {
    // FORCE HIDE EVERYTHING from home page IMMEDIATELY
    const homeMenu = document.getElementById('homeUserMenu');
    if (homeMenu) {
        homeMenu.style.display = 'none';
        homeMenu.style.visibility = 'hidden';
        homeMenu.style.opacity = '0';
        homeMenu.style.zIndex = '-9999';
    }
    
    const profileBtn = document.getElementById('homeProfileBtn');
    if (profileBtn) {
        profileBtn.style.display = 'none';
    }
    
    // Floating grup butonunu gizle
    const activeGroupButton = document.getElementById('activeGroupButton');
    if (activeGroupButton) {
        activeGroupButton.style.display = 'none';
    }
    
    const homePage = document.getElementById('homePage');
    if (homePage) {
        homePage.style.display = 'none';
        homePage.style.visibility = 'hidden';
        homePage.style.zIndex = '-9999';
        homePage.style.opacity = '0';
    }
    
    app.currentUser = null;
    localStorage.removeItem('hesapPaylas_user');
    localStorage.removeItem('hesapPaylas_token');
    
    // Close profile modal if open
    closeProfileModal();
    
    // Profil bilgilerini gizle
    updateHomePageProfile();
    
    showPage('onboardingPage');
}

// Hesabı Kapatma (Deactivate)
function closeAccountPrompt() {
    const user = JSON.parse(localStorage.getItem('hesapPaylas_user') || '{}');
    if (!user.is_account_owner) {
        alert('❌ Sadece hesap sahibi bu işlemi yapabilir.\nSiz bu hesaba katılan bir üyesiniz.');
        return;
    }
    
    const confirmed = confirm('Hesabınızı kapatmak istediğinizden emin misiniz?\n\n⚠️ Hesap kapatıldığında:\n- Aktif olmaktan çıkacak\n- Tüm verileriniz korunacak\n- Daha sonra tekrar açabilirsiniz');
    
    if (!confirmed) return;
    
    const token = localStorage.getItem('hesapPaylas_token');
    fetch(`${API_BASE_URL}/user/close-account`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert('❌ Hata: ' + data.error);
        } else {
            alert('✅ Hesabınız başarıyla kapatıldı.\nTüm verileriniz güvende.')
            logout();
        }
    })
    .catch(error => {
        alert('❌ Hesap kapatma hatası: ' + error.message);
    });
}

// Hesabı Silme (Delete)
function deleteAccountPrompt() {
    const user = JSON.parse(localStorage.getItem('hesapPaylas_user') || '{}');
    if (!user.is_account_owner) {
        alert('❌ Sadece hesap sahibi bu işlemi yapabilir.\nSiz bu hesaba katılan bir üyesiniz.');
        return;
    }
    
    const confirmed = confirm('⚠️ DİKKAT! Hesabınızı SİLMEK istediğinizden emin misiniz?\n\n🗑️ Hesap silme sırasında:\n- Hesapınız ve tüm verileri kalıcı olarak silinecek\n- Bu işlem GERİ ALINMAZ\n- Kapalı hesaplar silinemez\n\nEmin misiniz?');
    
    if (!confirmed) return;
    
    // Onay için şifre iste
    const password = prompt('Şifrenizi girin (onay için):');
    if (!password) return;
    
    const token = localStorage.getItem('hesapPaylas_token');
    fetch(`${API_BASE_URL}/user/delete-account`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert('❌ Hata: ' + data.error);
        } else {
            alert('🗑️ Hesabınız kalıcı olarak silinmiştir.\nTüm verileriniz kaldırılmıştır.');
            logout();
        }
    })
    .catch(error => {
        alert('❌ Hesap silme hatası: ' + error.message);
    });
}

// localStorage işlemleri
function saveToLocalStorage() {
    localStorage.setItem('app_state', JSON.stringify(app));
}

function loadFromLocalStorage() {
    const saved = localStorage.getItem('app_state');
    if (saved) {
        Object.assign(app, JSON.parse(saved));
    }
}

// Sayfa yönetimi
function showPage(pageId) {
    // FORCE hide ALL home menu elements first
    const homeMenu = document.getElementById('homeUserMenu');
    if (homeMenu) {
        homeMenu.style.display = 'none';
        homeMenu.style.visibility = 'hidden';
        homeMenu.style.opacity = '0';
    }
    
    const profileBtn = document.getElementById('homeProfileBtn');
    if (profileBtn) {
        profileBtn.style.display = 'none';
    }
    
    // Hide ALL pages completely
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
        page.style.visibility = 'hidden';
        page.style.opacity = '0';
        page.style.zIndex = '-1';
        page.classList.remove('active');
    });
    
    // Show ONLY the requested page
    const page = document.getElementById(pageId);
    if (page) {
        page.style.display = 'block';
        page.style.visibility = 'visible';
        page.style.opacity = '1';
        page.style.position = 'relative';
        page.style.zIndex = pageId === 'onboardingPage' ? '100' : '1';
        page.classList.add('active');
        
        // If showing homePage, show the menu and load floating groups button
        if (pageId === 'homePage' && homeMenu) {
            homeMenu.style.display = 'block';
            homeMenu.style.visibility = 'visible';
            homeMenu.style.opacity = '1';
            
            // IMPORTANT: Don't show button directly - let loadActiveGroups() decide
            // Load active groups immediately (it will show/hide button based on group count)
            const activeGroupButton = document.getElementById('activeGroupButton');
            if (activeGroupButton) {
                activeGroupButton.style.display = 'none'; // Start hidden
                setTimeout(() => {
                    loadActiveGroups(); // This will show button if groups exist
                }, 100);
            }
        }
        
        // Show hamburger menu for all pages except onboarding
        if (pageId !== 'onboardingPage') {
            ensurePageHasMenuButton(page);
        }
        
        window.scrollTo(0, 0);
    }
}

// Ensure every page has the hamburger menu button
function ensurePageHasMenuButton(page) {
    if (!page) return;
    
    // If already has menu button, return
    if (page.querySelector('.menu-toggle-btn')) return;
    
    // Check if page already has a header with these buttons
    const header = page.querySelector('.header, .standard-header');
    if (header && header.querySelector('.menu-toggle-btn')) return;
    
    // Find or create position for button
    let container = page.querySelector('.header, .standard-header');
    
    if (container) {
        // Add menu button to existing header
        if (!container.querySelector('.menu-toggle-btn')) {
            const menuBtn = document.createElement('button');
            menuBtn.className = 'menu-toggle-btn';
            menuBtn.id = 'menuToggleBtn-' + Math.random();
            menuBtn.onclick = toggleSideMenu;
            menuBtn.title = 'Menu';
            menuBtn.innerHTML = `
                <span style="width: 20px; height: 2px; background: #333; transition: all 0.3s;"></span>
                <span style="width: 20px; height: 2px; background: #333; transition: all 0.3s;"></span>
                <span style="width: 20px; height: 2px; background: #333; transition: all 0.3s;"></span>
            `;
            menuBtn.style.cssText = 'position: absolute !important; top: 15px !important; left: 15px !important; background: white; border: none; border-radius: 8px; width: 40px; height: 40px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: all 0.3s; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; padding: 0;';
            
            container.style.position = 'relative';
            container.insertBefore(menuBtn, container.firstChild);
        }
    }
}

// Ana Sayfaya Dön
function backToHome() {
    app.currentMode = null;
    app.currentUser = null;
    app.cart = {};
    showPage('homePage');
}

// Bilgi Sayfasına Dön
function backToInfo() {
    showPage('infoPage');
}

// Restaurant Sayfasına Dön
function backToRestaurant() {
    showPage('restaurantPage');
}

// Menüye Dön
function backToMenu() {
    showPage('menuPage');
}

// ADIM 1: Grup Kur / Katıl Seçimi
function goToGroupMode() {
    showPage('groupChoicePage');
}

// Grup Kurma (eski - şimdi hamburger menüde)
function goToCreateGroup() {
    // Yeni sistem: hamburger menüdeki Gruplarım → Yeni Grup Oluştur
    showPage('homePage');
}

// Grup Katılma (eski - şimdi hamburger menüde)
function goToJoinGroup() {
    // Yeni sistem: hamburger menüdeki Gruba Katıl
    openJoinGroupModal();
}

// QR Kod Okuyucu Fonksiyonları
let qrScannerActive = false;
let qrScannerStream = null;

function startQRScanner() {
    const video = document.getElementById('qrVideo');
    const canvas = document.getElementById('qrCanvas');
    const resultDiv = document.getElementById('qrResult');
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        resultDiv.innerHTML = '<p style="color: red;">Kamera erişimi desteklenmiyor!</p>';
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
            qrScannerStream = stream;
            qrScannerActive = true;
            video.srcObject = stream;
            video.play();
            
            // QR okuma döngüsünü başlat
            scanQRCode(video, canvas, resultDiv);
        })
        .catch(err => {
            console.error('Kamera erişimi hatası:', err);
            resultDiv.innerHTML = '<p style="color: red;">Kamera erişimi reddedildi!</p>';
        });
}

function scanQRCode(video, canvas, resultDiv) {
    if (!qrScannerActive) return;
    
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    
    if (typeof jsQR !== 'undefined') {
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code) {
            console.log('QR Kod Okundu:', code.data);
            qrScannerActive = false;
            
            // Kamerayı kapat
            stopQRScanner();
            
            // Deep link formatını kontrol et: hesappaylas://join?code=xxx-xxx&name=groupname
            if (code.data.startsWith('hesappaylas://')) {
                // Deep link formatı
                const urlParams = new URLSearchParams(code.data.replace('hesappaylas://join?', ''));
                const groupCode = urlParams.get('code');
                
                if (groupCode && /^\d{3}-\d{3}$/.test(groupCode)) {
                    resultDiv.innerHTML = `<p style="color: green; font-weight: bold;">✓ Kod okundu: ${groupCode}</p>`;
                    proceedToJoinGroup(groupCode);
                } else {
                    resultDiv.innerHTML = '<p style="color: red;">Geçersiz QR kod</p>';
                    qrScannerActive = true;
                    setTimeout(() => scanQRCode(video, canvas, resultDiv), 500);
                }
            } else {
                // Eski format uyumluluğu: "groupname-xxx-xxx" (6 haneli format)
                const parts = code.data.split('-');
                if (parts.length === 3) {
                    const groupCode = `${parts[1]}-${parts[2]}`;
                    resultDiv.innerHTML = `<p style="color: green; font-weight: bold;">✓ Kod okundu: ${groupCode}</p>`;
                    proceedToJoinGroup(groupCode);
                } else {
                    resultDiv.innerHTML = '<p style="color: orange;">Geçersiz QR kod formatı</p>';
                    qrScannerActive = true;
                    setTimeout(() => scanQRCode(video, canvas, resultDiv), 500);
                }
            }
        } else {
            requestAnimationFrame(() => scanQRCode(video, canvas, resultDiv));
        }
    } else {
        resultDiv.innerHTML = '<p style="color: red;">jsQR kütüphanesi yüklenmedi!</p>';
    }
}

function backToJoinCodePage() {
    showPage('joinCodePage');
    document.getElementById('joinGroupCode').value = '';
    document.getElementById('joinCodeResult').innerHTML = '';
}

function proceedToJoinGroup(groupCode) {
    // Gruba katılma işlemini başlat
    app.currentMode = 'join_group';
    app.groupCode = groupCode.trim();
    
    document.getElementById('infoTitle').innerText = 'Bilgilerinizi Girin';
    document.getElementById('groupIdGroup').style.display = 'none';
    document.getElementById('infoFirstName').value = '';
    document.getElementById('infoLastName').value = '';
    
    // 1 saniye sonra info sayfasına git
    setTimeout(() => {
        showPage('infoPage');
    }, 1000);
}

function submitJoinCode() {
    const groupCode = document.getElementById('joinGroupCode').value.trim();
    const resultDiv = document.getElementById('joinCodeResult');
    
    if (!groupCode) {
        resultDiv.innerHTML = '<p style="color: red;">Lütfen grup kodunu giriniz!</p>';
        return;
    }
    
    // Kod formatını doğrula (xxx-xxx - 6 haneli)
    if (!/^\d{3}-\d{3}$/.test(groupCode)) {
        resultDiv.innerHTML = '<p style="color: red;">Geçersiz kod formatı! (xxx-xxx şeklinde olmalı)</p>';
        return;
    }
    
    resultDiv.innerHTML = '<p style="color: green; font-weight: bold;">✓ Kod doğrulandı!</p>';
    
    // Bilgi sayfasına git
    setTimeout(() => {
        proceedToJoinGroup(groupCode);
    }, 500);
}

function stopQRScanner() {
    qrScannerActive = false;
    const video = document.getElementById('qrVideo');
    
    if (qrScannerStream) {
        qrScannerStream.getTracks().forEach(track => track.stop());
        qrScannerStream = null;
    }
    
    if (video) {
        video.srcObject = null;
    }
}

function backToGroupChoice() {
    stopQRScanner();
    showPage('groupChoicePage');
}

// Rezervasyon / Kupon Sayfası
function goToReservationMode() {
    alert('Rezervasyon ve Kupon özellikleri yakında gelecek!');
    // Şimdilik placeholder - ileride implement edilecek
}

// ESKI: Bireysel Sipariş (artık kullanılmıyor - goToGroupMode ile birleştirildi)
function goToIndividualMode() {
    goToGroupMode();
}

// ADIM 2: Bilgi Girişi
function submitInfo() {
    const firstName = document.getElementById('infoFirstName').value.trim();
    const lastName = document.getElementById('infoLastName').value.trim();
    
    if (!firstName) {
        alert('Lütfen adınızı girin!');
        return;
    }

    app.currentUser = `${firstName} ${lastName}`;
    app.cart[app.currentUser] = [];
    
    // Grup kuruyorsa, Backend API'ye istek gönder
    if (app.currentMode === 'create_group') {
        // Yeni grup oluşturma başarılı, ana sayfaya dön
        backToHome();
        return;
    }
    
    // Gruba katılıyorsa, mevcut grup kodunu kullan
    if (app.currentMode === 'join_group') {
        app.groupId = app.groupCode;
    }
    
    saveToLocalStorage();
    loadRestaurants();
    showPage('restaurantPage');
}

// Grup Kodu Sayfası
// Renk İsimler
const colorNames = [
    'Kırmızı', 'Mavi', 'Yeşil', 'Sarı', 'Turuncu', 'Mor', 'Pembe',
    'Siyah', 'Beyaz', 'Gri', 'Kahverengi', 'Turkuaz', 'İndigo', 'Lila',
    'Kestane', 'Açık Mavi', 'Açık Yeşil', 'Açık Kırmızı', 'Koyu Mavi', 'Koyu Yeşil'
];

// Grup kodu sayfasından devam et
function continueFromGroupCode() {
    // Mevcut kullanıcının adını kullan
    if (app.currentUser) {
        app.currentUserName = `${app.currentUser.firstName} ${app.currentUser.lastName}`;
    } else {
        app.currentUserName = 'Kullanıcı';
    }
    app.cart[app.currentUserName] = [];
    
    // Gruba katılma/oluşturma işlemi tamamlandığında ana sayfaya dön
    backToHome();
}

// Grup Kodu Oluştur (Çiçek Adı + Numara)
function generateGroupId() {
    // Rastgele renk ismi seç
    const randomColor = colorNames[Math.floor(Math.random() * colorNames.length)];
    
    // 6 haneli numara üret (xxx-xxx formatında)
    const num1 = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const num2 = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const numericCode = `${num1}-${num2}`;
    
    return {
        name: randomColor,
        code: numericCode,
        fullCode: `${randomColor}-${numericCode}`
    };
}

// PAYLAŞMA SEÇENEKLERİ
function showShareOptions() {
    document.getElementById('shareModal').style.display = 'flex';
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
}

// Akıllı Paylaş: Giriş yapılmışsa WhatsApp'ta paylaş, yoksa giriş sayfasına yönlendir
function smartShareGroup() {
    const user = localStorage.getItem('hesapPaylas_user');
    
    if (user) {
        // Kullanıcı giriş yapmış, doğrudan WhatsApp'ta paylaş (URL ile)
        shareViaWhatsAppWithUrl();
    } else {
        // Kullanıcı giriş yapmamış, giriş sayfasına yönlendir
        showPage('onboardingPage');
    }
}

// URL parametresi ile WhatsApp paylaşımı
function shareViaWhatsAppWithUrl() {
    const appUrl = getAppURL() + '/?code=' + app.currentGroupCode;
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl:\n\n${appUrl}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
}

function shareViaWhatsApp() {
    // Uygulama URL'sine grup kodu parametresi ile beraber
    const appUrl = getAppURL() + '/?code=' + app.currentGroupCode;
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl:\n\n${appUrl}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
    closeShareModal();
}

function shareViaSMS() {
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl: ${app.currentGroupCode}`;
    window.location.href = `sms:?body=${encodeURIComponent(message)}`;
    closeShareModal();
}

function shareViaEmail() {
    const subject = `${app.currentGroupName} Grubuna Davet`;
    const body = `Merhaba!\n\n${app.currentGroupName} isimli gruba katılmaya davet ediyorum.\n\nGrup Kodu: ${app.currentGroupCode}`;
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    closeShareModal();
}

function copyGroupCode() {
    const text = `${app.currentGroupName}: ${app.currentGroupCode}`;
    navigator.clipboard.writeText(text).then(() => {
        alert('Grup kodu kopyalandı!');
        closeShareModal();
    }).catch(() => {
        alert('Kopyalama başarısız oldu');
    });
}

// ADIM 3: Restaurant Seçimi
function loadRestaurants() {
    // Örnek restaurant verileri (gerçekte API'den gelecek)
    const restaurants = {
        rest_001: {
            id: 'rest_001',
            name: 'Tarihi Kebapçı',
            phone: '0216-123-4567',
            categories: {
                'Kebaplar': [
                    { name: 'Adana Kebap', price: 45.00, emoji: '🌶️' },
                    { name: 'Urfa Kebap', price: 50.00, emoji: '🔥' },
                    { name: 'İskender Kebap', price: 55.00, emoji: '🍖' },
                    { name: 'Şiş Kebap', price: 60.00, emoji: '🍢' }
                ],
                'Mezeler': [
                    { name: 'Hummus', price: 15.00, emoji: '🥜' },
                    { name: 'Baba Ganoush', price: 15.00, emoji: '🍆' },
                    { name: 'Tzatziki', price: 12.00, emoji: '🥒' }
                ],
                'Salata': [
                    { name: 'Çoban Salatası', price: 20.00, emoji: '🥗' },
                    { name: 'Yeşil Salata', price: 15.00, emoji: '🥬' }
                ],
                'İçecekler': [
                    { name: 'Ayran', price: 8.00, emoji: '🥛' },
                    { name: 'Çay', price: 5.00, emoji: '🍵' },
                    { name: 'Kola', price: 10.00, emoji: '🥤' }
                ]
            }
        },
        rest_002: {
            id: 'rest_002',
            name: 'Şef Mutfağı - Modern Türk Evi',
            phone: '0212-555-6789',
            categories: {
                'Başlangıçlar': [
                    { name: 'Falafel', price: 25.00, emoji: '🔵' },
                    { name: 'Calamari Kızartması', price: 35.00, emoji: '🦑' }
                ],
                'Ana Yemekler': [
                    { name: 'Balık Pilaü', price: 75.00, emoji: '🐟' },
                    { name: 'Tavuk Şiş', price: 55.00, emoji: '🍗' },
                    { name: 'Biftek', price: 85.00, emoji: '🥩' }
                ],
                'Tatlılar': [
                    { name: 'Baklava', price: 20.00, emoji: '🍯' },
                    { name: 'Künefe', price: 25.00, emoji: '🧡' }
                ]
            }
        }
    };
    
    app.restaurants = restaurants;
    
    const restaurantList = document.getElementById('restaurantList');
    restaurantList.innerHTML = '';
    
    Object.values(restaurants).forEach(restaurant => {
        const card = document.createElement('div');
        card.className = 'restaurant-card';
        card.innerHTML = `
            <h3>🏪 ${restaurant.name}</h3>
            <p>📞 ${restaurant.phone}</p>
            <p>${Object.keys(restaurant.categories).length} Kategori</p>
        `;
        card.onclick = () => selectRestaurant(restaurant);
        restaurantList.appendChild(card);
    });
}

function selectRestaurant(restaurant) {
    app.currentRestaurant = restaurant;
    saveToLocalStorage();
    showMenuPage();
}

// ADIM 4: Menü Görüntüleme
function showMenuPage() {
    const restaurant = app.currentRestaurant;
    
    document.getElementById('restaurantName').innerText = restaurant.name;
    document.getElementById('restaurantPhone').innerText = restaurant.phone;
    
    // Kategorileri oluştur
    const categoryTabs = document.getElementById('categoryTabs');
    categoryTabs.innerHTML = '';
    
    const categories = Object.keys(restaurant.categories);
    categories.forEach((category, index) => {
        const tab = document.createElement('div');
        tab.className = `category-tab ${index === 0 ? 'active' : ''}`;
        tab.innerText = category;
        tab.onclick = () => showCategory(category);
        categoryTabs.appendChild(tab);
    });
    
    // İlk kategoriyi göster
    showCategory(categories[0]);
    showPage('menuPage');
}

function showCategory(categoryName) {
    const restaurant = app.currentRestaurant;
    const items = restaurant.categories[categoryName];
    const menuItems = document.getElementById('menuItems');
    
    menuItems.innerHTML = '';
    
    items.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'menu-item';
        itemCard.innerHTML = `
            <div class="menu-item-header">
                <span class="menu-item-emoji">${item.emoji}</span>
                <div>
                    <div class="menu-item-name">${item.name}</div>
                    <div class="menu-item-price">${item.price.toFixed(2)} ₺</div>
                </div>
            </div>
            <input type="number" class="quantity-input" id="qty-${item.name}" min="1" value="1" placeholder="Adet">
            <button class="add-button" onclick="addToCart('${item.name}', ${item.price}, '${item.emoji}')">Sepete Ekle</button>
        `;
        menuItems.appendChild(itemCard);
    });
    
    // Aktif kategoriyei güncelle
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.innerText === categoryName) {
            tab.classList.add('active');
        }
    });
}

// ADIM 5: Sepete Ürün Ekleme
function addToCart(itemName, price, emoji) {
    const quantityInput = document.getElementById(`qty-${itemName}`);
    const quantity = parseInt(quantityInput.value) || 1;
    
    if (quantity < 1) {
        alert('Geçersiz adet!');
        return;
    }
    
    if (!app.cart[app.currentUser]) {
        app.cart[app.currentUser] = [];
    }
    
    app.cart[app.currentUser].push({
        name: itemName,
        quantity: quantity,
        price: price,
        emoji: emoji,
        total: quantity * price
    });
    
    saveToLocalStorage();
    updateCartCount();
    
    // Geri sıfırla
    quantityInput.value = 1;
    alert(`${quantity} x ${itemName} sepete eklendi!`);
}

function updateCartCount() {
    let total = 0;
    if (app.cart[app.currentUser]) {
        total = app.cart[app.currentUser].length;
    }
    document.getElementById('cartCount').innerText = total;
}

// ADIM 6: Sipariş Listesi ve Hesap Bölme
function goToCart() {
    updateCartCount();
    displayOrders();
    showPage('cartPage');
}

function displayOrders() {
    const ordersList = document.getElementById('ordersList');
    const summaryItems = document.getElementById('summaryItems');
    
    ordersList.innerHTML = '';
    summaryItems.innerHTML = '';
    
    let grandTotal = 0;
    
    Object.keys(app.cart).forEach(personName => {
        const items = app.cart[personName];
        
        if (items.length === 0) return;
        
        let personTotal = 0;
        
        const personSection = document.createElement('div');
        personSection.className = 'person-orders';
        
        let itemsHTML = '';
        items.forEach((item, index) => {
            personTotal += item.total;
            itemsHTML += `
                <div class="order-item">
                    <div class="item-info">
                        <span>${item.emoji}</span>
                        <strong>${item.name}</strong>
                        <span>x${item.quantity}</span>
                    </div>
                    <div class="item-price">${item.total.toFixed(2)} ₺</div>
                    <button class="remove-btn" onclick="removeFromCart('${personName}', ${index})">Sil</button>
                </div>
            `;
        });
        
        personSection.innerHTML = `
            <div class="person-name">
                👤 ${personName}
                <span class="person-total">${personTotal.toFixed(2)} ₺</span>
            </div>
            ${itemsHTML}
        `;
        
        ordersList.appendChild(personSection);
        grandTotal += personTotal;
        
        // Summary'ye ekle
        const summaryItem = document.createElement('div');
        summaryItem.className = 'summary-item';
        summaryItem.innerHTML = `
            <span>👤 ${personName}</span>
            <strong>${personTotal.toFixed(2)} ₺</strong>
        `;
        summaryItems.appendChild(summaryItem);
    });
    
    // Genel Toplam
    document.getElementById('grandTotal').innerText = `${grandTotal.toFixed(2)} ₺`;
}

function removeFromCart(personName, index) {
    app.cart[personName].splice(index, 1);
    saveToLocalStorage();
    displayOrders();
}

function resetAll() {
    if (confirm('Tüm verileri silmek istediğinize emin misiniz?')) {
        app.cart = {};
        app.cart[app.currentUser] = [];
        saveToLocalStorage();
        showMenuPage();
    }
}

// ==================== GROUPS PAGE ====================

function showGroupsPage() {
    console.log('[MODAL] showGroupsPage called');
    
    const groupsModal = document.getElementById('groupsPage');
    console.log('[MODAL] groupsPage element found:', !!groupsModal);
    console.log('[MODAL] groupsPage element:', groupsModal);
    
    if (!groupsModal) {
        console.error('[MODAL] ERROR: groupsPage element not found in DOM!');
        alert('ERROR: Modal element not found in DOM');
        return;
    }
    
    const token = localStorage.getItem('hesapPaylas_token');
    console.log('[MODAL] Token found:', !!token);
    
    // DEBUG
    const debugModal = document.getElementById('debugModal');
    if (debugModal) debugModal.innerHTML = '<span class="status-ok">Modal: CLICKED</span>';
    
    if (!token) {
        console.log('[MODAL] No token found');
        alert('Lütfen önce giriş yapınız!');
        return;
    }
    
    // Modal'ı göster - force visible
    console.log('[MODAL] Before: display=' + groupsModal.style.display + ', visibility=' + groupsModal.style.visibility + ', opacity=' + groupsModal.style.opacity);
    
    groupsModal.style.setProperty('display', 'flex', 'important');
    groupsModal.style.setProperty('visibility', 'visible', 'important');
    groupsModal.style.setProperty('opacity', '1', 'important');
    groupsModal.style.setProperty('z-index', '99999', 'important');
    groupsModal.style.setProperty('position', 'fixed', 'important');
    groupsModal.style.setProperty('top', '0', 'important');
    groupsModal.style.setProperty('left', '0', 'important');
    groupsModal.style.setProperty('width', '100%', 'important');
    groupsModal.style.setProperty('height', '100%', 'important');
    
    console.log('[MODAL] After: display=' + groupsModal.style.display + ', visibility=' + groupsModal.style.visibility + ', opacity=' + groupsModal.style.opacity);
    console.log('[MODAL] Computed style display:', window.getComputedStyle(groupsModal).display);
    console.log('[MODAL] Computed style visibility:', window.getComputedStyle(groupsModal).visibility);
    
    console.log('[MODAL] Modal opened, now loading groups...');
    
    // Grupları yükle
    loadUserGroups();
}

function closeGroupsModal() {
    const groupsModal = document.getElementById('groupsPage');
    groupsModal.style.display = 'none';
}

function loadUserGroups() {
    const token = localStorage.getItem('hesapPaylas_token');
    const baseURL = getBaseURL();
    
    // Reset loading messages
    const activeList = document.getElementById('activeGroupsList');
    const closedList = document.getElementById('closedGroupsList');
    if (activeList) activeList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Yükleniyor...</p>';
    if (closedList) closedList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Yükleniyor...</p>';
    
    if (!token) {
        console.log('[GROUPS] No token found, showing test groups');
        setTimeout(() => showTestGroups(), 100);
        return;
    }
    
    console.log('[GROUPS] Fetching groups from:', baseURL + '/api/user/groups');
    
    // Backend'den gerçek grupları yükle
    fetch(`${baseURL}/api/user/groups`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        console.log('[GROUPS] Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('[GROUPS] API Response:', data);
        if (data && Array.isArray(data) && data.length > 0) {
            console.log('[GROUPS] Found', data.length, 'groups');
            console.log('[GROUPS] First group members:', data[0]?.members);
            displayGroups(data);
        } else if (data && Array.isArray(data)) {
            console.log('[GROUPS] No groups found, showing empty state');
            displayGroups([]);
        } else {
            console.error('[GROUPS] Invalid response format:', data);
            if (activeList) activeList.innerHTML = '<p style="color: #e74c3c; text-align: center; padding: 20px;">Hata: Geçersiz veri formatı</p>';
        }
    })
    .catch(error => {
        console.error('[GROUPS] Error loading groups:', error);
        console.log('[GROUPS] Falling back to test groups');
        showTestGroups();
    });
}

function showTestGroups() {
    // Test verisi - demo için
    const allGroups = [
        { id: 1, name: 'Öğle Yemeği Grubu', description: 'Pazartesi öğle yemeği', created_at: '2026-01-09', qr_code: '123456', status: 'active' },
        { id: 2, name: 'Akşam Yemeği', description: 'Cuma akşamı', created_at: '2026-01-08', qr_code: '789012', status: 'active' },
        { id: 3, name: 'Geçen Hafta Grubu', description: 'Tamamlandı', created_at: '2026-01-01', qr_code: '345678', status: 'closed' }
    ];
    displayGroups(allGroups);
}

function displayGroups(groups) {
    console.log('[DISPLAY-MODAL] displayGroups called - MODAL GROUPS ONLY (not floating panel)');
    console.log('[DISPLAY-MODAL] Number of groups:', groups ? groups.length : 'null');
    
    const activeGroups = groups.filter(g => g.status === 'active');
    const closedGroups = groups.filter(g => g.status === 'closed');
    
    console.log('[DISPLAY-MODAL] Filtered - Active:', activeGroups.length, 'Closed:', closedGroups.length);
    
    // SADECE modal'daki activeGroupsList'e yaz - Floating panel'e ASLA yazma!
    const activeList = document.getElementById('activeGroupsList');
    console.log('[DISPLAY-MODAL] activeList element found:', !!activeList);
    
    if (!activeList) {
        console.error('[DISPLAY-MODAL] ERROR: activeGroupsList element not found - displayGroups will not update anything');
        return;
    }
    
    if (activeGroups.length > 0) {
        console.log('[DISPLAY-MODAL] Rendering', activeGroups.length, 'active groups in MODAL...');
        try {
            const html = activeGroups.map((group, index) => {
                console.log('[DISPLAY-MODAL] Rendering modal group', index + 1, ':', group.name, 'Status:', group.status);
                const memberCount = (group.members || []).length;
                const groupName = group.name || 'İsimsiz Grup';
                const groupDesc = group.description || 'Açıklama yok';
                const groupCode = formatQRCode(group.qr_code);
                
                // Tek satırda gösterim: "Mor (3 kişi) Divan'da akşam yemeği (Grup kodu:123-456)"
                const displayText = `${groupName} (${memberCount} kişi) ${groupDesc} (Grup kodu:${groupCode})`;
                
                return `
            <div class="group-card-modal" data-group-id="${group.id}" data-group-name="${groupName.replace(/"/g, '&quot;')}" data-group-desc="${groupDesc.replace(/"/g, '&quot;')}" data-group-date="${group.created_at}" data-group-qr="${group.qr_code}" style="padding: 12px; background: #e3f2fd; border-left: 4px solid #1a237e; border-radius: 8px; cursor: pointer; transition: all 0.3s;">
                <div style="font-weight: 600; color: #1a237e; cursor: pointer; user-select: none; word-break: break-word; line-height: 1.4;">${displayText}</div>
            </div>
        `;
            }).join('');
            console.log('[DISPLAY-MODAL] HTML generated for modal, length:', html.length);
            activeList.innerHTML = html;
            
            // Event listener ekle - tüm grup kartlarına
            document.querySelectorAll('.group-card-modal').forEach(card => {
                card.addEventListener('click', function() {
                    const groupId = this.dataset.groupId;
                    const groupName = this.dataset.groupName;
                    const groupDesc = this.dataset.groupDesc;
                    const groupDate = this.dataset.groupDate;
                    const groupQr = this.dataset.groupQr;
                    console.log('[DISPLAY-MODAL] Group card clicked:', groupId, groupName);
                    showGroupDetails(groupId, groupName, groupDesc, groupDate, groupQr);
                });
            });
            
            console.log('[DISPLAY-MODAL] HTML set to activeGroupsList (modal) successfully');
        } catch (err) {
            console.error('[DISPLAY-MODAL] Error rendering modal groups:', err);
            activeList.innerHTML = '<p style="color: #e74c3c; text-align: center; padding: 20px;">Hata: ' + err.message + '</p>';
        }
    } else {
        console.log('[DISPLAY-MODAL] No active groups - showing empty message in MODAL');
        activeList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Henüz aktif grup yok</p>';
    }
    
    // Kapanmış grupları göster
    const closedList = document.getElementById('closedGroupsList');
    if (closedGroups.length > 0) {
        const closedHtml = closedGroups.map(group => {
            const memberCount = (group.members || []).length;
            const groupName = group.name || 'İsimsiz Grup';
            const groupDesc = group.description || 'Açıklama yok';
            const groupCode = formatQRCode(group.qr_code);
            
            // Tek satırda gösterim: "Mor (3 kişi) Divan'da akşam yemeği (Grup kodu:123-456)"
            const displayText = `${groupName} (${memberCount} kişi) ${groupDesc} (Grup kodu:${groupCode})`;
            
            return `
            <div class="group-card-modal" data-group-id="${group.id}" data-group-name="${groupName.replace(/"/g, '&quot;')}" data-group-desc="${groupDesc.replace(/"/g, '&quot;')}" data-group-date="${group.created_at}" data-group-qr="${group.qr_code}" style="padding: 12px; background: #f5f5f5; border-left: 4px solid #9E9E9E; border-radius: 8px; cursor: pointer; opacity: 0.8; transition: all 0.3s;">
                <div style="font-weight: 600; color: #757575; cursor: pointer; user-select: none; word-break: break-word; line-height: 1.4;">${displayText}</div>
            </div>
        `}).join('');
        closedList.innerHTML = closedHtml;
        
        // Event listener ekle - kapalı gruplar için de
        closedList.querySelectorAll('.group-card-modal').forEach(card => {
            card.addEventListener('click', function() {
                const groupId = this.dataset.groupId;
                const groupName = this.dataset.groupName;
                const groupDesc = this.dataset.groupDesc;
                const groupDate = this.dataset.groupDate;
                const groupQr = this.dataset.groupQr;
                showGroupDetails(groupId, groupName, groupDesc, groupDate, groupQr);
            });
        });
    } else {
        closedList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Kapalı grup yok</p>';
    }
}

function showGroupDetails(groupId, groupName, groupDesc, groupDate, qrCode) {
    console.log('[GROUP-DETAILS] showGroupDetails called with groupId:', groupId, 'groupName:', groupName);
    const detailsModal = document.getElementById('groupDetailsModal');
    const groupsPage = document.getElementById('groupsPage');
    
    console.log('[GROUP-DETAILS] detailsModal found:', !!detailsModal, 'groupsPage found:', !!groupsPage);
    
    // groupsPage'i tamamen gizle - display none
    if (groupsPage) {
        console.log('[GROUP-DETAILS] Hiding groupsPage modal completely');
        groupsPage.style.display = 'none';
        groupsPage.style.visibility = 'hidden';
        groupsPage.style.pointerEvents = 'none';
    }
    
    // Modal'ı ön plana çık - hemen ve kalıcı olarak görünür hale getir
    detailsModal.style.setProperty('z-index', '99999', 'important');
    detailsModal.style.visibility = 'visible';
    detailsModal.style.opacity = '1';
    detailsModal.style.display = 'flex';
    detailsModal.style.pointerEvents = 'auto';
    detailsModal.classList.remove('modal-close');
    detailsModal.classList.add('modal-open');
    console.log('[GROUP-DETAILS] groupDetailsModal shown with z-index 99999');
    
    // Backend'den detaylı grup bilgisini çek
    const token = localStorage.getItem('hesapPaylas_token');
    console.log('[GROUP-DETAILS] Fetching group details from:', `${API_BASE_URL}/groups/${groupId}`);
    console.log('[GROUP-DETAILS] Token:', token ? 'present' : 'MISSING');
    
    fetch(`${API_BASE_URL}/groups/${groupId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(r => {
        console.log('[GROUP-DETAILS] Fetch response status:', r.status);
        return r.json();
    })
    .then(group => {
        console.log('[GROUP-DETAILS] Fetch successful, group data:', group);
        // Grup adını doğru göster
        document.getElementById('detailGroupName').textContent = group.name || groupName || 'İsimsiz Grup';
        // Grup kodunu göster (code_formatted varsa formatlanmış hali, yoksa raw code)
        document.getElementById('detailGroupCode').textContent = group.code_formatted || group.code || '---';
        document.getElementById('detailGroupCategory').textContent = group.category || 'Genel Yaşam';
        document.getElementById('detailGroupDate').textContent = new Date(group.created_at).toLocaleDateString('tr-TR');
        
        // Üye sayısını parantez içinde göster
        const memberCount = (group.members || []).length;
        document.getElementById('detailGroupMemberCount').textContent = `(${memberCount} üye)`;
        
        // Üyeleri isim olarak inline göster - aynı isim varsa M. Güven formatı yap
        const members = group.members || [];
        const creator = group.creator;
        
        // Grubu kuran kişi + tüm üyeler
        let allPeople = [];
        if (creator) {
            allPeople.push({ ...creator, isCreator: true });
        }
        // Grubu kuran kişi zaten üyeler arasında varsa tekrar ekleme
        members.forEach(m => {
            if (!creator || m.id !== creator.id) {
                allPeople.push({ ...m, isCreator: false });
            }
        });
        
        if (allPeople.length > 0) {
            // Aynı adlara sahip kişileri bul
            const nameCount = {};
            allPeople.forEach(p => {
                const firstName = (p.first_name || p.firstName || '');
                nameCount[firstName] = (nameCount[firstName] || 0) + 1;
            });
            
            const memberNamesHtml = allPeople.map(p => {
                const firstName = (p.first_name || p.firstName || '');
                const lastName = (p.last_name || p.lastName || '');
                // Aynı addan birden fazla varsa baş harfi göster
                const displayName = nameCount[firstName] > 1 ? `${firstName.charAt(0)}. ${lastName}` : firstName;
                const crownIcon = p.isCreator ? '👑 ' : '';
                return `<span class="member-name-tag" onclick="showUserAccountDetails('${p.id}')" style="padding: 4px 8px; background: ${p.isCreator ? '#fff3cd' : '#e3f2fd'}; border: 1px solid ${p.isCreator ? '#ffc107' : '#90CAF9'}; border-radius: 12px; font-size: 0.85em; color: ${p.isCreator ? '#856404' : '#1976D2'}; cursor: pointer; font-weight: 500; user-select: none;" title="${firstName} ${lastName}${p.isCreator ? ' (Kuran)' : ''}">${crownIcon}${displayName}</span>`;
            }).join('');
            document.getElementById('detailGroupMemberNames').innerHTML = memberNamesHtml;
        } else {
            document.getElementById('detailGroupMemberNames').innerHTML = '<span style="color: #999; font-size: 0.85em;">Üye yok</span>';
        }
        
        // Siparişleri/Hesap Özeti göster
        if (group.orders && group.orders.length > 0) {
            const ordersList = group.orders.map(order => `
                <div style="padding: 10px; background: white; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #3498db;">
                    <div style="font-weight: 600; color: #333; margin-bottom: 4px; font-size: 0.9em;">🍽️ ${order.restaurant}</div>
                    <div style="font-size: 0.85em; color: #666; margin-bottom: 3px;">Tarih: ${new Date(order.created_at).toLocaleDateString('tr-TR')}</div>
                    <div style="font-size: 0.85em; color: #27ae60; font-weight: 600;">₺${order.total_amount.toFixed(2)}</div>
                </div>
            `).join('');
            document.getElementById('detailGroupOrders').innerHTML = ordersList;
        } else {
            document.getElementById('detailGroupOrders').innerHTML = '';
        }
        
        // Ödeme dengesi (orders total)
        const totalBalance = group.orders ? group.orders.reduce((sum, order) => sum + order.total_amount, 0) : 0;
        document.getElementById('detailGroupBalance').textContent = `₺${totalBalance.toFixed(2)}`;
        
        // Üyeleri global'e sakla (detay açılması için)
        window.currentGroupMembers = group.members || [];
        
        // Modal'ı aç animasyon ile
        detailsModal.classList.remove('modal-close');
        detailsModal.classList.add('modal-open');
        detailsModal.style.display = 'flex';
    })
    .catch(error => {
        console.error('[GROUP-DETAILS] ERROR loading group details:', error);
        console.error('[GROUP-DETAILS] Error message:', error.message);
        console.error('[GROUP-DETAILS] Error stack:', error.stack);
        // Fallback: sadece basit bilgileri göster
        document.getElementById('detailGroupName').textContent = groupName || 'İsimsiz Grup';
        document.getElementById('detailGroupCode').textContent = '---';
        document.getElementById('detailGroupDate').textContent = new Date(groupDate).toLocaleDateString('tr-TR');
        document.getElementById('detailGroupMemberCount').textContent = '(0 üye)';
        
        // Modal'ı aç animasyon ile
        detailsModal.classList.remove('modal-close');
        detailsModal.classList.add('modal-open');
        detailsModal.style.display = 'flex';
    });
    
    window.currentGroupId = groupId;
}

// Hesap Özeti detaylarını aç/kapat
function toggleOrderDetails() {
    const detailsBox = document.getElementById('detailGroupOrders');
    const h3 = document.querySelector('#groupDetailsModal h3');
    
    if (detailsBox.style.display === 'none') {
        detailsBox.style.display = 'block';
        if (h3) h3.textContent = '📋 Hesap Özeti ▲';
    } else {
        detailsBox.style.display = 'none';
        if (h3) h3.textContent = '📋 Hesap Özeti ▼';
    }
}

// Kullanıcı hesap detaylarını göster
function showUserAccountDetails(userId) {
    console.log('[MEMBER-DETAILS] Showing details for user:', userId);
    // TODO: Kullanıcı hesap detayları modalı açılacak
    alert(`Kullanıcı ${userId} için hesap detayları açılacak (çok yakında!)`);
}

// Grup hesabını kapat
function closeGroupAccount() {
    const groupId = window.currentGroupId;
    if (!groupId) return;
    
    const confirmed = confirm('Grup hesabını kapatmak istediğinizden emin misiniz?\nGrup kapatıldığında tüm veriler korunacak.');
    if (!confirmed) return;
    
    const token = localStorage.getItem('hesapPaylas_token');
    fetch(`${API_BASE_URL}/groups/${groupId}/close`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(r => r.json())
    .then(data => {
        alert('✅ Grup başarıyla kapatıldı');
        closeGroupDetailsModal();
        loadUserGroups();
    })
    .catch(error => {
        alert('❌ Hata: ' + error.message);
    });
}

// Grup hesabını sil
function deleteGroupAccount() {
    const groupId = window.currentGroupId;
    if (!groupId) return;
    
    const confirmed = confirm('⚠️ DİKKAT! Grup hesabını SİLMEK istediğinizden emin misiniz?\nBu işlem GERİ ALINMAZ!\n\nGrup ve tüm verileriniz kalıcı olarak silinecektir.');
    if (!confirmed) return;
    
    const password = prompt('Şifrenizi girin (onay için):');
    if (!password) return;
    
    const token = localStorage.getItem('hesapPaylas_token');
    fetch(`${API_BASE_URL}/groups/${groupId}/delete`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert('❌ Hata: ' + data.error);
        } else {
            alert('🗑️ Grup kalıcı olarak silinmiştir');
            closeGroupDetailsModal();
            loadUserGroups();
        }
    })
    .catch(error => {
        alert('❌ Hata: ' + error.message);
    });
}

// QR Kod'u xxx-xxx formatında göster
function formatQRCode(code) {
    if (!code) return '---';
    const cleanCode = code.toString().replace(/\D/g, '').slice(0, 6);
    return cleanCode.length === 6 ? cleanCode.slice(0, 3) + '-' + cleanCode.slice(3) : cleanCode;
}

// QR Kod input maskesi (0532 333 22 22 formatında)
function formatQRCodeInput(value) {
    const cleaned = value.replace(/\D/g, '').slice(0, 6);
    if (cleaned.length <= 3) return cleaned;
    return cleaned.slice(0, 3) + '-' + cleaned.slice(3);
}

// QR Kod input handler
function handleQRCodeInput(input) {
    input.value = formatQRCodeInput(input.value);
}

function closeGroupDetailsModal() {
    const detailsModal = document.getElementById('groupDetailsModal');
    const groupsPage = document.getElementById('groupsPage');
    
    console.log('[GROUP-DETAILS-CLOSE] Closing group details modal');
    
    // Fade-out animasyonu
    detailsModal.classList.add('modal-close');
    detailsModal.classList.remove('modal-open');
    
    // Animasyon bitince kapat - 300ms (CSS animation duration)
    setTimeout(() => {
        detailsModal.style.visibility = 'hidden';
        detailsModal.style.display = 'none';
        detailsModal.style.opacity = '0';
        detailsModal.style.pointerEvents = 'none';
        
        // groupsPage'i geri göster - eğer orada idik, geri dön
        if (groupsPage) {
            console.log('[GROUP-DETAILS-CLOSE] Restoring groupsPage modal');
            groupsPage.style.display = 'flex';
            groupsPage.style.visibility = 'visible';
            groupsPage.style.pointerEvents = 'auto';
            groupsPage.style.setProperty('z-index', '99999', 'important');
        }
    }, 300);
}


function editGroup() {
    const newName = prompt('Yeni grup adı girin:');
    if (!newName) return;
    
    alert('✅ Grup güncellendi: ' + newName);
    closeGroupDetailsModal();
    loadUserGroups();
}

// ==================== QR Kod Okuyucu Fonksiyonları ====================

let html5QrcodeScanner = null;

function openJoinGroupModal() {
    document.getElementById('joinGroupModal').style.display = 'flex';
    document.getElementById('qr-reader-results').textContent = '';
    document.getElementById('groupCodeInput').value = '';
    document.getElementById('joinGroupMessage').textContent = '';
}

function closeJoinGroupModal() {
    document.getElementById('joinGroupModal').style.display = 'none';
    stopQRScanner();
}

function switchJoinTab(tab) {
    // Sekmeleri göster/gizle
    document.getElementById('scanTab').style.display = tab === 'scan' ? 'block' : 'none';
    document.getElementById('manualTab').style.display = tab === 'manual' ? 'block' : 'none';
    
    // Buton stillerini güncelle
    document.querySelectorAll('.join-tab-btn').forEach(btn => {
        btn.style.color = btn.textContent.includes(tab === 'scan' ? '📱' : '✏️') ? '#333' : '#999';
        btn.style.borderBottomColor = btn.textContent.includes(tab === 'scan' ? '📱' : '✏️') ? '#4A90E2' : 'transparent';
    });
    
    // Kamerayı kapat eğer manuel sekmeye geçiyorsa
    if (tab === 'manual') {
        stopQRScanner();
    }
}

function startQRScanner() {
    const startBtn = document.getElementById('startScanBtn');
    const stopBtn = document.getElementById('stopScanBtn');
    
    startBtn.style.display = 'none';
    stopBtn.style.display = 'block';
    
    html5QrcodeScanner = new Html5Qrcode("qr-reader");
    
    // Kamera izni iste
    const qrCodeSuccessCallback = (decodedText, decodedResult) => {
        onQRCodeScanned(decodedText);
    };
    
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        rememberLastUsedCamera: true,
        supportedScanTypes: ['IMAGE', 'CAMERA']
    };
    
    html5QrcodeScanner.start(
        { facingMode: "environment" },
        config,
        qrCodeSuccessCallback,
        (errorMessage) => {
            // Hata yapma, sessiz tut
        }
    ).catch(err => {
        console.error('Kamera açılamadı:', err);
        document.getElementById('qr-reader-results').textContent = '❌ Kamera izni gerekli';
        document.getElementById('qr-reader-results').style.color = '#e74c3c';
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
    });
}

function stopQRScanner() {
    if (html5QrcodeScanner) {
        html5QrcodeScanner.stop().catch(err => console.error('Kamera kapatılamadı:', err));
        html5QrcodeScanner = null;
    }
    
    const startBtn = document.getElementById('startScanBtn');
    const stopBtn = document.getElementById('stopScanBtn');
    
    startBtn.style.display = 'block';
    stopBtn.style.display = 'none';
}

function onQRCodeScanned(decodedText) {
    // Kodu temizle (sadece rakamları al)
    const cleanCode = decodedText.replace(/[^\d]/g, '');
    
    if (cleanCode.length === 6) {
        // Kodu xxx-xxx formatına çevir
        const formattedCode = cleanCode.slice(0, 3) + '-' + cleanCode.slice(3);
        
        // Sonucu göster
        document.getElementById('qr-reader-results').textContent = `✅ Kod okundu: ${formattedCode}`;
        document.getElementById('qr-reader-results').style.color = '#27ae60';
        
        // Kamerayı kapat
        stopQRScanner();
        
        // 1.5 saniye sonra gruba katıl
        setTimeout(() => {
            joinGroupWithCode(cleanCode);
        }, 1500);
    } else {
        document.getElementById('qr-reader-results').textContent = '⚠️ Geçersiz QR kod';
        document.getElementById('qr-reader-results').style.color = '#f39c12';
    }
}

function handleManualCodeInput(input) {
    // Sadece rakamları kabul et
    let value = input.value.replace(/[^\d]/g, '');
    
    // Maksimum 6 rakam
    if (value.length > 6) {
        value = value.slice(0, 6);
    }
    
    // xxx-xxx formatına çevir
    if (value.length > 3) {
        input.value = value.slice(0, 3) + '-' + value.slice(3);
    } else {
        input.value = value;
    }
}

function joinGroupWithManualCode() {
    const code = document.getElementById('groupCodeInput').value;
    const cleanCode = code.replace(/[^\d]/g, '');
    
    if (cleanCode.length !== 6) {
        document.getElementById('joinGroupMessage').textContent = '❌ Lütfen 6 haneli bir kod gir';
        document.getElementById('joinGroupMessage').style.color = '#e74c3c';
        return;
    }
    
    joinGroupWithCode(cleanCode);
}

function joinGroupWithCode(code) {
    const token = localStorage.getItem('hesapPaylas_token');
    const baseURL = getBaseURL();
    
    if (!token) {
        alert('❌ Lütfen önce giriş yap');
        closeJoinGroupModal();
        return;
    }
    
    document.getElementById('joinGroupMessage').textContent = '⏳ Gruba katılınıyor...';
    document.getElementById('joinGroupMessage').style.color = '#3498db';
    
    fetch(`${baseURL}/api/groups/join`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            qr_code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || data.id) {
            document.getElementById('joinGroupMessage').textContent = '✅ Gruba başarıyla katıldınız!';
            document.getElementById('joinGroupMessage').style.color = '#27ae60';
            
            setTimeout(() => {
                closeJoinGroupModal();
                loadUserGroups(); // Grupları yenile
            }, 1500);
        } else {
            document.getElementById('joinGroupMessage').textContent = `❌ ${data.message || 'Grup bulunamadı'}`;
            document.getElementById('joinGroupMessage').style.color = '#e74c3c';
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        document.getElementById('joinGroupMessage').textContent = '❌ Bir hata oluştu. Tekrar deneyin.';
        document.getElementById('joinGroupMessage').style.color = '#e74c3c';
    });
}

// ===== YENİ GRUP OLUŞTURMA FONKSİYONLARI =====

function showCreateGroupForm() {
    // Input'ları temizle
    document.getElementById('newGroupName').value = '';
    document.getElementById('newGroupDesc').value = '';
    document.getElementById('createGroupMessage').textContent = '';
    
    // Modal'ı göster
    const modal = document.getElementById('createGroupModal');
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
}

// Rastgele renk listesi
const COLOR_LIST = [
    { name: 'Kırmızı', code: '#FF0000' },
    { name: 'Mavi', code: '#0066FF' },
    { name: 'Yeşil', code: '#00AA00' },
    { name: 'Sarı', code: '#FFD700' },
    { name: 'Mor', code: '#9933FF' },
    { name: 'Turuncu', code: '#FF8800' },
    { name: 'Pembe', code: '#FF69B4' },
    { name: 'Cyan', code: '#00FFFF' },
    { name: 'Kahverengi', code: '#8B4513' },
    { name: 'Gri', code: '#808080' }
];

// Seçili rengi sakla
let selectedColor = null;

function getRandomColor() {
    return COLOR_LIST[Math.floor(Math.random() * COLOR_LIST.length)];
}

function selectCategory(category) {
    // Kategori butonlarının stilini sıfırla
    const buttons = ['cat-cafe', 'cat-life', 'cat-travel'];
    buttons.forEach(btn => {
        const element = document.getElementById(btn);
        if (btn === 'cat-cafe') {
            element.style.border = '2px solid #ddd';
            element.style.background = '#FFE8B6';
        } else if (btn === 'cat-life') {
            element.style.border = '2px solid #66BB6A';
            element.style.background = '#C8E6C9';
        } else if (btn === 'cat-travel') {
            element.style.border = '2px solid #ddd';
            element.style.background = '#B3E5FC';
        }
    });
    
    // Seçili kategori butonunu vurgula
    let selectedBtn;
    if (category === 'Cafe / Restaurant') {
        selectedBtn = 'cat-cafe';
    } else if (category === 'Genel Yaşam') {
        selectedBtn = 'cat-life';
    } else if (category === 'Seyahat / Konaklama') {
        selectedBtn = 'cat-travel';
    }
    
    if (selectedBtn) {
        const element = document.getElementById(selectedBtn);
        element.style.border = '3px solid #333';
    }
    
    // Hidden input'u güncelle
    document.getElementById('newGroupCategory').value = category;
    
    // Show description section
    document.getElementById('descriptionSection').style.display = 'block';
}

function openCreateGroupModal() {
    // Rastgele renk seç
    const randomColor = getRandomColor();
    selectedColor = randomColor;  // Global variable'a sakla
    
    const modal = document.getElementById('createGroupModal');
    
    // Modal'ı data-attribute'a da sakla (closure problem'ini önle)
    modal.setAttribute('data-group-color-name', randomColor.name);
    modal.setAttribute('data-group-color-code', randomColor.code);
    
    // Başlığı ayarla
    document.getElementById('modalTitle').textContent = 'Kategori Seç';
    
    // Grup Adı bölümünü GIZLE (henüz grup kurulmadı)
    document.getElementById('groupNameSection').style.display = 'none';
    
    // Success section'ı gizle
    document.getElementById('groupSuccessSection').style.display = 'none';
    
    // Kategori bölümünü göster
    document.getElementById('categorySection').style.display = 'block';
    
    // Kategoriyi sıfırla (Genel Yaşam seçili)
    document.getElementById('newGroupCategory').value = 'Genel Yaşam';
    selectCategory('Genel Yaşam');
    
    // Grubu Kur butonunu göster
    document.getElementById('createGroupBtn').style.display = 'block';
    
    document.getElementById('createGroupMessage').textContent = '';
    
    // Show modal
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
}

function closeCreateGroupModal() {
    // Modal'ı gizle
    document.getElementById('createGroupModal').style.display = 'none';
    
    // Success section'ı gizle
    document.getElementById('groupSuccessSection').style.display = 'none';
    
    // Kategori bölümünü gizle
    document.getElementById('categorySection').style.display = 'none';
    
    // Description bölümünü gizle
    document.getElementById('descriptionSection').style.display = 'none';
    
    // Description alanını temizle
    document.getElementById('newGroupDescription').value = '';
    
    // Grubu Kur butonunu gizle
    document.getElementById('createGroupBtn').style.display = 'none';
    
    document.getElementById('createGroupMessage').textContent = '';
}

function createNewGroup() {
    const groupCategory = document.getElementById('newGroupCategory').value;
    const messageDiv = document.getElementById('createGroupMessage');
    const modal = document.getElementById('createGroupModal');
    
    // Validasyon - Kategori seçilmiş mi?
    if (!groupCategory) {
        messageDiv.textContent = '❌ Lütfen bir kategori seç';
        messageDiv.style.color = '#e74c3c';
        return;
    }
    
    // Data-attribute'tan renk adını oku (global variable yerine - race condition'ı önle)
    let groupName = modal.getAttribute('data-group-color-name');
    if (!groupName) {
        groupName = selectedColor ? selectedColor.name : 'Grup';  // Fallback
    }
    const groupDescription = document.getElementById('newGroupDescription').value.trim();
    
    const baseURL = getBaseURL();
    const token = localStorage.getItem('hesapPaylas_token');
    
    messageDiv.textContent = '⏳ Grup oluşturuluyor...';
    messageDiv.style.color = '#f39c12';
    
    fetch(`${baseURL}/api/groups`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            name: groupName,
            description: groupDescription || null,
            category: groupCategory
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const newGroup = data.group;
            
            // Success ekranını göster
            showGroupSuccessScreen(
                selectedColor.name,  // Seçili renk adı (grup adı)
                selectedColor.name,  // Seçili renk adı
                selectedColor.code,  // Seçili renk kodu
                newGroup.code,  // Grup kodu (raw 6-digit: 123456)
                newGroup.code_formatted  // Formatted code (123-456)
            );
            
            messageDiv.textContent = '';
            
            // Kategori bölümünü gizle
            document.getElementById('categorySection').style.display = 'none';
            
            // Grubu Kur butonunu gizle
            document.getElementById('createGroupBtn').style.display = 'none';
        } else {
            messageDiv.textContent = `❌ ${data.message || 'Grup oluşturulamadı'}`;
            messageDiv.style.color = '#e74c3c';
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        messageDiv.textContent = '❌ Bir hata oluştu. Tekrar deneyin.';
        messageDiv.style.color = '#e74c3c';
    });
}

// Grup oluşturma başarılı - success ekranını göster
function showGroupSuccessScreen(groupName, colorName, colorCode, rawCode, formattedCode) {
    // Başlığı "Grup Kur" olarak değiştir
    document.getElementById('modalTitle').textContent = 'Grup Kur';
    
    // Success section'ı göster
    document.getElementById('groupSuccessSection').style.display = 'block';
    
    // Renk paletini göster
    document.getElementById('successColorSection').style.display = 'block';
    
    // Renk kutusunu ve adını güncelle
    document.getElementById('successColorBox').style.backgroundColor = colorCode;
    document.getElementById('successColorName').textContent = colorName;
    document.getElementById('successColorCode').textContent = colorCode;
    
    // QR kodu göster (QR Server API kullanarak)
    // rawCode kullan: "123456" (without formatting)
    const qrCodeContainer = document.getElementById('successQRCode');
    qrCodeContainer.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${rawCode}&color=000000" alt="QR Code" style="border: 2px solid #000;">`;
    
    // Grup kodunu göster (formatted: "123-456")
    document.getElementById('successGroupCode').textContent = formattedCode;
    
    // Katılım linkini oluştur ve göster (dynamic URL kullan)
    const baseURL = getAppURL();
    const participationLink = `${baseURL}?code=${formattedCode}`;
    const linkElement = document.getElementById('successParticipationLink');
    linkElement.textContent = participationLink;
    linkElement.href = participationLink;
    
    // WhatsApp share button'ında formatted grup kodunu sakla
    document.getElementById('whatsappShareBtn').setAttribute('data-group-code', formattedCode);
    
    // Aktif grupları yenile ve floating button'ı göster
    loadActiveGroups();
}

// WhatsApp'ta paylaş
function shareGroupOnWhatsapp() {
    const groupCode = document.getElementById('whatsappShareBtn').getAttribute('data-group-code');
    const participationLink = document.getElementById('successParticipationLink').textContent;
    const message = `Grup Kodu: ${groupCode}\n\nKatılmak için: ${participationLink}`;
    const encodedMessage = encodeURIComponent(message);
    
    // WhatsApp Web veya mobil app'ı aç
    window.open(`https://wa.me/?text=${encodedMessage}`, '_blank');
}

// Katılım linkini kopyala
function copyParticipationLink() {
    const linkText = document.getElementById('successParticipationLink').textContent;
    navigator.clipboard.writeText(linkText).then(() => {
        showNotification('✅ Link kopyalandı!', 'success');
    }).catch(err => {
        showNotification('❌ Kopyalanamadı', 'error');
    });
}

// Aktif Grupları Yönetme
function toggleActiveGroupPanel() {
    const panel = document.getElementById('activeGroupPanel');
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'block';
        loadActiveGroups();
    } else {
        panel.style.display = 'none';
    }
}

function loadActiveGroups() {
    console.log('✅ loadActiveGroups çağrıldı');
    const token = localStorage.getItem('hesapPaylas_token');
    if (!token) return;
    
    const baseURL = getBaseURL();
    fetch(`${baseURL}/api/user/groups`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(groups => {
        const listContainer = document.getElementById('activeGroupsFloatingList');
        const activeGroupButton = document.getElementById('activeGroupButton');
        
        listContainer.innerHTML = '';
        
        if (groups.length === 0) {
            // Grup yok - floating button'ı gizle
            if (activeGroupButton) {
                activeGroupButton.style.display = 'none';
            }
            listContainer.innerHTML = '<p style="color: #999; text-align: center; padding: 20px 0;">Henüz gruba katılmadınız</p>';
        } else {
            // Grup var - floating button'ı göster
            if (activeGroupButton) {
                activeGroupButton.style.display = 'block';
            }
            
            groups.forEach(group => {
                const groupItem = document.createElement('div');
                
                groupItem.style.cssText = `
                    padding: 12px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    border-left: 4px solid #00BCD4;
                    cursor: pointer;
                    transition: all 0.2s ease;
                `;
                groupItem.onmouseover = () => groupItem.style.background = '#f0f0f0';
                groupItem.onmouseout = () => groupItem.style.background = '#f9f9f9';
                groupItem.onclick = () => {
                    console.log('Grup seçildi:', group.id, group.name);
                    selectActiveGroup(group.id, group.name);
                };
                
                const groupName = group.name || 'İsimsiz Grup';
                const memberCount = group.members_count || 0;
                const description = group.description || group.category || 'Genel Yaşam';
                
                // Format: "Sarı (1 kişi) Big Chef'te öğle yemeği" - tek satırda
                let displayText = `${groupName} (${memberCount} kişi) ${description}`;
                
                groupItem.innerHTML = `<div style="font-weight: 600; color: #333; word-break: break-word; line-height: 1.4;">${displayText}</div>`;
                listContainer.appendChild(groupItem);
            });
        }
    })
    .catch(error => {
        console.error('Gruplar yüklenemedi:', error);
        // Hata durumunda floating button'ı gizle
        const activeGroupButton = document.getElementById('activeGroupButton');
        if (activeGroupButton) {
            activeGroupButton.style.display = 'none';
        }
    });
}

function selectActiveGroup(groupId, groupName) {
    console.log('selectActiveGroup çağrıldı:', groupId, groupName);
    
    // Aktif gruplar panelini kapat
    const panel = document.getElementById('activeGroupPanel');
    if (panel) {
        panel.style.display = 'none';
        console.log('activeGroupPanel kapatıldı');
    }
    
    // Gruplarım modal'ını kapat
    const groupsModal = document.getElementById('groupsPage');
    if (groupsModal) {
        groupsModal.style.display = 'none';
        console.log('groupsPage kapatıldı');
    }
    
    // Biraz bekle ve sonra detayları göster
    setTimeout(() => {
        console.log('Timeout sonrası showGroupMembersModal çağrılıyor');
        showGroupMembersModal(groupId);
    }, 100);
}

function showGroupMembersModal(groupId) {
    console.log('showGroupMembersModal çağrıldı:', groupId);
    
    const modal = document.getElementById('gruphızlıerişim');
    const membersList = document.getElementById('membersList');
    const memberModalTitle = document.getElementById('memberModalTitle');
    
    // Modal'ı aç
    modal.style.display = 'flex';
    
    // Token al
    const token = localStorage.getItem('hesapPaylas_token');
    if (!token) {
        membersList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Lütfen giriş yapınız</p>';
        return;
    }
    
    // Grup verilerini API'den getir
    const baseURL = getBaseURL();
    
    fetch(`${baseURL}/api/groups/${groupId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(group => {
        // Modal'ı aç
        modal.style.display = 'flex';
        
        // Başlık: "Hızlı İşlemler"
        memberModalTitle.textContent = 'Hızlı İşlemler';
        membersList.innerHTML = '';
        
        // Grup adı ve açıklaması tek satırda - MASK: Grup adı maskelenmiş gösterilir
        const groupInfoSection = document.createElement('div');
        groupInfoSection.style.cssText = `
            background: #f0f8ff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
            border-left: 4px solid #2196F3;
            cursor: pointer;
        `;
        // Grup adını maskeleyerek göster (ilk harfi + nokta + son harfi)
        const groupName = group.name || 'İsimsiz Grup';
        const maskedGroupName = groupName.length > 2 ? `${groupName.charAt(0)}${'.'.repeat(Math.max(1, groupName.length - 2))}${groupName.charAt(groupName.length - 1)}` : groupName;
        const groupDisplay = `${maskedGroupName} (${group.code || '---'}) ${group.description || 'Açıklama yok'}`;
        groupInfoSection.innerHTML = `
            <div style="font-size: 0.9em; color: #1976D2; font-weight: 600; word-break: break-word; line-height: 1.4;" title="${groupName}">${groupDisplay}</div>
        `;
        groupInfoSection.onclick = () => showUserAccountDetails(group.created_by);
        membersList.appendChild(groupInfoSection);
        
        // Üyeler - aynı isimli olanları işle
        if (group.members && group.members.length > 0) {
            // Üyeleri inceleyerek aynı isim olanları bul
            const memberNames = group.members.map(m => m.first_name || m.firstName);
            const duplicates = memberNames.filter((item, index) => memberNames.indexOf(item) !== index);
            
            const membersTitle = document.createElement('div');
            membersTitle.style.cssText = `
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                font-size: 0.95em;
            `;
            
            // Başlık
            const titleSpan = document.createElement('span');
            titleSpan.textContent = `👥 Üyeler (${group.members.length}): `;
            membersTitle.appendChild(titleSpan);
            
            // Her üyeyi tıklanabilir span olarak ekle
            group.members.forEach((member, index) => {
                const firstName = member.first_name || member.firstName;
                const lastName = member.last_name || member.lastName;
                
                // Eğer bu isim duplicate ise, isim + soyadının baş harfini göster
                const displayName = duplicates.includes(firstName) ? `${firstName.charAt(0)}.${lastName}` : firstName;
                
                const memberSpan = document.createElement('span');
                memberSpan.textContent = displayName;
                memberSpan.style.cssText = `
                    padding: 2px 6px;
                    background: #e3f2fd;
                    border: 1px solid #90CAF9;
                    border-radius: 8px;
                    color: #1976D2;
                    cursor: pointer;
                    font-weight: 500;
                    margin-right: 6px;
                    user-select: none;
                    transition: all 0.2s ease;
                `;
                memberSpan.onmouseover = () => {
                    memberSpan.style.background = '#90CAF9';
                    memberSpan.style.color = 'white';
                };
                memberSpan.onmouseout = () => {
                    memberSpan.style.background = '#e3f2fd';
                    memberSpan.style.color = '#1976D2';
                };
                memberSpan.onclick = () => showUserAccountDetails(member.id);
                memberSpan.title = `${firstName} ${lastName}`;
                
                membersTitle.appendChild(memberSpan);
            });
            
            membersList.appendChild(membersTitle);
        }
        
        // Sipariş / Harcama Butonu
        const orderBtn = document.createElement('button');
        orderBtn.style.cssText = `
            width: 100%;
            padding: 12px;
            background: #FF9800;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 15px;
            font-size: 0.95em;
        `;
        orderBtn.textContent = '📊 Sipariş / Harcama';
        orderBtn.onmouseover = () => orderBtn.style.background = '#F57C00';
        orderBtn.onmouseout = () => orderBtn.style.background = '#FF9800';
        orderBtn.onclick = () => {
            console.log('Sipariş / Harcama tıklandı');
            // Bu buton henüz implement edilmemiş, ileride doldurulacak
            showNotification('Sipariş/Harcama özelliği yakında aktif olacak');
        };
        membersList.appendChild(orderBtn);
        
        // Davet linkini WhatsApp'ta Paylaş - Yeşil Buton (EN ALTTA)
        const participationLink = `${getAppURL()}?code=${group.code}`;
        const whatsappBtn = document.createElement('button');
        whatsappBtn.style.cssText = `
            width: 100%;
            padding: 12px;
            background: #25D366;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95em;
        `;
        whatsappBtn.textContent = '💬 Davet linkini WhatsApp\'ta Paylaş';
        whatsappBtn.onmouseover = () => whatsappBtn.style.background = '#20BA5A';
        whatsappBtn.onmouseout = () => whatsappBtn.style.background = '#25D366';
        whatsappBtn.onclick = () => shareToWhatsApp(participationLink, group.name, group.description);
        membersList.appendChild(whatsappBtn);
    })
    .catch(error => {
        console.error('Grup detayları yüklenemedi:', error);
        membersList.innerHTML = '<p style="color: #c0392b; text-align: center; padding: 20px;">Grup detayları yüklenemedi: ' + error.message + '</p>';
    });
}

function closeGroupMembersModal() {
    const modal = document.getElementById('gruphızlıerişim');
    modal.style.display = 'none';
}

// Modal dışına tıklandığında kapat
document.addEventListener('click', (e) => {
    const modal = document.getElementById('gruphızlıerişim');
    if (e.target === modal) {
        closeGroupMembersModal();
    }
});

// Helper Functions
function shareToWhatsApp(link, groupName, groupDescription) {
    // Link parametresinin doğru gelip gelmediğini kontrol et
    if (!link) {
        console.error('ERROR: Link undefined!');
        showNotification('Hata: Katılım linki bulunamadı');
        return;
    }
    
    // Mesajda MUTLAKA linki ekle
    const descriptionText = groupDescription ? ` (${groupDescription})` : '';
    const message = `${groupName} Grubuna${descriptionText} katıl!\n\nLinki tıkla: ${link}`;
    const encodedMessage = encodeURIComponent(message);
    
    console.log('shareToWhatsApp çağrıldı');
    console.log('Link parametresi:', link);
    console.log('Group ismi:', groupName);
    console.log('Oluşturulacak mesaj:', message);
    console.log('Encoded mesaj:', encodedMessage);
    
    const whatsappUrl = `https://wa.me/?text=${encodedMessage}`;
    console.log('WhatsApp URL:', whatsappUrl);
    // Yeni pencerede aç
    window.open(whatsappUrl, '_blank');
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('Link kopyalandı');
        }).catch(err => {
            console.error('Kopyalama başarısız:', err);
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

function showNotification(message) {
    // Bildirim göster
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #27ae60;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10002;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Yardımcı Fonksiyonlar
// Sayfa Yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // DEBUG: Show token status
    const token = localStorage.getItem('hesapPaylas_token');
    const debugToken = document.getElementById('debugToken');
    if (debugToken) {
        if (token) {
            debugToken.innerHTML = '<span class="status-ok">Token: FOUND (' + token.substring(0, 10) + '...)</span>';
        } else {
            debugToken.innerHTML = '<span class="status-error">Token: NOT FOUND - Login required</span>';
        }
    }
    
    loadFromLocalStorage();
    checkExistingUser();
    // Kullanıcı giriş yaparsa aktif grupları yükle
    setTimeout(() => {
        if (localStorage.getItem('hesapPaylas_token')) {
            loadActiveGroups();
        }
    }, 1000);
});

