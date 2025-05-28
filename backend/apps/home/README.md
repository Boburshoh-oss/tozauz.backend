# Home App - Uy Boshqaruvi

Ushbu app foydalanuvchilarni uylarga birlashtirib, har bir uy a'zolarining EcoPacket faoliyatini kuzatish imkonini beradi.

## Features

- ✅ **Uy yaratish va boshqarish**
- ✅ **Taklifnoma kodi orqali uyga qo'shilish**
- ✅ **Uy a'zolarining EcoPacket statistikasi**
- ✅ **Optimallashtirilgan ORM so'rovlar** (`annotate` + `Count`)
- ✅ **Admin panel integratsiyasi**
- ✅ **To'liq test coverage**

## Installation

### 1. Migration yaratish va qo'llash:

```bash
cd backend
python manage.py makemigrations home
python manage.py migrate
```

### 2. Django admin-da superuser yarating (agar yo'q bo'lsa):

```bash
python manage.py createsuperuser
```

## API Endpoints

### Asosiy Report Endpoint (Talabga mos)

#### `GET /api/home/report/`

Foydalanuvchining uyidagi barcha a'zolar va ularning EcoPacket sonlarini qaytaradi.

**Authentication:** Required  
**Response:**

```json
{
  "home_id": 1,
  "home_name": "Bizning Uy",
  "member_count": 3,
  "total_ecopackets": 45,
  "members": [
    {
      "user_id": 1,
      "username": "998901234567",
      "first_name": "Akmal",
      "last_name": "Karimov",
      "phone_number": "998901234567",
      "ecopacket_count": 20,
      "joined_at": "2024-01-15T10:30:00Z",
      "is_admin": true
    }
  ]
}
```
