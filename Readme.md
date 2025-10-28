 🧢 Skill-Hat

**Skill-Hat** is a web-based service platform that connects **semi-skilled workers** in Bangladesh (such as electricians, painters, tutors, drivers, and cleaners) with customers seeking **short-term or small-scale services**.  
The platform ensures **trust, transparency, and security** through verified profiles, escrow payments, and controlled communication.

---

## 📖 Overview

Millions of semi-skilled workers in Bangladesh face **unstable employment**, while customers pay **excessive fees** due to intermediaries.  
**Skill-Hat** eliminates these middlemen by offering a **direct digital bridge** between workers and clients — secured with **verification, fair payment, and smart matching**.

---

## 🎯 Objectives

- Provide a **secure and reliable** online platform for hiring semi-skilled workers.  
- Implement a **smart payment and penalty system** using escrow logic.  
- Enable **trust-based connections** through NID and police verification.  
- Prevent off-platform fraud with **controlled communication**.  
- Offer **location-based smart worker matching** for convenience.

---

## ⚙️ Tech Stack

| Category | Technology |
|-----------|-------------|
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Backend** | Django (Python 3) |
| **Database** | MySQL |
| **Version Control** | Git & GitHub |
| **Hosting (Optional)** | Render / Vercel / Railway |
| **Authentication** | Django Auth System (Email/Phone Verification) |

---

## 🧩 Core Features

### 👷 Worker Features
- Profile creation with skill category & location.  
- NID and phone/email verification.  
- Police clearance upload (for sensitive jobs).  
- Rating and feedback from customers.  

### 🧍 Customer Features
- Browse workers by category and location.  
- Book and pay through the escrow system.  
- Cancel with penalty rules applied.  
- Rate workers after job completion.  

### 🧠 Admin Features
- Manage users, transactions, and trust scores.  
- Detect off-platform communications.  
- View analytics on worker performance and engagement.

---

## 🔒 Security & Trust System

- **Verified Profiles:** Every worker verified via NID, phone/email, and police clearance.  
- **Escrow Payments:** Funds held securely until both parties confirm completion.  
- **Trust Score:** Ratings affect job visibility and priority in search.  
- **Controlled Chat:** Phone numbers and links auto-removed before payment confirmation.

---

## 🏗️ Project Setup (Local Development)

### Prerequisites
- Python 3.12+  
- MySQL installed and running  
- Django (latest stable release)  

### 1️⃣ Clone the Repository
\`\`\`bash
git clone https://github.com/kawser25350/Skill-hat.git
cd Skill-hat
\`\`\`

### 2️⃣ Create & Activate Virtual Environment
\`\`\`bash
python -m venv venv
venv\\Scripts\\activate   # On Windows
source venv/bin/activate  # On Linux/Mac
\`\`\`

### 3️⃣ Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4️⃣ Configure MySQL Database
Open \`settings.py\` and set your credentials:
\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skill_hat_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
\`\`\`

### 5️⃣ Apply Migrations
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 6️⃣ Create a Superuser
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 7️⃣ Run the Server
\`\`\`bash
python manage.py runserver
\`\`\`
Visit the app at **http://127.0.0.1:8000/**

---

## 🎨 UI Design
- Built with **HTML5**, **CSS3**, and **Bootstrap 5** for responsiveness.  
- Clean, minimal interface focused on usability and accessibility.  
- Ready for integration with custom Django templates.

---

## 🧮 Future Enhancements
- AI-based worker recommendation system.  
- Real-time chat with message moderation.  
- Mobile-first PWA (Progressive Web App) version.  
- Job completion image verification for escrow release.

---

## 👥 Contributors

| Name | Role |
|------|------|
| **Kawser Ahmmed** | Project Lead / Full-Stack Developer |
| **Marziya sultana** | developer  /  Frontent-Developer |
---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this project with proper attribution.

---

## 📬 Contact

For inquiries, suggestions, or collaborations:

**Email:** kawser25350@gmail.com  
**GitHub:** [kawser25350](https://github.com/kawser25350)

---

> **Skill-Hat — Empowering Bangladesh’s semi-skilled workforce with digital trust and opportunity.**

