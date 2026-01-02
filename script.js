// Service Worker Registration (PWA desteği)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js').then(registration => {
            console.log('Service Worker registered:', registration);
        }).catch(error => {
            console.log('Service Worker registration failed:', error);
        });
    });
}

// PWA Install Prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Install button gösterilebilir
});

// ===== API CONFIGURATION =====

const API_BASE_URL = 'http://localhost:5000/api';
const GOOGLE_CLIENT_ID = '625132087724-43j0qmqgh8kds471d73oposqthr8tt1h.apps.googleusercontent.com';

// Initialize Google Sign-In
window.addEventListener('load', () => {
    // Google Sign-In'i production'da enable et
    // Localhost'ta disabled (localhost OAuth yapılandırması yok)
    if (window.google && window.google.accounts && window.location.hostname !== 'localhost') {
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleResponse
        });
        
        // Render Google Sign-In button
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
            setTimeout(() => {
                alert(`Hoş geldiniz ${response.user.first_name}! 🎉`);
            }, 300);
        })
        .catch(error => {
            alert('Google ile giriş başarısız: ' + error.message);
        });
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
            const result = await response.json();
            
            if (!response.ok) {
                console.error('API Error:', result);
                throw new Error(result.error || 'API request failed');
            }
            
            return result;
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
    
    // API'ye kaydol
    const form = document.querySelector('.signup-form');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Kaydediliyor...';
    }
    
    api.signup(firstName, lastName, email, password, phone)
        .then(response => {
            const user = response.user;
            const token = response.token;
            
            // Token ve user'ı localStorage'a kaydet
            localStorage.setItem('hesapPaylas_token', token);
            localStorage.setItem('hesapPaylas_user', JSON.stringify(user));
            
            app.currentUser = user;
            
            showPage('homePage');
            setTimeout(() => {
                alert(`Hoş geldiniz ${user.first_name}! 🎉\n\nŞimdi hesap bölüşümünü başlatabilirsiniz.`);
            }, 300);
        })
        .catch(error => {
            alert('Kayıt başarısız oldu: ' + error.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Kaydol';
            }
        });
}

// Kayıt Tamamlama
function completeSignup(userData) {
    app.currentUser = userData;
    localStorage.setItem('hesapPaylas_user', JSON.stringify(userData));
    
    console.log("Kullanıcı kaydı tamamlandı:", userData);
    
    showPage('homePage');
    
    setTimeout(() => {
        alert(`Hoş geldiniz ${userData.firstName}! 🎉\n\nŞimdi hesap bölüşümünü başlatabilirsiniz.`);
    }, 300);
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
        alert('E-posta ve şifre alanlarını dolduru…!');
        return;
    }
    
    const form = document.querySelector('.login-form');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Giriş yapılıyor...';
    }
    
    api.login(email, password)
        .then(response => {
            const user = response.user;
            const token = response.token;
            
            // Token ve user'ı localStorage'a kaydet
            localStorage.setItem('hesapPaylas_token', token);
            localStorage.setItem('hesapPaylas_user', JSON.stringify(user));
            
            app.currentUser = user;
            
            // Form alanlarını temizle
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPassword').value = '';
            
            // Ana sayfaya yönlendir
            showPage('homePage');
            alert(`Hoş geldin ${user.firstName}!`);
        })
        .catch(error => {
            console.error('Login error:', error);
            const errorMsg = error.message || 'Giriş başarısız oldu';
            alert(errorMsg);
            
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Giriş Yap';
            }
        });
}

// Profil Sayfasına Git
function goToProfile() {
    if (!app.currentUser) {
        alert('Lütfen önce üye olunuz!');
        return;
    }
    
    // Profil bilgilerini doldur
    document.getElementById('profileName').textContent = 
        `${app.currentUser.firstName} ${app.currentUser.lastName}`;
    document.getElementById('profileEmail').textContent = app.currentUser.email;
    document.getElementById('profilePhone').textContent = app.currentUser.phone;
    document.getElementById('profileEmailInfo').textContent = app.currentUser.email;
    
    // Üyelik tarihi
    const today = new Date().toLocaleDateString('tr-TR');
    document.getElementById('profileDate').textContent = today;
    
    // Bonus puanlarını göster
    updateBonusPoints();
    
    showPage('profilePage');
}

// Bonus Puanlarını Güncelle
function updateBonusPoints() {
    // Demo veri - gerçek uygulamada database'ten gelecek
    const bonusPoints = app.currentUser.bonusPoints || 2450;
    const status = calculateMemberStatus(bonusPoints);
    
    document.getElementById('bonusPoints').textContent = `${bonusPoints.toLocaleString('tr-TR')} Puan`;
    document.getElementById('statusBadge').textContent = status.name;
    
    // Progress bar'ı güncelle
    const progressPercentage = (bonusPoints / 5000) * 100;
    document.getElementById('progressFill').style.width = Math.min(progressPercentage, 100) + '%';
    
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
    benefitsList.innerHTML = status.benefits.map(benefit => 
        `<li>✅ ${benefit}</li>`
    ).join('');
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

// Çıkış Yap
function logout() {
    if (confirm('Çıkış yapmak istediğinize emin misiniz?')) {
        app.currentUser = null;
        localStorage.removeItem('hesapPaylas_user');
        localStorage.removeItem('hesapPaylas_token');
        showPage('onboardingPage');
        alert('Başarıyla çıkış yaptınız. Hoşça kalın! 👋');
    }
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
    // Tüm sayfaları gizle
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Seçili sayfayı göster
    const page = document.getElementById(pageId);
    if (page) {
        page.classList.add('active');
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
    
    // Kod girişi için modal göster
    const groupCode = prompt('Lütfen grup kodunu giriniz:');
    if (groupCode && groupCode.trim()) {
        // Grup kodunu app'e kaydet ve bilgi sayfasına git
        app.groupCode = groupCode.trim();
        document.getElementById('infoTitle').innerText = 'Bilgilerinizi Girin';
        document.getElementById('groupIdGroup').style.display = 'none';
        document.getElementById('infoFirstName').value = '';
        document.getElementById('infoLastName').value = '';
        showPage('infoPage');
    }
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
// Çiçek İsimler
const flowerNames = [
    'Gül', 'Lale', 'Papatya', 'Yasemin', 'Orkide', 'Freesia', 'Karanfil',
    'Krizantem', 'Cezayir', 'Lilac', 'Magolia', 'Azalea', 'Kameya', 'Fersem',
    'Gerbera', 'Cala', 'Anthurium', 'Strelitzia', 'Aster', 'Hortensiya'
];

function showGroupCodePage(groupData) {
    console.log('showGroupCodePage çağrıldı, groupData:', groupData);
    // Başlık güncelle
    document.getElementById('groupWelcomeTitle').textContent = `Grubunuzun Adı: ${groupData.name}`;
    document.getElementById('groupCodeDisplay').textContent = groupData.code;
    console.log('Kod yazıldı:', groupData.code);
    
    // Paylaşma için global değişkene kaydet
    app.currentGroupCode = groupData.code;
    app.currentGroupName = groupData.name;
    app.currentGroupFullCode = groupData.fullCode;
    
    // QR kodu temizle
    const qrContainer = document.getElementById('qrCodeContainer');
    qrContainer.innerHTML = '';
    
    // QR kod oluştur
    try {
        new QRCode(qrContainer, {
            text: groupData.fullCode,
            width: 250,
            height: 250,
            colorDark: '#11a853',
            colorLight: '#ffffff'
        });
    } catch (e) {
        console.log('QR kod oluşturulamadı:', e);
    }
    
    // Grup kodu sayfasını göster
    showPage('groupCodePage');
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
    // Rastgele çiçek ismi seç
    const randomFlower = flowerNames[Math.floor(Math.random() * flowerNames.length)];
    
    // 9 haneli numara üret (xxx-xxx-xxx formatında)
    const num1 = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const num2 = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const num3 = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
    const numericCode = `${num1}-${num2}-${num3}`;
    
    return {
        name: randomFlower,
        code: numericCode,
        fullCode: `${randomFlower}-${numericCode}`
    };
}

// PAYLAŞMA SEÇENEKLERİ
function showShareOptions() {
    document.getElementById('shareModal').style.display = 'flex';
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
}

function shareViaWhatsApp() {
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl: ${app.currentGroupCode}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
    closeShareModal();
}

function shareViaTelegram() {
    const message = `Merhaba! ${app.currentGroupName} isimli gruba katıl: ${app.currentGroupCode}`;
    window.open(`https://t.me/share/url?url=&text=${encodeURIComponent(message)}`, '_blank');
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
function generateGroupId() {
    return Math.random().toString(36).substr(2, 9).toUpperCase();
}
// Sayfa Yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    checkExistingUser();
});
