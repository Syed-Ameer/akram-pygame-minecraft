# PyCraft Web Edition - Browser Playable Version

## 🌐 Play in Browser

This converts PyCraft to run directly in your web browser using Pygbag!

## 📦 What I've Set Up

1. **main.py** - Simplified menu system compatible with web browsers
2. **pygbag.toml** - Build configuration
3. **GitHub Actions** - Automatic deployment to GitHub Pages

## 🚀 How to Deploy

### Step 1: Enable GitHub Pages
1. Go to your GitHub repository settings
2. Navigate to **Pages** (left sidebar)
3. Under **Source**, select **GitHub Actions**
4. Save

### Step 2: Push to GitHub
```bash
git add main.py pygbag.toml .github/
git commit -m "Add Pygbag web version"
git push origin feature-texture-v1
```

### Step 3: Wait for Build
- Go to **Actions** tab in GitHub
- Watch the "Build and Deploy Pygbag" workflow
- Takes ~2-5 minutes

### Step 4: Play!
Your game will be live at:
```
https://syed-ameer.github.io/akram-pygame-minecraft/
```

## 📝 Current Status

✅ **Working:**
- Basic game menu
- Keyboard controls
- Web compatibility
- Auto-deployment

⏳ **Next Steps (Optional):**
- Convert full Alpha v1.0 game to async
- Optimize textures for web loading
- Add actual gameplay (currently menu only)

## 🎮 Local Testing

Test the web version locally:
```bash
# Install pygbag
pip install pygbag

# Build and run
pygbag .

# Opens at http://localhost:8000
```

## ⚠️ Important Notes

**The full 25,000+ line game needs conversion:**
- Replace blocking `while running:` with async loops
- Add `await asyncio.sleep(0)` in main loops  
- Minimize large asset files
- Some features may need workarounds

**What Works Now:**
- Menu navigation (arrow keys + Enter)
- Basic pygame window
- Browser compatibility

**What's Next:**
- Convert one complete game version (Classic 1 or Alpha 1) to async
- Add actual gameplay mechanics
- Optimize for web performance

## 🔧 Troubleshooting

**Build fails?**
- Check GitHub Actions log
- Ensure main.py has no blocking operations
- Verify all imports are web-compatible

**Game doesn't load?**
- Check browser console (F12)
- Large textures/sounds slow loading
- Some Pygame features don't work in browser

## 📚 Resources

- [Pygbag Docs](https://pygame-web.github.io/)
- [Pygame Web Limitations](https://pygame-web.github.io/wiki/pygame/)
- [AsyncIO Tutorial](https://docs.python.org/3/library/asyncio.html)
