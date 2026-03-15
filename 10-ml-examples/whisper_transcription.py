"""
Whisper Transcription Example
=============================
Audio transcription using OpenAI's Whisper model.
Supports multiple languages and audio formats.

Deploy: beam deploy whisper_transcription.py:transcribe
"""

from beam import endpoint, task_queue, Image, Volume, Output
import base64


MODEL_CACHE = "./whisper_models"

image = Image(python_version="python3.11").add_commands([
    "apt-get update",
    "apt-get install -y ffmpeg",
]).add_python_packages([
    "openai-whisper",
    "torch",
    "numpy",
])


def load_whisper_model():
    """Load Whisper model at startup."""
    import whisper
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    model = whisper.load_model("base", download_root=MODEL_CACHE)
    
    return model


@endpoint(
    name="whisper-transcribe",
    cpu=2,
    memory="4Gi",
    gpu="A10G",
    image=image,
    on_start=load_whisper_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="whisper-models", mount_path=MODEL_CACHE)],
)
def transcribe(context, **inputs):
    """
    Transcribe audio to text.
    
    Example (base64 encoded audio):
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"audio_base64": "...", "language": "en"}'
    """
    import tempfile
    import os
    
    model = context.on_start_value
    
    audio_base64 = inputs.get("audio_base64")
    audio_url = inputs.get("audio_url")
    language = inputs.get("language")
    
    if not audio_base64 and not audio_url:
        return {"error": "Provide audio_base64 or audio_url"}
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        if audio_base64:
            audio_data = base64.b64decode(audio_base64)
            f.write(audio_data)
        temp_path = f.name
    
    try:
        options = {}
        if language:
            options["language"] = language
        
        result = model.transcribe(temp_path, **options)
        
        return {
            "text": result["text"],
            "language": result.get("language", language),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                }
                for seg in result.get("segments", [])
            ],
        }
    finally:
        os.unlink(temp_path)


def load_large_whisper():
    """Load larger Whisper model for better accuracy."""
    import whisper
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    model = whisper.load_model("large-v2", download_root=MODEL_CACHE)
    
    return model


@task_queue(
    name="whisper-transcribe-large",
    cpu=4,
    memory="16Gi",
    gpu="A10G",
    image=image,
    on_start=load_large_whisper,
    volumes=[Volume(name="whisper-models", mount_path=MODEL_CACHE)],
)
def transcribe_large(**inputs):
    """
    Transcribe with large model (async task queue).
    Better accuracy but slower, use for long audio files.
    """
    import whisper
    import tempfile
    import os
    
    model = whisper.load_model("large-v2", download_root=MODEL_CACHE)
    
    audio_base64 = inputs.get("audio_base64")
    language = inputs.get("language")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_data = base64.b64decode(audio_base64)
        f.write(audio_data)
        temp_path = f.name
    
    try:
        options = {"verbose": False}
        if language:
            options["language"] = language
        
        result = model.transcribe(temp_path, **options)
        
        output_path = "/tmp/transcription.txt"
        with open(output_path, "w") as f:
            f.write(result["text"])
        Output(path=output_path).save()
        
        return {
            "text": result["text"],
            "language": result.get("language"),
            "duration_seconds": result.get("duration"),
        }
    finally:
        os.unlink(temp_path)


@endpoint(
    name="whisper-detect-language",
    cpu=2,
    memory="4Gi",
    gpu="A10G",
    image=image,
    on_start=load_whisper_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="whisper-models", mount_path=MODEL_CACHE)],
)
def detect_language(context, **inputs):
    """
    Detect the language of audio.
    """
    import whisper
    import tempfile
    import os
    
    model = context.on_start_value
    
    audio_base64 = inputs.get("audio_base64")
    
    if not audio_base64:
        return {"error": "Provide audio_base64"}
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_data = base64.b64decode(audio_base64)
        f.write(audio_data)
        temp_path = f.name
    
    try:
        audio = whisper.load_audio(temp_path)
        audio = whisper.pad_or_trim(audio)
        
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        _, probs = model.detect_language(mel)
        
        top_languages = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "detected_language": top_languages[0][0],
            "confidence": round(top_languages[0][1], 4),
            "top_languages": [
                {"language": lang, "probability": round(prob, 4)}
                for lang, prob in top_languages
            ],
        }
    finally:
        os.unlink(temp_path)
