import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-q'])

for i in range(1, 16):
    cmd.load(f"site_frames.pdb.{i}", "structure", format="pdb")
    
    # Set consistent colors - adjust these to your needs
    cmd.color("green", "elem C")
    cmd.color("red", "elem O")
    cmd.color("blue", "elem N")
    cmd.color("white", "elem H")
    cmd.color("yellow", "elem S")
    cmd.color("magenta", "elem Mn")  # if you have manganese
    
    cmd.png(f"frame_{i:04d}.png", width=1280, height=720, ray=1)
    cmd.delete("all")

cmd.quit()
