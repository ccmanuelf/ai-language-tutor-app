# Admin Setup & User Management Guide

> **Complete guide for setting up and managing your family's AI Language Tutor**

## 📋 Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Creating User Accounts](#creating-user-accounts)
3. [Managing Users](#managing-users)
4. [Budget Management](#budget-management)
5. [System Monitoring](#system-monitoring)

---

## 🚀 First-Time Setup

### Prerequisites Checklist

- [ ] Python 3.12 or higher installed
- [ ] Git installed (for cloning repository)
- [ ] Text editor (VS Code, Sublime, nano, etc.)
- [ ] Internet connection
- [ ] Microphone (optional, for speech features)

### Step 1: Get the Application

**Option A: Clone from GitHub**
```bash
git clone https://github.com/ccmanuelf/ai-language-tutor-app.git
cd ai-language-tutor-app
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in that directory

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

**Create your `.env` file:**

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim .env, or code .env
```

**Required Configuration:**

```bash
# ==========================================
# ADMIN CREDENTIALS (Required)
# ==========================================

# Your admin email - this is YOUR email for managing the system
ADMIN_EMAIL=your.email@example.com

# Your admin username - how you'll be identified
ADMIN_USERNAME=Your Name

# Your admin password - CHOOSE A STRONG PASSWORD!
# Requirements: At least 8 characters
ADMIN_PASSWORD=YourSecurePassword123!

# ==========================================
# AI SERVICE CONFIGURATION (Required)
# ==========================================

# Anthropic Claude API Key
# Get yours at: https://console.anthropic.com
# This is the MINIMUM required for the app to work
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# ==========================================
# OPTIONAL BUT RECOMMENDED
# ==========================================

# Speech Services (Built-in)
# Mistral STT: Speech-to-text using your Mistral API key (already configured above)
# Piper TTS: High-quality text-to-speech (runs locally, no API key needed)
# No additional configuration required!

# Additional AI Providers (for variety and redundancy)
MISTRAL_API_KEY=your-mistral-key
DEEPSEEK_API_KEY=sk-your-deepseek-key

# ==========================================
# FEATURE FLAGS
# ==========================================

# Enable visual learning (image generation)
ENABLE_VISUAL_LEARNING=true

# Enable budget tracking and limits
ENABLE_BUDGET_MANAGEMENT=true

# Enable progress analytics
ENABLE_PROGRESS_TRACKING=true
```

### Step 4: Initialize the Database

```bash
# Run database migrations
alembic upgrade head

# The system will automatically create the admin user
# on first startup using your ADMIN_EMAIL and ADMIN_PASSWORD
```

### Step 5: Start the Application

**Open TWO terminal windows:**

**Terminal 1 - Backend:**
```bash
cd ai-language-tutor-app
source venv/bin/activate  # If using venv
python run_backend.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
cd ai-language-tutor-app
source venv/bin/activate  # If using venv
python run_frontend.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000
```

### Step 6: Verify Setup

1. Open browser to `http://localhost:3000`
2. You should see the AI Language Tutor homepage
3. Click **"Admin Dashboard"** in navigation
4. Log in with your ADMIN_EMAIL and ADMIN_PASSWORD
5. You should see the admin dashboard!

---

## 👥 Creating User Accounts

### Method 1: Via Admin Dashboard (Recommended)

**Access Dashboard:**
1. Navigate to `http://localhost:3000`
2. Click "Admin Dashboard"
3. Log in with admin credentials

**Create User:**
1. In sidebar, click **"User Management"**
2. Click **"Create New User"** button
3. Fill in the form:

```
Username: Sofia
Email: sofia@family.local
Password: SafePassword123!
Is Admin: ☐ (leave unchecked for regular users)
```

4. Click **"Create User"**
5. Success message will confirm creation

**Best Practices:**
- Use memorable but secure passwords
- Can use fictional emails (@family.local) or real ones
- Keep admin checkbox unchecked unless creating another admin

### Method 2: Via Command Line

**For advanced users:**

```bash
# Activate Python environment
source venv/bin/activate

# Run Python interactively
python

# Execute:
```

```python
from app.database.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Create password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create new user
db = SessionLocal()
new_user = User(
    username="Sofia",
    email="sofia@family.local",
    hashed_password=pwd_context.hash("SafePassword123!"),
    is_admin=False
)

db.add(new_user)
db.commit()
print(f"Created user: {new_user.username} (ID: {new_user.user_id})")
db.close()
```

---

## 🔧 Managing Users

### Viewing All Users

**In Admin Dashboard:**
1. Navigate to "User Management"
2. See table with all users:
   - User ID
   - Username
   - Email
   - Admin Status
   - Registration Date
   - Last Login

### Editing User Details

**Update Username or Email:**
1. Click "Edit" button next to user
2. Modify fields
3. Click "Save Changes"

**Reset Password:**
1. Click "Reset Password" for user
2. Enter new password
3. Confirm change
4. Notify user of new password

### Changing Admin Status

**Promote to Admin:**
1. Edit user
2. Check "Is Admin" checkbox
3. Save changes
4. User gains admin dashboard access

**Demote from Admin:**
1. Edit admin user
2. Uncheck "Is Admin"
3. Save changes
4. User loses admin privileges

### Deactivating Users

**Temporarily Disable:**
1. Edit user
2. Set "Active" to false
3. User cannot log in but data preserved

**Permanently Delete:**
1. Click "Delete" button
2. Confirm deletion
3. **WARNING**: All user data and progress will be lost!

---

## 💰 Budget Management

### Setting Up Budgets

**Global Budget (All Users):**
1. Admin Dashboard → "Budget Management"
2. Click "Set Global Budget"
3. Enter monthly limit (e.g., $50.00)
4. Set alert thresholds (e.g., 80%, 95%)
5. Save

**Per-User Budgets:**
1. Budget Management → "User Budgets"
2. Select user from dropdown
3. Set monthly limit
4. Configure alerts
5. Save

**Example Family Budget:**
```
Global Monthly Budget: $100.00
├── Mom (Admin): $30.00
├── Sofia: $25.00
├── Lucas: $25.00
└── Maria: $20.00
```

### Monitoring Usage

**Real-Time Dashboard:**
- Current month spending
- Per-user breakdown
- Cost by AI provider
- Cost by feature (conversation, speech, images)

**Usage Reports:**
1. Budget Management → "Reports"
2. Select date range
3. Export to CSV for detailed analysis

**Cost-Saving Tips:**
- Text conversations are cheaper than speech
- Image generation uses more credits
- Claude is premium; Mistral is economical
- Set per-user limits for kids

---

## 📊 System Monitoring

### Health Checks

**Backend Status:**
```bash
# Check if backend is running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_services": "available"
}
```

**Frontend Status:**
- Visit `http://localhost:3000`
- Page should load within 2 seconds

### Log Files

**Backend Logs:**
- Location: `logs/backend.log`
- Contains: API calls, errors, user actions

**Frontend Logs:**
- Location: `logs/frontend.log`
- Contains: UI events, rendering issues

**View Recent Logs:**
```bash
# Last 50 lines of backend log
tail -50 logs/backend.log

# Follow logs in real-time
tail -f logs/backend.log
```

### Database Maintenance

**Backup Database:**
```bash
# SQLite database backup
cp data/ai_language_tutor.db data/backups/ai_tutor_$(date +%Y%m%d).db
```

**Check Database Size:**
```bash
du -h data/ai_language_tutor.db
```

**Vacuum Database (optimize):**
```bash
sqlite3 data/ai_language_tutor.db "VACUUM;"
```

---

## 🛡️ Security Best Practices

### Passwords

✅ **DO:**
- Use unique, strong passwords for each user
- Change admin password regularly
- Use password manager to store credentials

❌ **DON'T:**
- Share admin password with regular users
- Use same password for multiple accounts
- Write passwords in plain text files

### API Keys

✅ **DO:**
- Keep `.env` file private
- Rotate API keys periodically
- Monitor API usage for anomalies
- Set budget limits to prevent overcharges

❌ **DON'T:**
- Commit `.env` to git (it's in .gitignore)
- Share API keys publicly
- Use API keys in frontend code

### User Privacy

✅ **DO:**
- Respect user conversation privacy
- Secure database with file permissions
- Use HTTPS in production deployment

❌ **DON'T:**
- Read user conversations without permission
- Share user data with third parties
- Deploy without SSL/TLS in production

---

## 📅 Recommended Maintenance Schedule

### Daily
- Monitor system is running
- Check for user-reported issues

### Weekly
- Review budget usage
- Check logs for errors
- Backup database

### Monthly
- Review user activity
- Rotate API keys (if policy requires)
- Update dependencies: `pip install --upgrade -r requirements.txt`

### Quarterly
- Review and update user accounts
- Analyze learning progress reports
- Update application (check GitHub for updates)

---

## 🎯 Example: Setting Up Your Family

### Family Profile
- **You (Mom)**: Admin, learning Italian
- **Sofia (12)**: Learning Spanish for school
- **Lucas (10)**: Learning French (interested in Paris)
- **Maria (Wife)**: Learning German for work

### Setup Process

**1. Create .env file:**
```bash
ADMIN_EMAIL=mom@family.com
ADMIN_USERNAME=Mom
ADMIN_PASSWORD=SecurePassword123!
ANTHROPIC_API_KEY=sk-ant-...
ENABLE_BUDGET_MANAGEMENT=true
```

**2. Start application and create users:**

| User | Email | Password | Budget | Goal |
|------|-------|----------|--------|------|
| Sofia | sofia@family.local | Sofia2024! | $25/mo | Spanish A1 |
| Lucas | lucas@family.local | Lucas2024! | $25/mo | French A1 |
| Maria | maria@family.local | Maria2024! | $30/mo | German B1 |

**3. Configure budgets:**
- Global: $100/month
- Alert at 80% ($80)
- Individual limits as shown above

**4. Set learning preferences:**
- Each user logs in first time
- Sets their target language
- Selects proficiency level
- Chooses preferred scenarios

**5. Weekly family practice:**
- Monday: Sofia's Spanish restaurant scenario
- Wednesday: Lucas's French direction scenarios
- Friday: Maria's German business calls
- Weekend: Free practice for all

---

## ❓ Troubleshooting

### Cannot Create Admin User

**Symptom**: Admin user not created on startup

**Check:**
```bash
# Verify .env has required variables
grep "ADMIN_EMAIL" .env
grep "ADMIN_PASSWORD" .env
```

**Solution:**
- Ensure .env file exists in root directory
- Check both ADMIN_EMAIL and ADMIN_PASSWORD are set
- Restart backend: `python run_backend.py`

### User Cannot Log In

**Check:**
1. User exists in database
2. Password is correct (try resetting)
3. User is marked as "active"
4. No typos in email address

**Reset Password:**
```python
# In Python console
from app.database.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
user = db.query(User).filter(User.email == "sofia@family.local").first()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user.hashed_password = pwd_context.hash("NewPassword123!")
db.commit()
```

### Budget Warnings Not Working

**Check:**
1. `ENABLE_BUDGET_MANAGEMENT=true` in .env
2. Email settings configured (for email alerts)
3. Thresholds set correctly in dashboard

---

## 🚀 Next Steps

1. ✅ Complete initial setup
2. ✅ Create family user accounts
3. ✅ Configure budgets
4. ✅ Have each user set their preferences
5. ✅ Start first conversation!
6. 📖 Read `USER_GUIDE.md` for learning tips
7. 🌟 Enjoy your family's language learning journey!

---

**Questions or Issues?**
- Check `docs/USER_GUIDE.md` for user-facing help
- Review `docs/DEPLOYMENT_READINESS_ASSESSMENT.md` for advanced setup
- Check GitHub Issues for known problems
- Consult logs for detailed error messages

**Happy Teaching! 👨‍🏫👩‍🏫**
