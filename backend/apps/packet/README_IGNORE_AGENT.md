# 🏷️ Category.ignore_agent Funksionalligi

## 📋 Umumiy Ma'lumot

`Category` modeliga qo'shilgan `ignore_agent` maydoni orqali ma'lum kategoriyaga tegishli ecopaket skanerlanganda `box.seller`ga ulush berilmasligi va barcha to'lovlar faqat foydalanuvchining o'ziga berilishi ta'minlanadi.

## 🔧 Funksionallik tavsifi

- `Category.ignore_agent = False` (default) - odatiy holat, bunda box.seller mavjud bo'lsa, unga belgilangan foizda ulush beriladi
- `Category.ignore_agent = True` - bu holda box.seller'ga ulush berilmaydi, barcha to'lovlar to'liq foydalanuvchiga tushadi

## 🖥️ Qanday ishlaydi?

1. Foydalanuvchi ecopaket QR kodini skanerlaydi
2. Tizim QR kodning kategoriyasini tekshiradi
3. Agar `category.ignore_agent == True` bo'lsa:
   - Sellerga hech qanday ulush bermasdan, to'liq summa foydalanuvchiga o'tkaziladi
   - Box.seller_share o'zgarmaydi
   - Foydalanuvchiga to'liq 100% summa o'tadi
4. Agar `category.ignore_agent == False` bo'lsa:
   - Box.seller_percentage asosida sellerga ulush beriladi (masalan, 30%)
   - Box.seller_share oshadi
   - Foydalanuvchiga qolgan summa o'tadi (masalan, 70%)

## 🛠️ Yangilangan Kodlar

### 1. Modellar

`Category` modelida `ignore_agent` maydoni allaqachon mavjud edi:

```python
class Category(models.Model):
    name = models.CharField(max_length=50)
    summa = models.PositiveIntegerField()
    ignore_agent = models.BooleanField(default=False)
    
    # ...
```

### 2. Admin Panel

Admin panel yangilandi, endi `ignore_agent` filtrlash va ro'yxatda ko'rish mavjud:

```python
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'summa', 'ignore_agent', 'count_user')
    list_filter = ['ignore_agent']
    search_fields = ['name']
    list_editable = ['ignore_agent']
```

### 3. Skanerlash Logikasi

QR kod skanerlanganda quyidagi logika ishlaydi:

```python
# Kategoriya ignore_agent=True bo'lsa, hamma pul foydalanuvchiga beriladi
if ecopakcet_catergory.ignore_agent:
    # Seller ulushini hisoblamay, hammasi foydalanuvchiga boradi
    bank_account.capital += ecopakcet_money
    bank_account.save()
    
    Earning.objects.create(
        bank_account=bank_account,
        amount=ecopakcet_money,
        tarrif=ecopakcet_catergory.name,
        box=box,
    )
else:
    # Odatiy hisob-kitob...
    # Seller ulushini hisoblash va berish...
```

## 📊 Yaratilgan Testlar

Test qilish uchun ikkita holat yaratildi:

1. `test_normal_category_scan()` - Odatiy kategoriyani test qilish (ignore_agent=False)
2. `test_ignored_category_scan()` - Yangi funksionallikni test qilish (ignore_agent=True)

## 🚀 Ishga Tushirish

### 1. Test kategoriyalar yaratish

```bash
python manage.py setup_test_categories
```

Bu quyidagi test kategoriyalarini yaratadi:
- Plastik, Qog'oz, Metal, Shisha (ignore_agent=False)
- Organik, Boshqa, Maishiy (ignore_agent=True)

### 2. Testlarni ishlatish

```bash
python manage.py test apps.packet.tests.CategoryIgnoreAgentTestCase
```

## 📝 Eslatmalar

1. Mavjud kategoriyalarni yangilash uchun admin panelida "ignore_agent" maydonini belgilang
2. Yangi kategoriyalar yaratishda "ignore_agent" maydoni uchun qiymat tanlang
3. Funksionallik amal qilishi uchun backend kodi yangilanishi kerak edi

## 🔄 Kerak bo'ladigan migratsiya fayllar

Ushbu funksionallik Category modelida allaqachon ignore_agent maydoni mavjud bo'lganligi uchun yangi migratsiya fayllar talab qilinmaydi.

---

**Muallif:** TozaUz Backend Development Team
**Sana:** YYYY-MM-DD 