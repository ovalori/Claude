# AI Video Editor Setup (FFmpeg + HyperFrames + Groq)

The 3 tools from the TikTok:

| Tool | What it does | Cost |
|---|---|---|
| **FFmpeg** | Cuts, trims, and mixes video/audio | Free |
| **HyperFrames** (by HeyGen) | Captions, text, and motion graphics written as HTML, rendered to MP4 | Free, open source |
| **Groq** | Fast Whisper transcription that understands Taglish | Free tier |

Claude Code runs all three for you. You describe the edit, and it does the work.

---

## 1. Install on your computer (one time)

### Windows
Open **PowerShell** and run:
```powershell
winget install Gyan.FFmpeg
winget install OpenJS.NodeJS.LTS
```
### Mac
```bash
brew install ffmpeg node
```
Close and reopen the terminal, then check that both are installed:
```bash
ffmpeg -version
node -v      # needs v22 or newer
```

### Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

## 2. Get your Groq API key (free)
1. Go to https://console.groq.com/keys and sign in with Google.
2. Click **Create API Key** and copy it (it starts with `gsk_`).
3. Save it as an environment variable (in a Claude cloud session, add it as a **Network secret** for `api.groq.com` instead):
   - Windows: `setx GROQ_API_KEY "gsk_yourkey"` (then reopen the terminal)
   - Mac: `echo 'export GROQ_API_KEY="gsk_yourkey"' >> ~/.zshrc && source ~/.zshrc`

Keep the key private. Don't post it in screenshots.

## 3. Get this project
```bash
git clone https://github.com/ovalori/Claude.git
cd Claude/editor
npx hyperframes doctor     # FFmpeg and Node should show ✓
```
Whisper-cpp, Kokoro and MusicGen show ✗. That's fine because Groq handles transcription.

## 4. Edit a video
Put your clip in the `editor` folder (for example `raw.mp4`), then:

```bash
# Taglish captions with word-level timing → transcript.json
bash scripts/transcribe-groq.sh raw.mp4
```

Then open Claude Code in the same folder (`claude`) and ask in plain words, for example:

> Using /hyperframes, make a 9:16 TikTok from raw.mp4. Cut the dead air and "uhm"s,
> add bold word-by-word captions from transcript.json (white text, yellow highlight
> on the current word), and add a "The only 3 tools" title card at the start.

Preview and render:
```bash
npm run dev        # preview in the browser
npm run render     # export the MP4
```

## Quick FFmpeg commands
```bash
ffmpeg -i raw.mp4 -ss 00:00:05 -to 00:00:35 -c copy clip.mp4      # trim 0:05–0:35
ffmpeg -i raw.mp4 -vf "crop=ih*9/16:ih" vertical.mp4              # crop landscape to 9:16
ffmpeg -i clip.mp4 -i music.mp3 -filter_complex "[1]volume=0.15[m];[0:a][m]amix=inputs=2:duration=first" -c:v copy mixed.mp4  # add quiet background music
```

## What's in this folder
- `editor/`: HyperFrames project (vertical 1080×1920), with `CLAUDE.md` so Claude Code knows how to use it
- `editor/scripts/transcribe-groq.sh`: video to Groq Whisper to `transcript.json` for captions
