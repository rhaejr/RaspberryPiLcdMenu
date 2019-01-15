from ffmpy import FFmpeg
title = 'Crushing Steel Toe Cap Boots with Hydraulic Press!'
ff = FFmpeg(inputs={'video/{}.mp4'.format(title): None}, outputs={'video/{}Converted.mpeg'.format(title): None})

ff.run()