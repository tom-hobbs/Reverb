import gradio as gr
import soundfile as sf
import numpy as np
from reverb import reverb
# import ipdb


def int16_to_float32(x):
    return x.astype(np.float32) / 32767


def float32_to_int16(x):
    return (np.clip(x, -1, 1) * 32767).astype(np.int16)


def process_audio(
    audio,
    diffusion_channels,
    diffusion_delay_ms,
    diffusion_feedthroughs,
    feedback_delay_ms,
    feedback_gain,
):
    sample_rate = audio[0]
    audio = int16_to_float32(audio[1])
    # Force stereo if mono
    if audio.ndim == 1:
        audio = np.stack((audio, audio), axis=-1)
    audio = reverb(
        audio,
        sample_rate,
        diffusion_channels,
        diffusion_delay_ms,
        diffusion_feedthroughs,
        feedback_delay_ms,
        feedback_gain,
    )
    audio = float32_to_int16(audio)
    return (sample_rate, audio)


# Gradio app interface
with gr.Blocks() as app:
    gr.Markdown("# Audio Reverb Processor")

    # Inputs: audio file
    audio_input = gr.Audio(label="Upload Audio File")

    # Reverb Parameters
    diffusion_channels = gr.Slider(
        minimum=1, maximum=10, value=2, step=1, label="Diffusion Channels"
    )
    diffusion_delay_ms = gr.Slider(
        minimum=1, maximum=100, value=50, step=1, label="Diffusion Delay (ms)"
    )
    diffusion_feedthroughs = gr.Slider(
        minimum=1, maximum=10, value=3, step=1, label="Diffusion Feedthroughs"
    )
    feedback_delay_ms = gr.Slider(
        minimum=1, maximum=500, value=250, step=1, label="Feedback Delay (ms)"
    )
    feedback_gain = gr.Slider(
        minimum=0.1, maximum=1.0, value=0.5, step=0.05, label="Feedback Gain"
    )

    # Output: processed audio
    reverb_output = gr.Audio(label="Processed Audio with Reverb")

    # Button to apply reverb
    apply_button = gr.Button("Apply Reverb")
    apply_button.click(
        process_audio,
        inputs=[
            audio_input,
            diffusion_channels,
            diffusion_delay_ms,
            diffusion_feedthroughs,
            feedback_delay_ms,
            feedback_gain,
        ],
        outputs=reverb_output,
    )

# Launch the app
app.launch()
