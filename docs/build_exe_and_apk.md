# SRA Business Lead Finder: Desktop EXE & Android APK Build Guide

This comprehensive guide explains how to convert and package **SRA Business Lead Finder** into a standalone **Windows Desktop Application (`.exe`)** and an **Android Mobile Application (`.apk`)**.

---

## Method 1: Instant App Installation via PWA (Fastest - No Compiling Needed)

The application includes a Progressive Web App (PWA) manifest. This allows users on Android phones and Windows PCs to install it directly as an app with an app icon.

### On Android Mobile:
1. Ensure your phone and development computer are on the same Wi-Fi network.
2. On your computer, run `ipconfig` to find your local IPv4 address (e.g. `192.168.1.15`).
3. On your Android phone, open Google Chrome and navigate to:
   ```
   http://192.168.1.15:3000
   ```
4. Tap the **3-dot menu** in Chrome.
5. Tap **"Install App"** or **"Add to Home Screen"**.
6. An app icon named **"SRA Leads"** will be installed on your phone. It launches fullscreen like a native Android APK!

### On Windows Desktop:
1. Open Google Chrome or Microsoft Edge and navigate to `http://localhost:3000`.
2. Look at the right side of the address bar for the **"Install app"** icon (or 3 dots -> *Apps* -> *Install this site as an app*).
3. Click **Install**.
4. SRA Lead Finder will run in its own dedicated desktop window with a taskbar icon and desktop shortcut!

---

## Method 2: Packaging as Windows Desktop App (`.exe`) using Tauri

[Tauri](https://tauri.app) packages Next.js web applications into ultra-lightweight, native Windows `.exe` installers (typically < 10 MB).

### Prerequisites:
- Microsoft Visual Studio C++ Build Tools installed.
- Rust toolchain (`winget install Rustlang.Rustup` or from [rustup.rs](https://rustup.rs)).

### Steps:
1. Open PowerShell in `d:\scrap_tool\frontend`:
   ```powershell
   cd d:\scrap_tool\frontend
   npm install --save-dev @tauri-apps/cli
   ```
2. Initialize Tauri:
   ```powershell
   npx tauri init
   ```
   - App Name: `SRA Lead Finder`
   - Window Title: `SRA Business Lead Finder`
   - Web assets path: `../out` (or `http://localhost:3000` for development)
   - Dev URL: `http://localhost:3000`

3. Build the Windows installer:
   ```powershell
   npx tauri build
   ```
4. Output `.exe`:
   Located at:
   `d:\scrap_tool\frontend\src-tauri\target\release\bundle\msi\SRA Lead Finder_1.0.0_x64_en-US.msi` and `.exe`.

---

## Method 3: Packaging as Android Native APK (`.apk`) using Capacitor

[Capacitor](https://capacitorjs.com) turns Next.js web apps into native Android Studio projects ready to compile into `.apk`.

### Prerequisites:
- Android Studio installed with Android SDK.

### Steps:
1. Navigate to frontend:
   ```powershell
   cd d:\scrap_tool\frontend
   ```
2. Install Capacitor dependencies:
   ```powershell
   npm install @capacitor/core @capacitor/cli @capacitor/android
   ```
3. Initialize Capacitor:
   ```powershell
   npx cap init "SRA Business Lead Finder" "com.sra.leadfinder" --web-dir "out"
   ```
4. Add the Android native project:
   ```powershell
   npx cap add android
   ```
5. Configure `capacitor.config.json` with your backend server IP:
   ```json
   {
     "appId": "com.sra.leadfinder",
     "appName": "SRA Business Lead Finder",
     "webDir": "out",
     "server": {
       "url": "http://YOUR_SERVER_IP:3000",
       "cleartext": true
     }
   }
   ```
6. Open the project in Android Studio:
   ```powershell
   npx cap open android
   ```
7. In Android Studio:
   - Click **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
   - Once completed, click **Locate** to get your standalone `app-debug.apk` file!
   - Send this `.apk` to any Android phone to install directly!
