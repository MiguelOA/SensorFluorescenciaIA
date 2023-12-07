from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

#Slow motion
in_loc = 'video.mp4'

#Import video clip
clip = VideoFileClip(in_loc)
print("fps: {}".format(clip.fps))
