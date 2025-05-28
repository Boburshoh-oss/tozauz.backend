# 🏠 Uy va Hudud Boshqaruvi - Yangi Funksionallik

## 📋 Umumiy Ma'lumot

Ushbu yangilanish `Home` modeliga hudud (region) tushunchasi va oylik chiqindi limitlari bilan bog'liq professional funksionallikni qo'shadi. Har bir uy ma'lum bir hududga tegishli bo'ladi va hudud o'zining oylik chiqindi limitiga ega bo'ladi.

## 🎯 Asosiy Xususiyatlar

### 1. Hudud (Region) Tizimi
- ✅ Har bir hudud noyob kod va nom bilan
- ✅ Oylik chiqindi limitlari (default: 15 ta paket)
- ✅ Hudud statistikalari va hisobotlari
- ✅ Avtomatik limit kuzatuvi

### 2. Ogohlantirishlar Tizimi
- ✅ 80% - 🟡 Ogohlantirish
- ✅ 100%+ - 🔴 Kritik holat
- ✅ Real-time monitoring
- ✅ Email xabarnomalar

### 3. Hisobotlar va Statistika
- ✅ Oylik hisobotlar avtomatik yaratish
- ✅ Hudud bo'yicha statistika
- ✅ Uy hissasi va foizlari
- ✅ Tarixiy ma'lumotlar

## 🗂️ Yangi Modellar

### Region (Hudud)
```python
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    monthly_waste_limit = models.PositiveIntegerField(default=15)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### WasteMonthlyReport (Oylik Hisobot)
```python
class WasteMonthlyReport(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    total_scans = models.PositiveIntegerField(default=0)
    total_homes = models.PositiveIntegerField(default=0)
    total_members = models.PositiveIntegerField(default=0)
    limit_exceeded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🔧 Yangilanigan Modellar

### Home (Uy) - Yangi Maydonlar
```python
# Yangi maydon
region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="homes")

# Yangi metodlar
def get_monthly_waste_count(self, year=None, month=None)
def check_region_limit_warning(self, year=None, month=None)
```

## 🌐 API Endpoints

### Hudud (Region) Endpoints
```
GET /api/home/regions/                    # Hududlar ro'yxati
GET /api/home/regions/{id}/               # Hudud tafsilotlari
GET /api/home/regions/{id}/monthly_stats/ # Oylik statistika
POST /api/home/regions/{id}/generate_report/ # Hisobot yaratish
```

### Uy (Home) Endpoints - Yangilangan
```
GET /api/home/homes/          # Uylar ro'yxati (region ma'lumotlari bilan)
GET /api/home/warning/        # Uy ogohlantirishini olish
GET /api/home/region-warnings/ # Barcha hududlar holati
GET /api/home/status/         # Foydalanuvchi holati (region bilan)
```

### Yangi API Response Misollari

#### Region Statistics
```json
{
  "year": 2024,
  "month": 12,
  "total_scans": 12,
  "limit": 15,
  "remaining": 3,
  "is_exceeded": false,
  "usage_percentage": 80.0
}
```

#### Home Warning Response
```json
{
  "home_id": 1,
  "home_name": "Mening Uyim",
  "region_name": "Toshkent shahri",
  "has_warning": true,
  "is_critical": false,
  "region_stats": {
    "total_scans": 12,
    "limit": 15,
    "remaining": 3,
    "usage_percentage": 80.0
  },
  "home_contribution": 5,
  "home_percentage": 41.67,
  "warning_message": "🟡 ESLATMA: Toshkent shahri hududida oylik limit 80% ga yetdi! Qolgan: 3 ta paket."
}
```

## 💻 Management Commands

### Hududlarni To'ldirish
```bash
# O'zbekiston hududlarini yaratish
python manage.py populate_regions

# Mavjud hududlarni o'chirish va qayta yaratish  
python manage.py populate_regions --clear
```

### Oylik Hisobotlar
```bash
# Barcha hududlar uchun joriy oy hisoboti
python manage.py generate_monthly_reports

# Ma'lum hudud uchun
python manage.py generate_monthly_reports --region TAS-01

# Ma'lum oy uchun
python manage.py generate_monthly_reports --year 2024 --month 11

# Mavjud hisobotlarni qayta yaratish
python manage.py generate_monthly_reports --force
```

## 🚨 Avtomatik Ogohlantirishlar

### Signal-based Monitoring
- EcoPacket skanerlanganda avtomatik tekshirish
- 80% yetganda ogohlantirish
- 100% oshganda kritik xabar
- Email xabarnomalar (konfiguratsiya kerak)

### Settings Konfiguratsiyasi
```python
# settings.py da qo'shing
REGION_ADMIN_EMAIL = "admin@example.com"
DEFAULT_FROM_EMAIL = "noreply@example.com"

# Email konfiguratsiyasi
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

## 📊 Admin Panel Yangilanishlari

### Region Admin
- 📈 Real-time statistika ko'rinishi
- 🎨 Rangli indikatorlar (qizil/sariq/yashil)
- 📋 Limit holati monitorngi
- ⚡ Hisobotlar yaratish action

### Home Admin
- 🌍 Hudud ma'lumotlari
- ⚠️ Ogohlantirish holati
- 📊 Oylik chiqindi hisobchisi
- 🔍 Filtrlash va qidiruv yangilandi

## 🧪 Testing

### Test Fayllar
```bash
# Unit testlar
python manage.py test apps.home.test_region_functionality

# Manual test ma'lumotlari yaratish
python manage.py shell -c "
import apps.home.test_region_functionality as test
test.create_test_data()
"
```

### Test Ma'lumotlari
- Test hudud (TEST-01) - 5 ta limit
- Test uy va foydalanuvchi
- Limit test qilish uchun tayyor

## 📁 Fayl Strukturasi

```
backend/apps/home/
├── models.py                    # Region, WasteMonthlyReport, Home yangilandi
├── admin.py                     # Admin paneli yangilandi  
├── serializers.py               # Yangi serializer'lar
├── views.py                     # Region ViewSet, warning endpoints
├── urls.py                      # Yangi URL'lar
├── signals.py                   # Avtomatik monitoring
├── apps.py                      # Signal import
├── management/
│   └── commands/
│       ├── populate_regions.py        # Hududlar yaratish
│       └── generate_monthly_reports.py # Hisobotlar yaratish
├── test_region_functionality.py       # Test fayllar
└── README_REGION_FUNCTIONALITY.md     # Bu fayl
```

## 🚀 Ishga Tushirish

### 1. Migration yaratish va ishlatish
```bash
cd backend
python manage.py makemigrations home
python manage.py migrate
```

### 2. Hududlarni to'ldirish
```bash
python manage.py populate_regions
```

### 3. Admin superuser yaratish (agar yo'q bo'lsa)
```bash
python manage.py createsuperuser
```

### 4. Test ma'lumotlari yaratish
```bash
python manage.py shell -c "
import apps.home.test_region_functionality as test
test.create_test_data()
"
```

### 5. Server ishga tushirish
```bash
python manage.py runserver
```

## 📋 Foydalanish Misollari

### 1. Yangi Uy Yaratish (hudud bilan)
```python
# API orqali
POST /api/home/homes/
{
  "name": "Mening Uyim",
  "region": 1,  # Hudud ID
  "address": "Toshkent, Yunusobod",
  "description": "Oilaviy uy"
}
```

### 2. Hudud Holati Tekshirish
```python
# API orqali
GET /api/home/warning/

# Response
{
  "has_warning": true,
  "warning_message": "🟡 ESLATMA: Toshkent shahri hududida oylik limit 80% ga yetdi!"
}
```

### 3. Hisobot Yaratish
```python
# API orqali
POST /api/home/regions/1/generate_report/
{
  "year": 2024,
  "month": 12
}
```

## 🔧 Konfiguratsiya

### 1. Limit Chegaralarini O'zgartirish
```python
# models.py da
warning_threshold = 0.8  # 80% da ogohlantirish
critical_threshold = 1.0  # 100% da kritik
```

### 2. Email Xabarnomalarni Yoqish
```python
# settings.py da
REGION_ADMIN_EMAIL = "admin@yourcompany.uz"
```

### 3. Logging Konfiguratsiyasi
```python
LOGGING = {
    'loggers': {
        'apps.home.signals': {
            'level': 'INFO',
            'handlers': ['file'],
        },
    },
}
```

## 🔮 Kelajakdagi Rivojlanish

- 📱 Mobile push notification'lar
- 📊 Dashboard va visualizatsiya
- 🤖 AI-based prediction
- 📈 Trend analysis
- 🌟 Gamification elements

---

**✨ Muvaffaqiyatli amalga oshirildi!** Endi sizning Home tizimi professional darajada hudud boshqaruvi va oylik limit kuzatuvi imkoniyatlariga ega bo'ldi. 