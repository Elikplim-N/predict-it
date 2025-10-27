# 🚀 START HERE

## What is this?

An **ML Competition Platform** for your class where:
- Students upload prediction CSVs
- System calculates RMSE automatically
- Live leaderboard shows rankings
- Students can access from **anywhere** (internet)

---

## 🎯 Two Options

### Option 1: Cloud Hosting (RECOMMENDED) ☁️
**Students access from anywhere on the internet**

```bash
./deploy.sh
```

Then follow the guide in **[DEPLOY_QUICK.md](DEPLOY_QUICK.md)**

**Time:** 10-15 minutes  
**Best for:** Tests lasting hours/days, students not in same location

---

### Option 2: Local Network 📡
**Students must be on same WiFi as you**

```bash
./start.sh
```

Then share your IP address with students.

**Time:** 2 minutes  
**Best for:** In-class tests, all students in same room

See **[QUICK_START.md](QUICK_START.md)** for details

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **DEPLOY_QUICK.md** | Fast cloud deployment (10 min read) |
| **DEPLOYMENT.md** | Complete deployment guide (all platforms) |
| **QUICK_START.md** | Local network setup for test day |
| **README.md** | Full documentation |

---

## ⚡ Quickest Path

1. Run: `./deploy.sh`
2. Push to GitHub
3. Deploy on Railway.app (free account)
4. Set environment variables
5. Share URL with students
6. Done! 🎉

**Total time:** 15 minutes

---

## 🧪 Test Files Included

- `sample_ground_truth.csv` - Upload this as admin
- `sample_prediction.csv` - Test with this as student

---

## 🔐 Default Credentials

**Admin Login:** `/admin/login`
- Username: `admin`
- Password: `admin123`

(Change in `app.py` line 55 before deploying)

---

## 💡 Need Help?

1. **Cloud deployment:** Read [DEPLOY_QUICK.md](DEPLOY_QUICK.md)
2. **Local network:** Read [QUICK_START.md](QUICK_START.md)
3. **Full details:** Read [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Ready?** Run `./deploy.sh` to start! 🚀
