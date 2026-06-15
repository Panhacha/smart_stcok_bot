# SmartStockBot 📦

**SmartStockBot** គឺជាប្រព័ន្ធគ្រប់គ្រងស្តុក និងការលក់ (POS) ដែលមានដំណើរការនៅលើ **Telegram Bot** រួមបញ្ចូលគ្នាជាមួយ **Telegram Mini App (Web App)**។ វាត្រូវបានរចនាឡើងដើម្បីជួយសម្រួលដល់ម្ចាស់ហាងក្នុងការគ្រប់គ្រងទំនិញ សាខា ចំណូល និងបុគ្គលិកដោយភាពងាយស្រួល និងសុវត្ថិភាព។

---

## 🌟 លក្ខណៈពិសេស (Key Features)

### 👥 ការគ្រប់គ្រងតួនាទី (Role Management)
- **Owner (ម្ចាស់ហាង)**: មានសិទ្ធិពេញលេញក្នុងការមើលរបាយការណ៍ បន្ថែម/លុបទំនិញ បង្កើតសាខា និងកែប្រែស្តុក។ ត្រូវមានលេខកូដ (PIN) ផ្ទាល់ខ្លួនដើម្បីចូល។
- **Staff (បុគ្គលិក)**: អាចស្កេនបាកូដលក់ទំនិញ ឆែកមើលស្តុក និងបញ្ចូលស្តុកប្រចាំថ្ងៃ។

### 🏢 ការគ្រប់គ្រងសាខា (Branch Management)
- គាំទ្រការគ្រប់គ្រងហាងដែលមានសាខាច្រើន។
- អាចបន្ថែមសាខាថ្មី ឬលុបសាខាដែលលែងប្រើ (Soft Delete ដើម្បីកុំអោយបាត់ប្រវត្តិលក់)។
- បុគ្គលិកត្រូវរើសសាខាប្រចាំការរបស់ខ្លួន។

### 📱 Telegram Mini App (Web App Integration)
- **POS Scanner (សម្រាប់បុគ្គលិក)**: ផ្ទាំងលក់ទំនិញដែលបុគ្គលិកអាចប្រើប្រាស់កាមេរ៉ាទូរស័ព្ទដើម្បីស្កេនបាកូដកាត់ស្តុកបានយ៉ាងលឿន។
- **Owner Dashboard (សម្រាប់ម្ចាស់ហាង)**: ផ្ទាំងសង្ខេបទិន្នន័យ (ចំណូលសរុប, ចំនួនលក់, និងទំនិញជិតអស់ស្តុក)។
- **History (ប្រវត្តិលក់)**: អាចឆែកមើលប្រតិបត្តិការលក់ និងកាត់ស្តុកបានយ៉ាងងាយស្រួលតាមកាលបរិច្ឆេទ។

### 📊 របាយការណ៍ និងការកត់ត្រា (Reports & Tracking)
- កត់ត្រារាល់ប្រតិបត្តិការទាំងអស់ (លក់, បញ្ចូលស្តុក, កែតម្រូវ, ខូចខាត)។
- បញ្ចេញរបាយការណ៍ជាទម្រង់ PDF សម្រាប់ប្រចាំថ្ងៃ និងប្រចាំខែ។

---

## 🛠 បច្ចេកវិទ្យាដែលប្រើប្រាស់ (Tech Stack)

- **Backend (Bot)**: Python, `aiogram` (Telegram Bot Framework)
- **Frontend (Web App)**: React.js, Vite, CSS (Glassmorphism UI)
- **Database**: Supabase (PostgreSQL)
- **Report Generation**: `reportlab` (PDF generation)

---

## 🚀 របៀបដំឡើង និងដំណើរការ (Setup & Run)

### ១. តម្រូវការជាមុន (Prerequisites)
- Python 3.9+
- Node.js & npm (សម្រាប់ Web App)
- គណនី Supabase (Database)
- Telegram Bot Token ពី [@BotFather](https://t.me/BotFather)

### ២. ការកំណត់ Environment Variables
បង្កើត File ឈ្មោះ `.env` នៅថតខាងក្រៅ (Root directory) ដោយមានទិន្នន័យដូចខាងក្រោម៖
```env
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OWNER_PIN=1234
STAFF_PIN=1111
WEBAPP_URL=your_ngrok_or_vercel_url
```

### ៣. របៀបដំណើរការ Bot (Run the Bot)
```bash
# ដំណើរការ Virtual Environment (បើមាន)
.\venv\Scripts\activate

# Install ជំនួយផ្សេងៗ
pip install -r requirements.txt

# Run ប៊ត
python run_polling.py
```

### ៤. របៀបដំណើរការ Web App (Run the Web App)
```bash
cd webapp
npm install
npm run dev
```
*(ចំណាំ៖ ត្រូវប្រើប្រាស់ `ngrok` ឬ Cloudflared ដើម្បីភ្ជាប់ localhost web app ជាមួយ Telegram Bot `WEBAPP_URL` ក្នុងពេលកំពុង Develop)*

---

## 📁 រចនាសម្ព័ន្ធកូដ (Project Structure)
```
SmartStockBot/
│
├── bot/                       # កូដស្នូលរបស់ Telegram Bot
│   ├── handlers/              # គ្រប់គ្រងការបញ្ជា (Owner, Staff, Common)
│   ├── database/              # មុខងារទាក់ទងនឹង Database (Supabase)
│   ├── middlewares/           # គ្រប់គ្រងសិទ្ធិអ្នកប្រើប្រាស់
│   └── ui/                    # រៀបចំ Keyboards នៅក្នុង Bot
│
├── webapp/                    # កូដ Telegram Mini App (React)
│   ├── src/
│   │   ├── App.jsx            # ផ្ទាំងផ្លាស់ប្តូរ (Router)
│   │   ├── Dashboard.jsx      # ផ្ទាំង Owner
│   │   ├── POS.jsx            # ផ្ទាំង Staff
│   │   └── index.css          # រចនាបទ UI
│
├── run_polling.py             # ឯកសារសម្រាប់ចាប់ផ្តើមដំណើរការ Bot
├── schema.sql                 # ទម្រង់ Database Tables
└── README.md                  # ឯកសារជំនួយនេះ




`.env 

BOT_TOKEN=8947126421:AAGwdn_F7mg2OlDqqF6KYJuvvVYA9FMThjM
SUPABASE_URL=https://gjdjqnffelyxsgzzgpmn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdqZGpxbmZmZWx5eHNnenpncG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEzODY5NzAsImV4cCI6MjA5Njk2Mjk3MH0.ox1BitnRY0KGuWz40TnwCrqd_zr2iJ_f0LkHEG77Hi4
WEBHOOK_HOST=aws-1-ap-northeast-1.pooler.supabase.com
