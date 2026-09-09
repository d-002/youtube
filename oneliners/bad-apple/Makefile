VIDEO_IN=bad_apple.mp4
FRAMES_DIR=frames
FRAMERATE=138*2/60 # two frames per beat at 138BPM
EXTRACTED_AUDIO=audio.m4a
TEMPLATE_FILE=template.py
OUTPUT_FILE=bad_apple.py

.PHONY: all extract-frames extract-audio to-python clean

all: extract-frames extract-audio to-python

extract-frames:
	mkdir -p $(FRAMES_DIR)
	ffmpeg -i $(VIDEO_IN) -vf "fps=$(FRAMERATE)" -y $(FRAMES_DIR)/frame%04d.png

extract-audio:
	ffmpeg -i $(VIDEO_IN) -vn -acodec copy -y $(EXTRACTED_AUDIO)

to-python:
	python create_code.py $(FRAMES_DIR) $(TEMPLATE_FILE) $(OUTPUT_FILE)

clean:
	$(RM) -r $(FRAMES_DIR) $(EXTRACTED_AUDIO) $(OUTPUT_FILE)
