from utils import multichannel, stereo, channeldelay, channelshuffle, polarityshuffle, feedbackdelay, fwht

def reverb(audio_array, sample_rate, diffusion_channels, diffusion_delay_ms, diffusion_feedthroughs, feedback_delay_ms, feedback_gain):
    output_array = multichannel(audio_array, diffusion_channels)
    for i in range(diffusion_feedthroughs):
        output_array = channeldelay(audio_array, diffusion_delay_ms, sample_rate)
        output_array = channelshuffle(output_array)
        output_array = polarityshuffle(output_array)
        output_array = fwht(output_array)
    output_array = feedbackdelay(output_array,feedback_delay_ms,feedback_gain, sample_rate)
    output_array = stereo(output_array)
    return output_array
