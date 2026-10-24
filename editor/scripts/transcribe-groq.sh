#!/usr/bin/env bash
# Transcribe a video/audio file with Groq Whisper (handles Taglish) and
# write a word-level transcript.json that HyperFrames captions can use.
# Usage: GROQ_API_KEY=... scripts/transcribe-groq.sh <video-or-audio> [out.json]
set -euo pipefail

in="${1:?usage: transcribe-groq.sh <video-or-audio> [out.json]}"
out="${2:-transcript.json}"
: "${GROQ_API_KEY:?Set GROQ_API_KEY first (get one at https://console.groq.com/keys)}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Groq's upload limit is 25 MB; mono 16 kHz mp3 keeps ~30+ min under it.
ffmpeg -loglevel error -y -i "$in" -vn -ac 1 -ar 16000 -b:a 64k "$tmp/audio.mp3"

# No language flag on purpose: whisper-large-v3 auto-detects mixed Tagalog/English.
curl -sS --fail-with-body https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F file=@"$tmp/audio.mp3" \
  -F model=whisper-large-v3 \
  -F response_format=verbose_json \
  -F "timestamp_granularities[]=word" \
  -o "$tmp/groq.json"

cp "$tmp/groq.json" "$out"
npx --yes hyperframes@0.8.191 transcribe "$out"
echo "Transcript ready: $out"
