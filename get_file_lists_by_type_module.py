import os
import csv

def get_all_DAW_extensions():
    # Get the directory where this script is located
    dawINFO_csv = os.path.dirname(os.path.abspath(__file__))
    dawINFO_csv = os.path.join(dawINFO_csv,'daw_info.csv')
    extensions = []
    with open(dawINFO_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header row
        for row in reader:
            extensions += row[1:]
        #end
    #end
    return extensions
#end



## =--- Audio file processing ---=##

# .wav (Waveform Audio File Format)
# .flac (Free Lossless Audio Codec)
# .alac (Apple Lossless Audio Codec)
# .aif / .aiff (Audio Interchange File Format)
# .mp3 (MPEG-1 or MPEG-2 Audio Layer III)
# .m4a (MPEG-4 Part 14, Advanced Audio Coding)
# .ogg (Ogg Vorbis)
# .opus (Opus Interactive Audio Codec)
# .wma (Windows Media Audio)
audio_extensions = ['.wav', '.flac', '.alac', '.aif', '.aiff', '.mp3', '.m4a', '.ogg', '.opus', '.wma']

def get_list_of_audio_files(directory):
    # Get a list of all files in the directory with an audio extension
    audio_files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in audio_extensions]

    # Return the list of audio files
    return audio_files
#end


## =--- Video file processing ---=##

# MP4 (MPEG-4 Part 14)
# AVI (Audio Video Interleave)
# MOV (QuickTime File Format)
# WMV (Windows Media Video)
# FLV (Flash Video)
# MKV (Matroska Multimedia Container)
# MPEG (Moving Picture Experts Group)
# WebM (WebM Project)
# 3GP (3GPP Multimedia File)
# M4V (iTunes Video File)
video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.mpeg', '.webm', '.3gp', '.m4v']

def get_list_of_video_files(directory):
    # Get a list of all files in the directory with a video extension
    video_file = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in video_extensions]

    # Return the list of video files
    return video_file
#end

## =--- Score file processing ---=##

# PDF - Portable Document Format
# MIDI - Musical Instrument Digital Interface
# Sibelius - Proprietary score-writing software format
# MusicXML - An open standard for exchanging digital sheet music
# Finale - Proprietary score-writing software format
# LilyPond - A free and open-source music engraving program
# MuseScore - A free and open-source music notation software
# Guitar Pro - Proprietary tablature writing software format
# ABC notation - A simple text-based format for music notation
# Noteflight - A web-based music notation software

# Score file extensions
score_extensions = ['.pdf', '.mid', '.sib', '.musicxml', '.musx', '.ly', '.mscz', '.gpx', '.abc']

def get_list_of_score_files(directory):
    # Get a list of all files in the directory with a score extension
    score_files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in score_extensions]

    # Return the list of score files
    return score_files
#end
