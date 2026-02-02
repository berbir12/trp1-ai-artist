# TRP1 Submission Report

**Candidate:** Bereket  
**Date:** February 2, 2026

---

## Links

- **YouTube Video:** https://youtu.be/HKkxdMyr3Nc
- **GitHub Repository:** https://github.com/berbir12/TRP1

---

## Environment Setup Documentation

### Which APIs did you configure?

- **Google Gemini API** - For Lyria music generation
- **Google Vertex AI Studio** - For Veo 3.1 video generation ($300 free credits)

Setup process:
```bash
cd trp1-ai-artist
uv sync
# Created .env with GEMINI_API_KEY
uv run ai-content list-providers
```

### Any issues encountered during setup?

**Yes - OAuth2 Authentication Error:**

When attempting to generate video programmatically through the Python SDK:
```
401 UNAUTHENTICATED: API keys are not supported by this API.
Expected OAuth2 access token or other authentication credentials.
Method: google.ai.generativelanguage.v1beta.PredictionService.PredictLongRunning
```

**Root Cause:** Veo video generation endpoint requires OAuth2 authentication when called programmatically, while Lyria music generation accepts API keys.

### How did you resolve them?

**Solution: Hybrid Approach**

Instead of setting up complex OAuth2 service accounts, I used **Google Vertex AI Studio web interface** for video generation:

1. Accessed Vertex AI Studio through Google Cloud Console
2. Used the $300 free credits available for new users
3. Generated video through the browser UI with Veo 3.1
4. Downloaded the MP4 file locally
5. Combined it programmatically with Lyria-generated music using MoviePy

This pragmatic workaround let me focus on content creation rather than authentication debugging.

---

## Codebase Understanding

### Architecture diagram or description

```
┌─────────────────────────────────────┐
│         CLI / User Code              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      ProviderRegistry (Singleton)    │
│  ┌────────┐ ┌────────┐ ┌─────────┐  │
│  │ lyria  │ │minimax │ │   veo   │  │
│  │ (music)│ │(music) │ │ (video) │  │
│  └────────┘ └────────┘ └─────────┘  │
└──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Provider Protocol Interface       │
│  (MusicProvider / VideoProvider)     │
└──────────────────────────────────────┘
```

**Package Structure:**
```
src/ai_content/
├── core/          # Protocols, Registry, Result objects
├── providers/     # Google, AIMLAPI, Kling implementations
├── presets/       # Pre-configured style prompts
├── pipelines/     # Orchestration workflows
└── cli/           # Command-line interface
```

### Key insights about the provider system

**1. Registry Pattern with Decorators**
```python
@ProviderRegistry.register_music("lyria")
class GoogleLyriaProvider:
    ...
```
Providers self-register, enabling plugin architecture without modifying core code.

**2. Protocol-Based (Duck Typing)**
No inheritance required - any class implementing the required methods works.

**3. Result Objects over Exceptions**
```python
@dataclass
class GenerationResult:
    success: bool
    provider: str
    file_path: Path | None
    error: str | None
```
Explicit success/failure handling makes multi-provider workflows easier.

**4. Async-First**
All I/O operations are non-blocking for concurrent provider calls.

### How the pipeline orchestration works

**Single Provider Flow:**
```
User CLI → Registry.get_provider("lyria") → Provider.generate() → GenerationResult
```

**Multi-Provider Pipeline (future):**
```
1. Archive.org search → metadata
2. Parallel generation:
   - Lyria → music
   - Veo → video
3. FFmpeg merge → final music video
4. YouTube upload
```

Currently, orchestration is manual - you run separate commands and combine outputs with custom scripts.

---

## Generation Log

### Commands executed

**Music Generation (Lyria):**
```bash
uv run ai-content music \
  --prompt "Ethiopian jazz fusion with kirar, masenqo, smooth walking bass" \
  --provider lyria \
  --bpm 85 \
  --duration 8
```

**Video Generation (Vertex AI Studio - Web UI):**
- Opened Vertex AI Studio → Generative AI → Veo
- Input prompt: "Cinematic view of Simien Mountain landscapes with dramatic clouds and golden hour lighting, nature documentary style"
- Settings: 8 seconds, 1080p, 16:9, Veo 3.1 Preview
- Downloaded as `simien_mountain_cinematic_view.mp4`

**Audio-Video Combination:**
```bash
python scripts/09_combine_music_video.py \
  --video exports/simien_mountain_cinematic_view.mp4 \
  --audio exports/ethio_jazz_instrumental.wav \
  --output exports/music_video_ethiopian_mountains.mp4
```

### Prompts used and why

**Music Prompt:**
> "Ethiopian jazz fusion with kirar, masenqo, smooth walking bass"

**Why:** Combined traditional Ethiopian instruments (kirar, masenqo) with jazz elements to create authentic cultural fusion matching the Simien Mountains theme.

**Video Prompt:**
> "Cinematic view of Simien Mountain landscapes with dramatic clouds and golden hour lighting, nature documentary style"

**Why:** 
- "Cinematic" + "nature documentary style" = professional quality
- "Golden hour lighting" = warm, beautiful tones
- "Dramatic clouds" = visual interest and movement
- Specific location ensures cultural accuracy

### Results achieved

| Artifact | Details |
|----------|---------|
| **Music** | `ethio_jazz_instrumental.wav` |
| | Duration: 8 seconds |
| | File size: ~1.2 MB |
| | Generation time: ~15 seconds |
| **Video** | `simien_mountain_cinematic_view.mp4` |
| | Resolution: 1920x1080 @ 24fps |
| | File size: ~4.5 MB |
| | Generation time: ~2-3 minutes |
| | Cost: $0.20 (from free credits) |
| **Combined** | `music_video_ethiopian_mountains.mp4` |
| | Duration: 8 seconds (synced) |
| | Resolution: 1920x1080 @ 24fps |
| | File size: ~5.8 MB |
| | Format: H.264 + AAC |

---

## Challenges & Solutions

### What didn't work on first try?

**1. Programmatic Video Generation**
- Expected: Python SDK to accept API key like Lyria does
- Reality: Got OAuth2 authentication error
- Impact: Blocked automated video generation workflow

**2. Audio-Video Duration Mismatch**
- Lyria generated 8.2 seconds of audio
- Veo generated exactly 8.0 seconds of video
- MoviePy would extend or cut content incorrectly

### How did you troubleshoot?

**OAuth2 Issue:**
1. Checked API key format and permissions
2. Reviewed SDK documentation (unclear about OAuth2 requirement)
3. Searched for similar issues - found Veo requires different auth than Lyria
4. Evaluated options: Setup OAuth2 vs use web UI

**Duration Mismatch:**
1. Printed both durations: `video.duration` and `audio.duration`
2. Tested MoviePy's default behavior - it extended video with black frames
3. Found `subclipped()` method for precise trimming

### What workarounds did you discover?

**Workaround 1: Vertex AI Studio Web UI**

Instead of spending hours on OAuth2 setup, I used the browser interface:
- Faster to get started
- Visual preview before download
- Same Veo 3.1 model quality
- Trade-off: Manual step instead of fully automated

**Workaround 2: Duration Synchronization**

Added automatic duration syncing in combination script:
```python
duration = min(video.duration, audio.duration)
video = video.subclipped(0, duration)
audio = audio.subclipped(0, duration)
```

This ensures both clips are exactly the same length before merging.

---

## Insights & Learnings

### What surprised you about the codebase?

**1. Registry Pattern Elegance**
The decorator-based registration is brilliant - new providers just "appear" in the registry without modifying core code.

**2. Real-Time Music Generation**
Lyria's WebSocket streaming generates 8 seconds of music in ~15 seconds total. That's impressively fast.

**3. Minimal Dependencies**
Only essential packages (httpx, pydantic, typer). No bloated frameworks.

### What would you improve?

**1. Fallback Authentication**
When OAuth2 is required but not configured, automatically suggest using web UI alternatives with links.

**2. Duration Control**
Let users specify exact durations rather than relying on provider defaults (Veo always returns 8s).

**3. Progress Indicators**
For long-running jobs, show progress bars or estimated completion times.

**4. Preset Library**
Add more cultural presets (Afrobeat, K-pop, Latin jazz) with proper instrument tags.

### How does this compare to other AI tools you've used?

| Aspect | This Framework | Suno/Runway | OpenAI/Anthropic APIs |
|--------|----------------|-------------|----------------------|
| **Flexibility** | High - swap providers | Locked to one | Single provider |
| **Cost Control** | Transparent tracking | Subscription-based | Pay-per-token |
| **Extensibility** | Plugin architecture | Closed platform | API-only |
| **Learning Curve** | Steep (code required) | Easy (web UI) | Medium |
| **Production Ready** | Yes, with customization | For individuals | Yes |

**Key Advantages:**
- **Provider independence** - Not locked into one vendor
- **Cost transparency** - Track every generation with job tracker
- **Customizable** - Add providers, modify prompts, integrate with pipelines

**Best For:** Production workflows where you need flexibility, cost control, and integration with existing systems.

---

## Final Thoughts

This challenge taught me that **pragmatism > perfectionism**. When the programmatic video approach failed, switching to the web UI was the right decision. The hybrid workflow (manual video + programmatic music + scripted combination) demonstrates that understanding multiple approaches matters more than rigid adherence to one method.

The codebase's architecture makes it production-ready for content generation at scale - the registry pattern, async design, and result objects show thoughtful engineering for real-world use cases.

**Time Spent:** ~2.5 hours  
**Status:** ✅ Complete
