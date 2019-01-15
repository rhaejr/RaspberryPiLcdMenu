from pytube import YouTube
import os

directory = "/home/pi/RaspberryPiLcdMenu/Music/"

vids = ['https://www.youtube.com/watch?v=e8A9J94UWI8']

for i in vids:
    # yt = YouTube(i).streams
    # print(yt)
    try:
        yt = YouTube(i).streams.filter(only_audio=True).first().download(output_path=directory)
        print('Finished: ' + i)
    except:
        print('Failed: ' + i)

# subprocess.call('C:\\ffmpeg-20170221-a5c1c7a-win64-static\\bin\\ffmpeg -i "{}.mp4" -vn -c:a copy {}_soundtrack.m4a'.format(yt.filename,yt.filename))

[os.rename(os.path.join(directory, f), os.path.join(directory, f).replace(' ', '_')) for f in os.listdir(directory)]
