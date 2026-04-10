#!/usr/bin/env bash
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit
#
# MiniMax Music Generation CLI (pure bash)
#
# Supported models:
#   music-2.5         Song generation with lyrics (default)
#   music-2.6         Enhanced song generation (lyrics required)
#   music-cover        Audio cover / style transfer (requires reference audio)
#   lyrics_generation  Standalone lyrics generation
#
# Usage:
#   bash scripts/music/generate_music.sh --lyrics "[verse]\nHello world" -o output/song.mp3 --download
#   bash scripts/music/generate_music.sh --model music-2.6 --lyrics "[verse]\nStars" -o song.mp3 --download
#   bash scripts/music/generate_music.sh --model music-cover --prompt "pop cover" --reference /path/to/audio.mp3 -o cover.mp3 --download
#   bash scripts/music/generate_music.sh --model lyrics_generation --prompt "a cheerful summer day" -o lyrics.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source shared common functions
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

# ============================================================================
# Main
# ============================================================================

main() {
  load_env
  check_api_key

  local lyrics="" prompt="" model="music-2.5" instrumental=false
  local reference="" target_vocals="" language="" mode=""
  local genre="" mood="" tempo="" bpm="" key="" instruments="" vocals=""
  local use_case="" structure="" avoid="" references=""
  local output="" output_format="url" stream=false download=false
  local sample_rate="" bitrate="" format="" aigc_watermark=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lyrics) lyrics="$2"; shift 2 ;;
      --prompt) prompt="$2"; shift 2 ;;
      --model) model="$2"; shift 2 ;;
      --instrumental) instrumental=true; shift ;;
      --genre) genre="$2"; shift 2 ;;
      --mood) mood="$2"; shift 2 ;;
      --tempo) tempo="$2"; shift 2 ;;
      --bpm) bpm="$2"; shift 2 ;;
      --key) key="$2"; shift 2 ;;
      --instruments) instruments="$2"; shift 2 ;;
      --vocals) vocals="$2"; shift 2 ;;
      --use-case) use_case="$2"; shift 2 ;;
      --structure) structure="$2"; shift 2 ;;
      --avoid) avoid="$2"; shift 2 ;;
      --references) references="$2"; shift 2 ;;
      --reference) reference="$2"; shift 2 ;;
      --target-vocals) target_vocals="$2"; shift 2 ;;
      --language) language="$2"; shift 2 ;;
      --mode) mode="$2"; shift 2 ;;
      -o|--output) output="$2"; shift 2 ;;
      --output-format) output_format="$2"; shift 2 ;;
      --stream) stream=true; shift ;;
      --download) download=true; shift ;;
      --sample-rate) sample_rate="$2"; shift 2 ;;
      --bitrate) bitrate="$2"; shift 2 ;;
      --format) format="$2"; shift 2 ;;
      --aigc-watermark) aigc_watermark="$2"; shift 2 ;;
      -h|--help)
        cat <<'USAGE'
MiniMax Music Generation CLI

Usage:
  generate_music.sh [options]

Options:
  --lyrics TEXT        Song lyrics (with [verse]/[chorus] tags)
  --prompt TEXT        Music style/description prompt
  --instrumental       Generate instrumental (no vocals)
  --model MODEL        Model name (default: music-2.5)
                       Choices: music-2.5, music-2.6, music-cover, lyrics_generation
  --genre TEXT         Genre (e.g. pop, rock, jazz)
  --mood TEXT          Mood (e.g. happy, melancholic)
  --tempo TEXT         Tempo description (e.g. fast, slow)
  --bpm NUMBER         Beats per minute
  --key TEXT           Musical key (e.g. C major, A minor)
  --instruments TEXT   Instruments to include
  --vocals TEXT        Vocal style description
  --use-case TEXT      Use case (e.g. background, theme song)
  --structure TEXT     Song structure
  --avoid TEXT         Elements to avoid
  --references TEXT    Reference tracks/artists
  --reference PATH     Reference audio file path (for music-cover)
  --target-vocals TEXT Target vocal description (for music-cover)
  --language TEXT       Lyrics language (for lyrics_generation)
  --mode TEXT          Generation mode (for lyrics_generation)
  --output-format FMT  Output format: url (default), hex, or lyrics
  --download           Download audio file (for url format)
  --sample-rate N      Audio sample rate
  --bitrate N          Audio bitrate
  --format FMT         Audio format (mp3, wav, etc.)
  -o, --output FILE    Output file path (required)

Models:
  music-2.5         Song generation — needs --lyrics or --instrumental
  music-2.6         Enhanced song generation — --lyrics is required
  music-cover        Audio cover / style transfer — needs --reference
  lyrics_generation  Standalone lyrics generation — outputs text (use --output-format lyrics)

Examples:
  # Song with lyrics (music-2.5 default)
  generate_music.sh --lyrics "[verse]\nHello world" -o song.mp3 --download

  # Music-2.6 (enhanced, lyrics required)
  generate_music.sh --model music-2.6 --lyrics "[verse]\nStars" -o song26.mp3 --download

  # Cover / style transfer (music-cover)
  generate_music.sh --model music-cover --prompt "pop cover" --reference input.mp3 -o cover.mp3 --download

  # Standalone lyrics generation
  generate_music.sh --model lyrics_generation --prompt "a cheerful summer day" -o lyrics.txt --output-format lyrics

  # Instrumental
  generate_music.sh --instrumental --prompt "ambient electronic" -o ambient.mp3 --download
USAGE
        exit 0
        ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  # lyrics_generation model — no audio output, skip output validation
  if [[ "$model" != "lyrics_generation" ]]; then
    if [[ -z "$output" ]]; then
      echo "Error: --output / -o is required" >&2
      exit 1
    fi
    if ! validate_output_path "$output"; then
      exit 1
    fi
  fi

  # lyrics_generation always uses lyrics output format
  if [[ "$model" == "lyrics_generation" ]]; then
    output_format="lyrics"
  fi

  # Build prompt from structured fields
  local field_parts=()
  [[ -n "$genre" ]] && field_parts+=("Genre: $genre")
  [[ -n "$mood" ]] && field_parts+=("Mood: $mood")
  [[ -n "$tempo" ]] && field_parts+=("Tempo: $tempo")
  [[ -n "$bpm" ]] && field_parts+=("BPM: $bpm")
  [[ -n "$key" ]] && field_parts+=("Key: $key")
  [[ -n "$instruments" ]] && field_parts+=("Instruments: $instruments")
  [[ -n "$vocals" ]] && field_parts+=("Vocals: $vocals")
  [[ -n "$use_case" ]] && field_parts+=("Use case: $use_case")
  [[ -n "$structure" ]] && field_parts+=("Structure: $structure")
  [[ -n "$avoid" ]] && field_parts+=("Avoid: $avoid")
  [[ -n "$references" ]] && field_parts+=("References: $references")

  local field_prompt=""
  if [[ ${#field_parts[@]} -gt 0 ]]; then
    field_prompt="$(IFS=' '; echo "${field_parts[*]}")"
  fi

  if [[ -n "$field_prompt" ]]; then
    if [[ -n "$prompt" ]]; then
      prompt="$prompt. $field_prompt"
    else
      prompt="$field_prompt"
    fi
  fi

  # Build base payload
  local payload
  payload=$(jq -n \
    --arg model "$model" \
    --arg prompt "$prompt" \
    --arg of "$output_format" \
    --argjson stream "$stream" \
    '{model: $model, prompt: $prompt, output_format: $of, stream: $stream}')

  # ── Model-specific payload assembly ───────────────────────────────────────
  case "$model" in

    lyrics_generation)
      # Standalone lyrics generation via /v1/lyrics_generation
      # Endpoint: https://api.minimaxi.com/v1/lyrics_generation
      local lyrics_mode="${mode:-write_full_song}"
      payload=$(echo "$payload" | jq --arg lm "$lyrics_mode" '. + {mode: $lm}')
      ;;

    music-cover)
      # Cover / style transfer — needs reference audio, no lyrics needed
      if [[ -z "$reference" ]]; then
        echo "Error: --reference is required for music-cover model" >&2
        exit 1
      fi
      if ! validate_input_path "$reference"; then
        exit 1
      fi
      local audio_b64
      audio_b64="$(base64 -b 0 "$reference" 2>/dev/null)" || {
        echo "Error: failed to read reference file: $reference" >&2
        exit 1
      }
      payload=$(echo "$payload" | jq --arg ab "$audio_b64" '. + {audio_base64: $ab}')
      [[ -n "$target_vocals" ]] && payload=$(echo "$payload" | jq --arg tv "$target_vocals" '. + {target_vocals: $tv}')
      ;;

    music-2.6)
      # music-2.6 requires lyrics — no instrumental workaround
      if $instrumental; then
        payload=$(echo "$payload" | jq '.lyrics = "[intro] [outro]"')
        prompt="${prompt}. pure music, no lyrics"
        payload=$(echo "$payload" | jq --arg p "$prompt" '.prompt = $p')
      elif [[ -z "$lyrics" ]]; then
        echo "Error: --lyrics is required for music-2.6 (use --instrumental for pure music)" >&2
        exit 1
      else
        payload=$(echo "$payload" | jq --arg l "$lyrics" '. + {lyrics: $l}')
      fi
      [[ -n "$sample_rate" ]] && payload=$(echo "$payload" | jq --argjson sr "$sample_rate" '. + {sample_rate: $sr}')
      [[ -n "$bitrate" ]] && payload=$(echo "$payload" | jq --argjson br "$bitrate" '. + {bitrate: $br}')
      [[ -n "$format" ]] && payload=$(echo "$payload" | jq --arg f "$format" '. + {format: $f}')
      ;;

    *)
      # music-2.5 and other models
      if $instrumental; then
        payload=$(echo "$payload" | jq '. + {lyrics: "[intro] [outro]"}')
        prompt="${prompt}. pure music, no lyrics"
        payload=$(echo "$payload" | jq --arg p "$prompt" '.prompt = $p')
      elif [[ -z "$lyrics" ]]; then
        echo "Error: --lyrics is required for non-instrumental music (use --instrumental for pure music)" >&2
        exit 1
      else
        payload=$(echo "$payload" | jq --arg l "$lyrics" '. + {lyrics: $l}')
      fi
      ;;
  esac

  # Audio settings (not applicable to lyrics_generation)
  if [[ "$model" != "lyrics_generation" && "$model" != "music-2.6" ]]; then
    local audio_setting="{}"
    [[ -n "$sample_rate" ]] && audio_setting=$(echo "$audio_setting" | jq --argjson sr "$sample_rate" '. + {sample_rate: $sr}')
    [[ -n "$bitrate" ]] && audio_setting=$(echo "$audio_setting" | jq --argjson br "$bitrate" '. + {bitrate: $br}')
    [[ -n "$format" ]] && audio_setting=$(echo "$audio_setting" | jq --arg f "$format" '. + {format: $f}')
    if [[ "$audio_setting" != "{}" ]]; then
      payload=$(echo "$payload" | jq --argjson as "$audio_setting" '. + {audio_setting: $as}')
    fi
  fi

  [[ -n "$aigc_watermark" ]] && payload=$(echo "$payload" | jq --argjson aw "$aigc_watermark" '. + {aigc_watermark: $aw}')

  local api_host="${MINIMAX_API_HOST:-https://api.minimaxi.com}"
  # lyrics_generation has its own endpoint; all music models share /v1/music_generation
  local api_path="music_generation"
  [[ "$model" == "lyrics_generation" ]] && api_path="lyrics_generation"
  local api_url="${api_host}/v1/${api_path}"

  echo "Generating music with model: $model"
  if [[ "$model" == "lyrics_generation" ]]; then
    echo "Output: lyrics text"
  else
    echo "Output format: $output_format"
  fi

  # Send request via curl
  local raw_output http_code response
  raw_output="$(curl -s -w "\n%{http_code}" \
    -X POST "$api_url" \
    -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
    -H "Content-Type: application/json" \
    --max-time 300 \
    -d "$payload" 2>/dev/null)" || {
    echo "Error: curl request failed" >&2
    exit 1
  }

  http_code="${raw_output##*$'\n'}"
  response="${raw_output%$'\n'*}"

  if [[ "$http_code" -ge 400 ]] 2>/dev/null; then
    echo "Error: API returned HTTP $http_code" >&2
    echo "$response" >&2
    exit 1
  fi

  local status_code
  status_code="$(echo "$response" | jq -r '(.base_resp.status_code // 0)')" || status_code=0
  if [[ "$status_code" != "0" ]]; then
    echo "API error: $(echo "$response" | jq '.base_resp')" >&2
    exit 1
  fi

  if [[ "$model" == "lyrics_generation" ]]; then
    local lyrics_text song_title style_tags
    lyrics_text="$(echo "$response" | jq -r '.data.lyrics // .lyrics // empty' 2>/dev/null)" || lyrics_text=""
    song_title="$(echo "$response" | jq -r '.data.song_title // .song_title // empty' 2>/dev/null)" || song_title=""
    style_tags="$(echo "$response" | jq -r '.data.style_tags // .style_tags // empty' 2>/dev/null)" || style_tags=""
    if [[ -z "$lyrics_text" || "$lyrics_text" == "null" ]]; then
      echo "Error: No lyrics in response." >&2
      echo "$response" | jq . >&2
      exit 1
    fi
    # Print metadata to stderr (not stdout) so toolkit.py can capture clean lyrics
    [[ -n "$song_title" && "$song_title" != "null" ]] && echo "Title: $song_title" >&2
    [[ -n "$style_tags" && "$style_tags" != "null" ]] && echo "Style: $style_tags" >&2
    # Always write to output file when set, print path to stdout
    if [[ -n "$output" ]]; then
      echo "$lyrics_text" > "$output"
      echo "OUTPUT_PATH: $output"
    else
      echo "$lyrics_text"
    fi
    return 0
  fi

  mkdir -p "$(dirname "$output")"

  if [[ "$output_format" == "hex" ]]; then
    local audio_hex
    audio_hex="$(echo "$response" | jq -r '.data.audio // empty' 2>/dev/null)" || audio_hex=""
    if [[ -z "$audio_hex" ]]; then
      echo "Error: No audio hex data in response." >&2
      exit 1
    fi
    echo "$audio_hex" | xxd -r -p > "$output"
    echo "Audio saved to: $output"

  elif [[ "$output_format" == "url" ]]; then
    local audio_url
    audio_url="$(echo "$response" | jq -r '.data.audio_url // .data.audio // .data.audio_file.download_url // empty' 2>/dev/null)" || audio_url=""
    if [[ -z "$audio_url" ]]; then
      echo "Error: No audio URL in response." >&2
      echo "$response" | jq . >&2
      exit 1
    fi
    echo "Audio URL: $audio_url" >&2
    if $download; then
      curl -s -o "$output" --max-time 120 "$audio_url"
      echo "OUTPUT_PATH: $output"
    else
      echo "Use --download to save the file." >&2
      echo "$audio_url" > "$output"
      echo "OUTPUT_PATH: $output"
    fi
  fi

  # Print extra info if present
  local extra
  extra="$(echo "$response" | jq -r '.extra_info // .data.extra_info // empty')" 2>/dev/null || true
  if [[ -n "$extra" && "$extra" != "null" ]]; then
    echo "Extra info: $extra"
  fi
}

main "$@"
