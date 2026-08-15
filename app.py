import streamlit as st
import time
import wave
import io
import numpy as np
from pathlib import Path

from main import (
    VoiceAssistant,
    retrieve_context,
    add_to_knowledge_base,
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "configs" / "config.yaml"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NOVA | Neural AI Assistant",
    page_icon="🎙️",
    layout="centered",
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    """
    <style>

        .block-container {
            max-width: 950px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        .nova-subtitle {
            color: #9ca3af;
            font-size: 17px;
            margin-top: -10px;
        }

        .nova-caption {
            color: #8b8f98;
            font-size: 14px;
            margin-top: 8px;
        }

        .response-box {
            padding: 18px 20px;
            border-radius: 14px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            margin-top: 10px;
        }

        .voice-box {
            padding: 20px;
            border-radius: 16px;
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 20px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# NOVA HEADER
# =========================================================

st.markdown(
    """
    <h1 style="margin-bottom:0;">NOVA</h1>

    <div class="nova-subtitle">
        Neural Orchestration & Voice Assistant
    </div>

    <div class="nova-caption">
        Voice • LLM • Memory • RAG • Intelligent Tools
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# LOAD BACKEND
# =========================================================

@st.cache_resource
def load_assistant():
    return VoiceAssistant(
        config_path=str(CONFIG_PATH)
    )


try:
    assistant = load_assistant()

except Exception as e:
    st.error("NOVA backend could not be initialized.")
    st.exception(e)
    st.stop()


# =========================================================
# WAV AUDIO -> NUMPY
# =========================================================

def wav_to_numpy(audio_file):
    """
    Convert browser-recorded WAV audio into
    mono float32 NumPy audio for the existing STT.
    """

    audio_bytes = audio_file.getvalue()

    with wave.open(io.BytesIO(audio_bytes), "rb") as wav:

        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()

        raw_audio = wav.readframes(frame_count)

    if sample_width == 2:

        audio = (
            np.frombuffer(
                raw_audio,
                dtype=np.int16
            ).astype(np.float32)
            / 32768.0
        )

    elif sample_width == 4:

        audio = (
            np.frombuffer(
                raw_audio,
                dtype=np.int32
            ).astype(np.float32)
            / 2147483648.0
        )

    elif sample_width == 1:

        audio = (
            np.frombuffer(
                raw_audio,
                dtype=np.uint8
            ).astype(np.float32)
            - 128
        ) / 128.0

    else:
        raise ValueError(
            f"Unsupported audio format: {sample_width} bytes"
        )

    # Stereo -> mono
    if channels > 1:

        audio = audio.reshape(-1, channels)

        audio = np.mean(
            audio,
            axis=1
        )

    return audio.astype(np.float32), sample_rate


# =========================================================
# NOVA AI PIPELINE
# =========================================================

def process_with_nova(user_text):

    # -----------------------------------------------------
    # MEMORY RESET
    # -----------------------------------------------------

    if user_text.strip().lower() == "reset memory":

        assistant.conversation_memory.clear()

        return (
            "Conversation memory has been reset.",
            {
                "actionable": {
                    "prediction": "RESET",
                    "confidence": 1.0,
                },
                "contextable": {
                    "prediction": "NO",
                    "confidence": 1.0,
                },
                "contexts": [],
                "tool_used": False,
            }
        )

    # -----------------------------------------------------
    # ACTIONABLE CLASSIFICATION
    # -----------------------------------------------------

    actionable_result = (
        assistant.actionable_classifier
        .is_actionable(user_text)
    )

    # -----------------------------------------------------
    # CONTEXTABLE CLASSIFICATION
    # -----------------------------------------------------

    contextable_result = (
        assistant.contextable_classifier
        .is_contextable(user_text)
    )

    # -----------------------------------------------------
    # RETRIEVE RAG MEMORY
    # -----------------------------------------------------

    contexts = retrieve_context(
        user_text,
        k=5
    )

    context_block = "\n".join(
        f"- {ctx}"
        for ctx in contexts
    )

    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    history_block = ""

    if assistant.include_history_in_prompt:

        history_str = (
            assistant.conversation_memory
            .get_history_string()
        )

        if history_str:

            history_block = (
                "\nConversation History:\n"
                f"{history_str}\n"
            )

    # -----------------------------------------------------
    # FINAL LLM PROMPT
    # -----------------------------------------------------

    final_prompt = f"""
You are NOVA, a helpful AI voice assistant.

Context from memory:
{context_block}

{history_block}

User:
{user_text}

Answer the user clearly and naturally.
"""

    # -----------------------------------------------------
    # LLM
    # -----------------------------------------------------

    llm_response, _ = assistant.llm.generate(
        final_prompt,
        max_tokens=500,
        temperature=0.7,
        top_p=0.9,
        tools_prompt=assistant.tool_manager.get_tools_prompt(),
    )

    # -----------------------------------------------------
    # TOOL PROCESSING
    # -----------------------------------------------------

    processed = (
        assistant.tool_manager
        .process_response_with_tools(
            llm_response
        )
    )

    if processed["tool_used"]:

        response_text = processed["content"]

        tool_result = (
            assistant.tool_manager
            .format_tool_result_for_user(
                processed["tool_result"]
            )
        )

        if response_text:

            response = (
                f"{response_text}\n\n"
                f"{tool_result}"
            )

        else:

            response = tool_result

    else:

        response = processed["content"]

    # -----------------------------------------------------
    # SAVE CONVERSATION
    # -----------------------------------------------------

    assistant.conversation_memory.add_turn(
        user_text,
        response
    )

    # -----------------------------------------------------
    # SAVE TO RAG MEMORY
    # -----------------------------------------------------

    if contextable_result["contextable"]:

        add_to_knowledge_base(
            user_text,
            {
                "timestamp": time.time()
            }
        )

    # -----------------------------------------------------
    # DETAILS
    # -----------------------------------------------------

    details = {
        "actionable": actionable_result,
        "contextable": contextable_result,
        "contexts": contexts,
        "tool_used": processed["tool_used"],
    }

    return response, details


# =========================================================
# VOICE INTERFACE
# =========================================================

st.markdown("### 🎙️ Talk to NOVA")

st.markdown(
    """
    <div class="voice-box">
        <b>Voice Mode</b><br>
        Press the microphone button, speak naturally,
        and stop recording when you are finished.
        NOVA will transcribe and process your voice.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MICROPHONE
# =========================================================

audio_value = st.audio_input(
    "🎙️ Record your message",
    sample_rate=16000,
)


# =========================================================
# VOICE PROCESSING
# =========================================================

if audio_value is not None:

    # -----------------------------------------------------
    # TRANSCRIPTION
    # -----------------------------------------------------

    with st.spinner("🎧 Transcribing your voice..."):

        try:

            audio_np, sample_rate = (
                wav_to_numpy(audio_value)
            )

            transcription_start = time.time()

            transcript = assistant.stt.transcribe(
                audio_np
            )

            transcription_time = (
                time.time()
                - transcription_start
            )

        except Exception as e:

            st.error(
                "Voice transcription failed."
            )

            st.exception(e)
            st.stop()

    # -----------------------------------------------------
    # SHOW TRANSCRIPT
    # -----------------------------------------------------

    if transcript and transcript.strip():

        st.markdown("### 🗣️ You said")

        st.markdown(
            f"""
            <div class="response-box">
                {transcript}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # NOVA PROCESSING
        # -------------------------------------------------

        with st.spinner("🧠 NOVA is thinking..."):

            try:

                response, details = (
                    process_with_nova(
                        transcript
                    )
                )

            except Exception as e:

                st.error(
                    "NOVA processing failed."
                )

                st.exception(e)
                st.stop()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        st.markdown("### 🤖 NOVA")

        st.markdown(
            '<div class="response-box">',
            unsafe_allow_html=True,
        )

        st.markdown(response)

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # TEXT TO SPEECH
        # -------------------------------------------------

        if (
            assistant.tts_enabled
            and assistant.tts
            and response
        ):

            try:

                assistant.tts.speak_async(
                    response
                )

                st.caption(
                    "🔊 NOVA is speaking..."
                )

            except Exception as e:

                st.warning(
                    f"TTS could not start: {e}"
                )

        # -------------------------------------------------
        # PROCESSING DETAILS
        # -------------------------------------------------

        st.divider()

        with st.expander(
            "🧠 NOVA Processing Details"
        ):

            st.write(
                "**Transcription Time:**",
                f"{transcription_time:.2f} seconds"
            )

            st.write(
                "**Sample Rate:**",
                f"{sample_rate} Hz"
            )

            st.write(
                "**Actionable:**",
                details["actionable"]["prediction"]
            )

            st.write(
                "**Actionable Confidence:**",
                round(
                    details["actionable"]["confidence"],
                    3
                )
            )

            st.write(
                "**Contextable:**",
                details["contextable"]["prediction"]
            )

            st.write(
                "**Contextable Confidence:**",
                round(
                    details["contextable"]["confidence"],
                    3
                )
            )

            st.write(
                "**Retrieved Memories:**",
                len(details["contexts"])
            )

            st.write(
                "**Tool Used:**",
                details["tool_used"]
            )

    else:

        st.warning(
            "NOVA could not detect any speech. "
            "Please try recording again."
        )


# =========================================================
# TEXT FALLBACK
# =========================================================

st.divider()

st.markdown("### 💬 Or type to NOVA")

user_text = st.text_input(
    "Your message",
    placeholder="Ask NOVA anything...",
    label_visibility="collapsed",
)

send = st.button(
    "🚀 Send Text to NOVA",
    type="secondary",
    use_container_width=True,
)


if send:

    if not user_text.strip():

        st.warning(
            "Please enter something."
        )

    else:

        with st.spinner(
            "🧠 NOVA is thinking..."
        ):

            try:

                response, details = (
                    process_with_nova(
                        user_text
                    )
                )

            except Exception as e:

                st.error(
                    "NOVA processing failed."
                )

                st.exception(e)
                st.stop()

        st.markdown("### 🤖 NOVA")

        st.markdown(
            '<div class="response-box">',
            unsafe_allow_html=True,
        )

        st.markdown(response)

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

        # TTS
        if (
            assistant.tts_enabled
            and assistant.tts
            and response
        ):

            try:

                assistant.tts.speak_async(
                    response
                )

                st.caption(
                    "🔊 NOVA is speaking..."
                )

            except Exception as e:

                st.warning(
                    f"TTS could not start: {e}"
                )

        st.divider()

        with st.expander(
            "🧠 NOVA Processing Details"
        ):

            st.write(
                "**Actionable:**",
                details["actionable"]["prediction"]
            )

            st.write(
                "**Actionable Confidence:**",
                round(
                    details["actionable"]["confidence"],
                    3
                )
            )

            st.write(
                "**Contextable:**",
                details["contextable"]["prediction"]
            )

            st.write(
                "**Contextable Confidence:**",
                round(
                    details["contextable"]["confidence"],
                    3
                )
            )

            st.write(
                "**Retrieved Memories:**",
                len(details["contexts"])
            )

            st.write(
                "**Tool Used:**",
                details["tool_used"]
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6b7280;
        font-size:13px;
        margin-top:40px;
    ">
        NOVA • Neural Orchestration & Voice Assistant
        <br>
        Voice • LLM • Memory • RAG • Intelligent Tools
    </div>
    """,
    unsafe_allow_html=True,
)