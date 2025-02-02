from kokoro import KPipeline
import soundfile as sf
import numpy as np

# Load text from a file
with open("input.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Initialize TTS pipeline
pipeline = KPipeline(lang_code='a')  # Ensure lang_code matches voice

# Generate audio segments
generator = pipeline(
    text, voice='af_heart',  # <= Change voice here
    speed=1, split_pattern=r'\n+'
)

# Collect all audio chunks
audio_chunks = []

for i, (gs, ps, audio) in enumerate(generator):
    print(f"Processing segment {i}: {gs[:50]}...")  # Print first 50 chars for reference
    audio_chunks.append(audio)

# Concatenate all audio segments
final_audio = np.concatenate(audio_chunks)

# Save as a single output file
sf.write("output.wav", final_audio, 24000)
print("Generated output.wav successfully!")
