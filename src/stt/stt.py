import numpy as np
from faster_whisper import WhisperModel


class SpeechToText:

    def __init__(
        self,
        model_size="small",
        compute_type="int8",
        device="cpu",
        sample_rate=16000
    ):
        self.model_size = model_size
        self.compute_type = compute_type
        self.device = device
        self.sample_rate = sample_rate

        print(
            f"Loading Whisper model: "
            f"{model_size} | device={device} | compute={compute_type}"
        )

        self.model = WhisperModel(
            model_size,
            compute_type=compute_type,
            device=device
        )

        print("Whisper model loaded successfully.")

    def transcribe(self, audio_data):

        if audio_data is None:
            return ""

        audio = np.asarray(audio_data, dtype=np.float32)

        if audio.size == 0:
            return ""

        # Convert stereo to mono if necessary
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        # Keep audio in valid range
        audio = np.clip(audio, -1.0, 1.0)

        try:

            segments, info = self.model.transcribe(
                audio,

                # English speech
                language="en",

                # Normal transcription
                task="transcribe",

                # Better accuracy
                beam_size=5,

                # Don't depend on previous audio
                condition_on_previous_text=False,

                # Prevent hallucination on weak audio
                no_speech_threshold=0.6,

                # Stable decoding
                temperature=0.0
            )

            parts = []

            for segment in segments:
                text = segment.text.strip()

                if text:
                    parts.append(text)

            transcript = " ".join(parts).strip()

            return transcript

        except Exception as e:

            print(f"[STT ERROR] {type(e).__name__}: {e}")

            return ""

    def __str__(self):

        return (
            f"SpeechToText("
            f"model={self.model_size}, "
            f"device={self.device}, "
            f"compute_type={self.compute_type})"
        )