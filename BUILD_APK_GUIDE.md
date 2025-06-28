# 📱 Complete APK Build Guide

This guide shows you **3 different methods** to build your Snake Game APK from GitHub.

## 🚀 Method 1: GitHub Actions (Easiest - Recommended)

### Steps:
1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add APK build workflow"
   git push origin main
   ```

2. **Trigger the build:**
   - Go to your GitHub repository
   - Click "Actions" tab
   - Click "Build APK" workflow
   - Click "Run workflow" → "Run workflow"

3. **Download your APK:**
   - Wait 20-45 minutes for build to complete
   - Go to Actions → Click on your build
   - Scroll down to "Artifacts"
   - Download "snake-game-apk"
   - Extract the ZIP to get your APK!

**✅ Pros:** No setup required, builds automatically
**❌ Cons:** Takes 20-45 minutes, limited monthly build minutes

---

## 🖥️ Method 2: Local Build on Ubuntu/Linux

### Prerequisites:
```bash
# Install Ubuntu (Windows users: use WSL2)
# OR use a Linux VM
# OR use a Linux cloud server
```

### Step-by-Step:
1. **Clone your repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv git zip unzip
   sudo apt install -y openjdk-8-jdk build-essential libssl-dev libffi-dev python3-dev
   sudo apt install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm
   sudo apt install -y libncurses5-dev libncursesw5-dev xz-utils tk-dev
   
   # Set Java path
   export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
   echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
   ```

3. **Setup Python environment:**
   ```bash
   python3 -m venv snake_env
   source snake_env/bin/activate
   pip install --upgrade pip
   pip install cython==0.29.33
   pip install -r requirements.txt
   ```

4. **Build the APK:**
   ```bash
   buildozer android debug
   ```

5. **Find your APK:**
   ```bash
   ls bin/
   # Your APK: advancedsnake-1.0-armeabi-v7a-debug.apk
   ```

**✅ Pros:** Fast builds after setup, full control
**❌ Cons:** Requires Linux setup

---

## ☁️ Method 3: Google Colab (Free Cloud Build)

### Steps:
1. **Go to [Google Colab](https://colab.research.google.com/)**

2. **Create new notebook and run these cells:**

**Cell 1 - Setup:**
```python
!apt update
!apt install -y openjdk-8-jdk build-essential libssl-dev libffi-dev python3-dev
!apt install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm
!apt install -y libncurses5-dev libncursesw5-dev xz-utils tk-dev

import os
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
```

**Cell 2 - Clone and Install:**
```python
!git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
%cd YOUR_REPO_NAME
!pip install cython==0.29.33
!pip install -r requirements.txt
```

**Cell 3 - Build APK:**
```python
!buildozer android debug
```

**Cell 4 - Download APK:**
```python
from google.colab import files
import os

# Find the APK file
apk_files = [f for f in os.listdir('bin/') if f.endswith('.apk')]
if apk_files:
    files.download(f'bin/{apk_files[0]}')
    print(f"✅ APK ready: {apk_files[0]}")
else:
    print("❌ No APK found")
```

**✅ Pros:** Free, no local setup, decent speed
**❌ Cons:** Need Google account, session timeout

---

## 🔧 Common Issues & Solutions

### Issue: "Command 'buildozer' not found"
**Solution:**
```bash
pip install --upgrade buildozer
```

### Issue: "Java not found"
**Solution:**
```bash
sudo apt install openjdk-8-jdk
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

### Issue: "NDK download failed"
**Solution:** Edit `buildozer.spec`:
```ini
[android]
ndk = 23b
```

### Issue: "Build failed with gradle error"
**Solution:** Clear cache:
```bash
buildozer android clean
buildozer android debug
```

## 📱 Testing Your APK

1. **Enable Developer Options** on Android phone
2. **Enable USB Debugging**
3. **Install APK:**
   ```bash
   adb install bin/your-app.apk
   ```
   OR transfer APK to phone and install manually

## 🚀 Publishing to Google Play Store

1. **Build release APK:**
   ```bash
   buildozer android release
   ```

2. **Sign your APK** (required for Play Store)

3. **Create Google Play Console account** ($25 one-time fee)

4. **Upload and publish!**

---

## ⚡ Quick Commands Reference

```bash
# Build debug APK
buildozer android debug

# Build release APK  
buildozer android release

# Clean build cache
buildozer android clean

# Update buildozer
pip install --upgrade buildozer

# Check buildozer status
buildozer android logcat
```

## 🎯 Expected Build Times

- **First build:** 20-45 minutes (downloads SDK/NDK)
- **Subsequent builds:** 3-10 minutes
- **Clean builds:** 10-20 minutes

## 💡 Pro Tips

1. **Use Method 1 (GitHub Actions)** for easiest setup
2. **Use Method 2 (Local)** for fastest iteration
3. **Use Method 3 (Colab)** if you can't install Linux
4. **Always test APK** on real device before publishing
5. **Keep your AdMob IDs secure** (already configured!)

---

**🎉 Your Snake Game APK will be ready to earn money on Google Play Store!** 