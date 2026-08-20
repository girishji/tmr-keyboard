This directory should be used as IPC plugin in Kicad 10+.

Create a symlink in ~/Documents/KiCad/10.0/plugins 

Two icons appear on right hand top corner

Output messages go into the warning system. Click on the yellow icon that
appears (if warnings exist) on the right hand bottom corner. Write all output
messages as follows: print(f"foo", file=sys.stderr, flush=True)

