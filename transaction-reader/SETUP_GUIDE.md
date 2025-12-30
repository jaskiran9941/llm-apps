# 🔧 Gmail API Setup Guide

This guide will walk you through setting up Gmail API access for Transaction Reader. **Each user needs to create their own Google Cloud project and OAuth credentials.**

## Why Do I Need This?

To read your Gmail messages, the app needs permission from Google. This is done through OAuth 2.0, which requires:
1. A Google Cloud project
2. Gmail API enabled
3. OAuth 2.0 credentials (credentials.json)

**Note**: Due to Google's policies, each user must create their own credentials. This ensures your data privacy and security.

## Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Sign in with your Google account

3. Click **"Select a project"** dropdown at the top

4. Click **"New Project"**

5. Enter project details:
   - **Project name**: `Transaction Reader` (or any name you prefer)
   - **Organization**: Leave as default
   - Click **"Create"**

6. Wait for the project to be created (takes a few seconds)

7. Make sure your new project is selected in the dropdown

### Step 2: Enable Gmail API

1. In the Google Cloud Console, click the hamburger menu (≡) in the top left

2. Navigate to **"APIs & Services" → "Library"**

3. In the search bar, type `Gmail API`

4. Click on **"Gmail API"** from the results

5. Click the blue **"Enable"** button

6. Wait for it to enable (takes a few seconds)

### Step 3: Configure OAuth Consent Screen

Before creating credentials, you need to configure the OAuth consent screen:

1. Go to **"APIs & Services" → "OAuth consent screen"** (left sidebar)

2. Select **"External"** user type (unless you have a Google Workspace account)

3. Click **"Create"**

4. Fill in the required fields:

   **App information:**
   - **App name**: `Transaction Reader`
   - **User support email**: Your email address

   **App Domain** (optional - you can skip):
   - Leave blank for personal use

   **Developer contact information:**
   - **Email addresses**: Your email address

5. Click **"Save and Continue"**

6. **Scopes** screen:
   - Click **"Add or Remove Scopes"**
   - Search for `gmail.readonly`
   - Check the box for `https://www.googleapis.com/auth/gmail.readonly`
   - Click **"Update"**
   - Click **"Save and Continue"**

7. **Test users** screen:
   - Click **"+ Add Users"**
   - Enter your Gmail address (the one you want to analyze)
   - Add any other Gmail addresses you want to analyze
   - Click **"Add"**
   - Click **"Save and Continue"**

8. **Summary** screen:
   - Review your settings
   - Click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" → "Credentials"** (left sidebar)

2. Click **"+ Create Credentials"** at the top

3. Select **"OAuth client ID"**

4. Choose application type:
   - Select **"Desktop app"** from the dropdown

5. Enter a name:
   - **Name**: `Transaction Reader Desktop` (or any name)

6. Click **"Create"**

7. A dialog will appear with your credentials:
   - Click **"Download JSON"**
   - Save the file

8. **Important**: Rename the downloaded file to `credentials.json`

### Step 5: Place Credentials in Project

1. Move the `credentials.json` file to your project root directory:

```bash
mv ~/Downloads/client_secret_*.json ~/path/to/transaction-reader/credentials.json
```

2. Verify the file is in the correct location:

```bash
ls transaction-reader/
# Should see: credentials.json
```

### Step 6: Add Test Users (Important!)

Since your OAuth consent screen is in "Testing" mode, only test users can access the app.

**To add test users:**

1. Go to **"APIs & Services" → "OAuth consent screen"**

2. Scroll down to **"Test users"** section

3. Click **"+ Add Users"**

4. Enter the Gmail address(es) you want to analyze

5. Click **"Save"**

**Note**: You must add each Gmail account as a test user BEFORE authenticating it in the app.

## 🔐 Publishing Your App (Optional)

If you want anyone to use your app without adding them as test users, you need to publish the OAuth consent screen. However, this requires Google's verification.

### Option A: Keep in Testing Mode (Recommended for Personal Use)

- **Pros**: No verification needed, works immediately
- **Cons**: Only test users can authenticate (max 100 users)
- **Best for**: Personal use or small groups

### Option B: Publish the App

1. Go to **"OAuth consent screen"**
2. Click **"Publish App"**
3. Google will review your app (can take days/weeks)
4. You may need to provide:
   - Privacy policy
   - Terms of service
   - YouTube video demo
   - Verification documents

**Note**: For most personal projects, testing mode is sufficient.

## 🎯 Testing Your Setup

1. Make sure `credentials.json` is in your project root

2. Run the app:
```bash
streamlit run app.py
```

3. Add an account in the app sidebar

4. A browser window should open asking you to:
   - Choose your Google account
   - See a warning "Google hasn't verified this app" - click **"Continue"** (it's your own app!)
   - Grant permissions to "Read your email messages and settings"

5. If successful, you'll see "✓ Added [your-email]" in the app

## ❗ Common Issues

### "Error 400: redirect_uri_mismatch"

**Solution**: Add authorized redirect URI:
1. Go to **"Credentials"**
2. Click on your OAuth client ID
3. Add to "Authorized redirect URIs":
   - `http://localhost:8080/`
4. Click **"Save"**

### "Error 403: access_denied"

**Solution**: Add yourself as a test user:
1. Go to **"OAuth consent screen"**
2. Scroll to **"Test users"**
3. Click **"+ Add Users"**
4. Add your Gmail address
5. Click **"Save"**

### "invalid_client" Error

**Solution**: Your credentials.json is incorrect or corrupt:
1. Go back to **"Credentials"**
2. Delete the old OAuth client ID
3. Create a new one and download fresh credentials

### Port 8080 Already in Use

**Solution**: Either:
- Stop the process using port 8080
- Or change the port in `gmail_helper.py` line 37 (change `port=8080` to another port like `8081`)

## 🔒 Security Best Practices

1. **Never commit credentials.json to Git**
   - It's already in `.gitignore`
   - If accidentally committed, delete the OAuth client and create a new one

2. **Keep token files private**
   - `token_*.json` files store your authentication
   - Also in `.gitignore`

3. **Use read-only scopes**
   - The app only requests `gmail.readonly`
   - It cannot send emails or modify your inbox

4. **Revoke access anytime**
   - Go to https://myaccount.google.com/permissions
   - Find "Transaction Reader"
   - Click "Remove Access"

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Overview](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

## 💬 Still Having Issues?

If you're stuck, please [open an issue](https://github.com/YOUR_USERNAME/transaction-reader/issues) with:
- Screenshots of your setup
- Error messages
- Steps you've tried

We're here to help!
