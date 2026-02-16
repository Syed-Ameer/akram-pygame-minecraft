# 🚀 Deploy PyCraft Launcher to Replit

## Quick Deploy Instructions

### Step 1: Import to Replit
1. Go to [replit.com](https://replit.com)
2. Click **"+ Create Repl"**
3. Choose **"Import from GitHub"**
4. Paste URL: `https://github.com/Syed-Ameer/akram-pygame-minecraft`
5. Branch: `feature-texture-v1`
6. Click **"Import from GitHub"**

### Step 2: Configure (Auto-detected)
Replit will automatically detect:
- ✅ Language: Python
- ✅ Run command: `streamlit run launcher.py`
- ✅ Files: `.replit` and `replit.nix` already configured

### Step 3: Install Dependencies
Replit will auto-install from `requirements.txt`:
```bash
# If needed, manually run in Shell:
pip install -r requirements.txt
```

### Step 4: Run!
1. Click the big green **"Run"** button
2. Replit starts Streamlit launcher
3. Opens in right panel or new tab
4. **Your launcher is now live!**

### Step 5: Get Public URL
- Click **"Open website"** icon (top right)
- Copy the URL: `https://your-repl-name.yourusername.repl.co`
- Share this URL globally!

## How It Works on Replit

### When Users Click "🚀 PLAY GAME":
1. Streamlit launcher runs `subprocess.Popen`
2. Game launches on Replit's Linux container
3. **Replit's VNC automatically captures the game window**
4. Game displays in Replit's viewer panel
5. User sees and plays the game!

### What Replit Provides:
- ✅ Virtual display (Xvfb) - built-in
- ✅ VNC server - built-in
- ✅ Web viewer - built-in
- ✅ Public URL - automatic
- ✅ GUI support - automatic

**You don't need to configure VNC - Replit handles it!**

## Features That Work on Replit

✅ All game versions launch
✅ Meme of Month with reactions
✅ Account system (saves to accounts.json)
✅ Play count tracking
✅ DLC toggle
✅ Auto-launch feature
✅ Game window display

## Limitations

⚠️ **Free tier limits:**
- Repl goes to sleep after inactivity
- Wakes up when URL visited
- Limited CPU/RAM (fine for 2D games)

⚠️ **Multiple users:**
- Only ONE game can run at a time per Repl
- If user A launches game, user B must wait
- Consider forking for multiple instances

## Tips

### Keep Repl Awake (Optional):
Use UptimeRobot or similar to ping your URL every 5 minutes

### Performance:
- 2D Minecraft clones run smoothly
- 3D versions may be slower
- Adjust game settings for cloud performance

### Sharing:
- Share Repl URL directly
- Users don't need Replit accounts to play
- Embed in website with iframe (optional)

## Troubleshooting

**Issue: Games don't display**
- Check Replit's "Console" tab for errors
- Verify Xvfb is running: `ps aux | grep Xvfb`
- Replit should auto-start display

**Issue: Slow loading**
- First run installs packages (slower)
- Subsequent runs are faster
- Free tier has CPU limits

**Issue: Account data lost**
- Free tier may reset filesystem
- Upgrade to Replit Hacker plan for persistence
- Or use external database (Replit DB)

## Success!

Your PyCraft Launcher is now globally accessible! 🎉

**URL Format:**
`https://akram-pygame-minecraft.yourusername.repl.co`

Share this URL and anyone can:
1. Visit your launcher
2. Select game version
3. Click PLAY GAME
4. Play Minecraft in their browser!
