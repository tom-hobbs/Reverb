import numpy as np

#convert stereo to mono
def mono(audio_array):
    mono_array=np.copy(audio_array)
    mono_array[:,0]=(audio_array[:,0]+audio_array[:,1])/2
    mono_array[:,1]=mono_array[:,0]
    return mono_array

#convert 2 channel audio to n channels
def multichannel(audio_array, 
                 channels: int = 8
                 ):
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
def diffuse(audio_array, window_size):
    #generate hadamard matrix of size 2^(window_size)
    n = 2^(window_size)
    H = np.array([[1]])
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    length = audio_array.shape[0]
    n = 1 + int(np.log2(length)) # find the nearest power of 2
    H = hadamard_matrix(np.power(2,n))
    T = np.zeros((np.power(2,n), audio_array.shape[1]))
    T[:length, :] = audio_array #pad with zeros
    output_array = H @ T
    return output_array


#performs a sliding window fast Walsh–Hadamard transform (fwht) on all channels simultaneously
def fwht(audio_array: np.ndarray,
          window_size: int = 8 #must be a power of 2
          ): 
    
    assert np.log2(window_size).is_integer(), "window_size must be a power of 2"

    #generates a standard hadamard matrix, H, of order N = 2^k
    H = np.block([[1]]) #order 1 matrix
    while H.shape[0] < window_size: #generate hadamard matrix of order = window_size
        H = np.block([[H, H], [H, -H]])

    #rearrange rows of H in sequency order
        #window_size == H.shape[0] == H.shape[1]
    zero_crossings = np.zeros((window_size, window_size + 1)) #generate empty output matrix with column to store sequency data
    zero_crossings[:window_size,:window_size] = H
    for i in range(window_size): #count zero crossings and store in last column of zero_crossings
        x = 0
        for j in range(window_size - 1):
            if H[i, j] != H[i, j + 1]:
                x = x + 1    
        zero_crossings[i,window_size] = x
    zero_crossings = zero_crossings[zero_crossings[:, window_size].argsort()] #rearrange rows as based on values in last column
    H = zero_crossings[:window_size,:window_size] #store ordered matrix in H
    
    #set up output arrays
    window_number = audio_array.shape[0] #how many windows are needed
    X = np.zeros((audio_array.shape[0] + window_size - 1, audio_array.shape[1])) #add empty length for sliding window
    X[:audio_array.shape[0],:] = audio_array
    audio_array = X
    output_array = np.copy(audio_array)

    for j in range(window_number):
        window_end = j + window_size
        window_array = audio_array[j:window_end,:]
        #print("H before calc", H)
        #print("window array before calc", window_array)
        #print("audio array before calc2", audio_array)
        output_array[j:window_end,:] = (1 / np.sqrt(2)) * np.matmul(H, window_array)

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
