import numpy as np

#convert stereo to mono
def mono(audio_array):
    mono_array=np.copy(audio_array)
    mono_array[:,0]=(audio_array[:,0]+audio_array[:,1])/2
    mono_array[:,1]=mono_array[:,0]
    return mono_array

#convert 2 channel audio to n channels
def multichannel(audio_array, channels):
    output_array = np.zeros((audio_array.shape[0],channels))
    for i in range(channels):
        j = i / (channels - 1)
        output_array[:,i] = (((1 - j) * audio_array[:,0]) + (j * audio_array[:,1]))
    return output_array

#convert n channel array to stereo by averaging signal across channels
def stereo(audio_array):
    channels = audio_array.shape[1]
    output_array = np.zeros((audio_array.shape[0],2))
    for i in range(int(channels / 2)):
        j = i + int(channels / 2)
        output_array[:,0] = output_array[:,0] + audio_array[:,i]
        output_array[:,1] = output_array[:,1] + audio_array[:,j]
    output_array = output_array / int(channels / 2)
    return output_array

#multichannel delay
def channeldelay(audio_array, delay_time_ms, sample_rate):
    channels = audio_array.shape[1]
    delay_samples = int(sample_rate * (delay_time_ms / 1000)) #calculate delay time in samples
    output_array = np.zeros((audio_array.shape[0] + delay_samples, audio_array.shape[1])) #create output array with time for delayed signal\
    step = int(delay_samples / channels)
    for i in range(channels):
        for j in range(audio_array.shape[0]):
            output_array[(j + (i * step)),i] = audio_array[j,i]
    return output_array

#channel shuffle (randomises order of the channels)
def channelshuffle(audio_array):
    channels = audio_array.shape[1]
    output_array = np.copy(audio_array)
    shuffle = np.random.permutation(channels)
    output_array = audio_array[:, shuffle]
    return output_array

#polarity reverser (reverses polarity on channels with odd indecies)
def polarityshuffle(audio_array):
    channels = audio_array.shape[1]
    for i in range(int(channels / 2)):
        i = (2 * i) + 1
        audio_array[:,i] = audio_array[:,i] * (-1)
    return audio_array

#generate hadamard matrix (of order n)
def hadamard_matrix(n):
    H = np.array([[1]])
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H

#diffuse with hadamard matrix transform
def diffuse(audio_array):
    length = audio_array.shape[0]
    n = 1 + int(np.log2(length)) # find the nearest power of 2
    H = hadamard_matrix(np.power(2,n))
    T = np.zeros((np.power(2,n), audio_array.shape[1]))
    T[:length, :] = audio_array #pad with zeros
    output_array = H @ T
    return output_array

#windowed delay feedback system
def feedbackdelay(audio_array, delay_time_ms, feedback_gain, sample_rate):
    delay_samples = int(sample_rate * (delay_time_ms / 1000)) #calculate delay time in samples
    delay_buffer = np.zeros((delay_samples, audio_array.shape[1])) #create buffer of delay time with equivilent channels as incoming file
    output_array = np.zeros((audio_array.shape[0] + (20 * delay_samples), audio_array.shape[1])) #output array to store wet signal and accomodate delay tail
    output_array[:audio_array.shape[0],:] = audio_array 
    audio_array = output_array #extends audio_array to output_array length by adding zeros, for compailibility with for loop
    delay_index = 0 #allows indexing of the position within short delay buffer in the for loop
    for i in range(audio_array.shape[0]):
        output_array[i,:] = audio_array[i,:] + (delay_buffer[delay_index,:] * feedback_gain) #adds delay buffer to wet signal
        delay_buffer[delay_index,:] = output_array[i,:] #writes new wet signal into delay buffer
        delay_index = (delay_index + 1) % delay_samples #incremends delay index (in base buffer size)
    return output_array
