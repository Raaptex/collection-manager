import sys, gui, setproctitle

setproctitle.setproctitle('Collection Manager')

gui.start(sys.argv[1])