/**
 * Hesap Paylaş - Main Application Script
 * Version: 2.0.0
 * Last Updated: 2026-01-09
 */

// Service Worker DISABLED - Caching issues
/*
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js').then(registration => {
            console.log('Service Worker registered:', registration);
        }).catch(error => {
            console.log('Service Worker registration failed:', error);
        });
        
        // Deep link'i handle et
        handleDeepLink();
    });
}
*/

// Unregister existing service workers
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
        registrations.forEach(registration => {
            registration.unregister();
            console.log('Service Worker unregistered');
        });
    });
    
    window.addEventListener('load', () => {
        handleDeepLink();
    });
}

// PWA Install Prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Install button gösterilebilir
});

// Deep Link Handler - URL parametrelerini kontrol et
function handleDeepLink() {
    const params = new URLSearchParams(window.location.search);
    const groupCode = params.get('code');
    
    if (groupCode && /^\d{3}-\d{3}-\d{3}$/.test(groupCode)) {
        console.log('Deep link detected with code:', groupCode);
        
        // Eğer user login'se direkt gruba katıl
        const user = localStorage.getItem('hesapPaylas_user');
        if (user) {
            // User varsa, gruba katılma akışını başlat
            app.currentMode = 'join_group';
            app.groupCode = groupCode;
            
            setTimeout(() => {
                document.getElementById('infoTitle').innerText = 'Bilgilerinizi Girin';
                document.getElementById('groupIdGroup').style.display = 'none';
                document.getElementById('infoFirstName').value = '';
                document.getElementById('infoLastName').value = '';
                showPage('infoPage');
            }, 500);
        } else {
            // Login değilse, group code'u sessionStorage'e kaydet ve login sayfasına yönlendir
            sessionStorage.setItem('pendingGroupCode', groupCode);
        }
    }
}

// ===== API CONFIGURATION =====

const API_BASE_URL = 'http://localhost:5000/api';
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
            // Profil butonunu göster
            if (profileBtn) profileBtn.style.display = 'block';
            
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
    // Şimdilik varsayılan konum
    const targetLocationInput = document.getElementById('targetLocation');
    targetLocationInput.value = 'Kızılay, Ankara (40.9893, 29.0412)';
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
                let error;
                if (contentType && contentType.includes('application/json')) {
                    const result = await response.json();
                    error = result.error || 'API request failed';
                } else {
                    error = `HTTP ${response.status}: ${response.statusText}`;
                }
                console.error('API Error:', error);
                throw new Error(error);
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
    
    // Telefon validasyonu
    const phoneRegex = /^(\+90|0)?\d{10}$/;
    const cleanPhone = phone.replace(/\s/g, '');
    if (!phoneRegex.test(cleanPhone)) {
        alert('Geçerli bir telefon numarası giriniz!');
        return;
    }
    
    // Offline Mode - localStorage'a kaydet
    const user = {
        id: Date.now().toString(),
        firstName: firstName,
        lastName: lastName,
        email: email,
        phone: phone,
        createdAt: new Date().toISOString()
    };
    
    // localStorage'a kullanıcıyı ve şifreyi kaydet (demo amaçlı)
    const usersData = JSON.parse(localStorage.getItem('hesapPaylas_users') || '{}');
    usersData[email] = {
        ...user,
        password: password // Demo amaçlı (gerçek app'te hash edilmeli)
    };
    localStorage.setItem('hesapPaylas_users', JSON.stringify(usersData));
    
    // Giriş yap
    localStorage.setItem('hesapPaylas_token', 'demo-token-' + user.id);
    localStorage.setItem('hesapPaylas_user', JSON.stringify(user));
    
    app.currentUser = user;
    
    // Formu temizle
    document.getElementById('manualSignupForm').reset();
    
    // Ana sayfaya git
    showPage('homePage');
    
    // Profil bilgilerini güncelle
    updateHomePageProfile();
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
    const signupTabBtn = document.getElementById('signupTabBtn');
    const loginTabBtn = document.getElementById('loginTabBtn');
    
    if (formType === 'signup') {
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
        signupTabBtn.classList.add('active');
        loginTabBtn.classList.remove('active');
    } else {
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';
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
    
    // Offline Mode - localStorage'dan kontrol et
    const usersData = JSON.parse(localStorage.getItem('hesapPaylas_users') || '{}');
    const userData = usersData[email];
    
    if (!userData || userData.password !== password) {
        alert('E-posta veya şifre yanlış!');
        return;
    }
    
    // Giriş başarılı
    const user = {
        id: userData.id,
        firstName: userData.firstName,
        lastName: userData.lastName,
        email: userData.email,
        phone: userData.phone,
        createdAt: userData.createdAt
    };
    
    localStorage.setItem('hesapPaylas_token', 'demo-token-' + user.id);
    localStorage.setItem('hesapPaylas_user', JSON.stringify(user));
    
    app.currentUser = user;
    
    // Form alanlarını temizle
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';
    
    // Ana sayfaya yönlendir
    showPage('homePage');
    
    // Profil bilgilerini güncelle
    updateHomePageProfile();
}

// Profil Sayfasına Git
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
    const profileDate = document.getElementById('profileDate');
    
    if (profileName) profileName.textContent = `${user.firstName || ''} ${user.lastName || ''}`.trim() || 'Kullanıcı';
    if (profileEmail) profileEmail.textContent = user.email || '';
    if (profilePhone) profilePhone.textContent = user.phone || '-';
    if (profileEmailInfo) profileEmailInfo.textContent = user.email || '';
    
    // Üyelik tarihi
    const memberDate = user.createdAt ? new Date(user.createdAt).toLocaleDateString('tr-TR') : new Date().toLocaleDateString('tr-TR');
    if (profileDate) profileDate.textContent = memberDate;
    
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
        
        // If showing homePage, show the menu
        if (pageId === 'homePage' && homeMenu) {
            homeMenu.style.display = 'block';
            homeMenu.style.visibility = 'visible';
            homeMenu.style.opacity = '1';
        }
        
        window.scrollTo(0, 0);
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

// Grup Kurma
function goToCreateGroup() {
    app.currentMode = 'create_group';
    // Grubu hemen oluştur - infoPage'i atla
    const groupData = generateGroupId();
    console.log('Grup Oluşturuldu:', groupData);
    app.groupId = groupData.fullCode;
    app.groupName = groupData.name;
    showGroupCodePage(groupData);
}

// Grup Katılma
function goToJoinGroup() {
    app.currentMode = 'join_group';
    
    // Manuel kod girişi seçeneği göster
    showPage('joinCodePage');
    document.getElementById('joinGroupCode').value = '';
    document.getElementById('joinCodeResult').innerHTML = '';
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
            
            // Deep link formatını kontrol et: hesappaylas://join?code=xxx-xxx-xxx&name=groupname
            if (code.data.startsWith('hesappaylas://')) {
                // Deep link formatı
                const urlParams = new URLSearchParams(code.data.replace('hesappaylas://join?', ''));
                const groupCode = urlParams.get('code');
                
                if (groupCode && /^\d{3}-\d{3}-\d{3}$/.test(groupCode)) {
                    resultDiv.innerHTML = `<p style="color: green; font-weight: bold;">✓ Kod okundu: ${groupCode}</p>`;
                    proceedToJoinGroup(groupCode);
                } else {
                    resultDiv.innerHTML = '<p style="color: red;">Geçersiz QR kod</p>';
                    qrScannerActive = true;
                    setTimeout(() => scanQRCode(video, canvas, resultDiv), 500);
                }
            } else {
                // Eski format uyumluluğu: "groupname-xxx-xxx-xxx"
                const parts = code.data.split('-');
                if (parts.length === 4) {
                    const groupCode = `${parts[1]}-${parts[2]}-${parts[3]}`;
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
    
    // Kod formatını doğrula (xxx-xxx-xxx)
    if (!/^\d{3}-\d{3}-\d{3}$/.test(groupCode)) {
        resultDiv.innerHTML = '<p style="color: red;">Geçersiz kod formatı! (xxx-xxx-xxx şeklinde olmalı)</p>';
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
    
    // Grup kuruyorsa, grup kodu oluştur
    if (app.currentMode === 'create_group') {
        const groupData = generateGroupId();
        app.groupId = groupData.fullCode;
        app.groupName = groupData.name;
        
        // Grup kodu göstereceği sayfaya yönlendir
        showGroupCodePage(groupData);
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

function showGroupCodePage(groupData) {
    console.log('showGroupCodePage çağrıldı, groupData:', groupData);
    
    // Renk kodu haritası
    const colorMap = {
        'Kırmızı': '#e74c3c',
        'Mavi': '#3498db',
        'Yeşil': '#27ae60',
        'Sarı': '#f1c40f',
        'Turuncu': '#e67e22',
        'Mor': '#9b59b6',
        'Pembe': '#e91e63',
        'Siyah': '#2c3e50',
        'Beyaz': '#ecf0f1',
        'Gri': '#95a5a6',
        'Kahverengi': '#8b4513',
        'Turkuaz': '#1abc9c',
        'İndigo': '#4b0082',
        'Lila': '#da70d6',
        'Kestane': '#a0522d',
        'Açık Mavi': '#5dade2',
        'Açık Yeşil': '#52be80',
        'Açık Kırmızı': '#f5b7b1',
        'Koyu Mavi': '#1b4965',
        'Koyu Yeşil': '#186a3b'
    };
    
    // Başlık güncelle - renk adı göster ve rengi uygula
    const titleSpan = document.getElementById('groupWelcomeTitle');
    titleSpan.textContent = groupData.name;
    titleSpan.style.color = colorMap[groupData.name] || '#333';
    
    // Format code as xxx-xxx (6 digits with one dash)
    const codeStr = groupData.code.toString().padStart(6, '0');
    const formattedCode = codeStr.replace(/(\d{3})(\d{3})/, '$1-$2');
    document.getElementById('groupCodeDisplay').textContent = formattedCode;
    console.log('Kod yazıldı:', formattedCode);
    
    // Paylaşma için global değişkene kaydet
    app.currentGroupCode = groupData.code;
    app.currentGroupName = groupData.name;
    app.currentGroupFullCode = groupData.fullCode;
    
    // Grup kodu sayfasını göster
    showPage('groupCodePage');
    
    // QR kod oluşturma işlemini biraz sonra yap (sayfaydın render olduktan sonra)
    setTimeout(() => {
        const qrContainer = document.getElementById('qrCodeContainer');
        console.log('QR Container:', qrContainer);
        
        // QR kodunda deep link formatı kullan: hesappaylas://join?code=xxx-xxx-xxx&name=groupname
        const deepLinkUrl = `hesappaylas://join?code=${groupData.code}&name=${encodeURIComponent(groupData.name)}`;
        console.log('Deep Link URL:', deepLinkUrl);
        
        if (qrContainer) {
            // Var olan QR kodu temizle
            qrContainer.innerHTML = '';
            
            try {
                if (typeof QRCode !== 'undefined') {
                    console.log('QR kod oluşturmaya başlanıyor...');
                    new QRCode(qrContainer, {
                        text: deepLinkUrl,
                        width: 200,
                        height: 200,
                        colorDark: '#11a853',
                        colorLight: '#ffffff'
                    });
                    console.log('QR kod başarıyla oluşturuldu');
                } else {
                    console.error('QRCode kütüphanesi yüklenmedi! QRCode değeri:', window.QRCode);
                    qrContainer.textContent = 'QR Kod Oluşturulamadı';
                }
            } catch (e) {
                console.error('QR kod oluşturulamadı - Hata:', e.message);
                console.error('Hata stack:', e.stack);
                qrContainer.textContent = 'Hata: ' + e.message;
            }
        } else {
            console.error('qrCodeContainer bulunamadı!');
        }
    }, 200);
}

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
        // Kullanıcı giriş yapmış, doğrudan WhatsApp'ta paylaş
        shareViaWhatsApp();
    } else {
        // Kullanıcı giriş yapmamış, giriş sayfasına yönlendir
        showPage('onboardingPage');
    }
}

function shareViaWhatsApp() {
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl: ${app.currentGroupCode}`;
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

// Yardımcı Fonksiyonlar
// Sayfa Yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    checkExistingUser();
});
