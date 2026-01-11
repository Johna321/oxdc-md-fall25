# PyMOL script to render BiOx+2 active site animation
# Focus: Mn1 coordination sphere, lid (Glu162), and oxalate

# Load trajectory
load active_site_prod_combined.pdb, traj

# Basic setup
bg_color white
set ray_shadows, 0
set antialias, 2
set ray_trace_mode, 1

# Hide everything first
hide all

# Show protein as cartoon (thin)
show cartoon, traj
set cartoon_transparency, 0.7
color gray80, traj

# Mn1 - large purple sphere
select mn1, resn MN1
show spheres, mn1
color purple, mn1
set sphere_scale, 0.8, mn1

# Mn2 - smaller sphere for reference
select mn2, resn MN and resi 384
show spheres, mn2
color lightpink, mn2
set sphere_scale, 0.5, mn2

# Mn1 coordination ligands - sticks
select coord_ligands, (resn HD1 or resn HD2 or resn HD3 or resn GU1)
show sticks, coord_ligands
color cyan, coord_ligands and elem C
color blue, coord_ligands and elem N
color red, coord_ligands and elem O

# Oxalate - thick sticks, yellow carbon
select oxalate, resn OX1
show sticks, oxalate
set stick_radius, 0.25, oxalate
color yellow, oxalate and elem C
color red, oxalate and elem O

# Glu162 (GLH) - THE KEY RESIDUE - green, prominent
select glu162, resn GLH and resi 162
show sticks, glu162
set stick_radius, 0.2, glu162
color forest, glu162 and elem C
color red, glu162 and elem O

# Lid region cartoon - highlight
select lid, resi 160-166
set cartoon_color, lightgreen, lid
set cartoon_transparency, 0.3, lid

# Label key atoms
#label mn1 and name MN, "Mn1"
#label glu162 and name CD, "Glu162"

# Center and zoom on Mn1
center mn1
zoom mn1, 15

# Set view (looking down at active site)
set_view (\
     0.891642094,   -0.270833731,    0.362550199,\
     0.421987236,    0.763268292,   -0.489029825,\
    -0.164464533,    0.589058578,    0.791246951,\
     0.000000000,    0.000000000,  -45.000000000,\
     0.000000000,    0.000000000,    0.000000000,\
    35.000000000,   55.000000000,  -20.000000000 )

# Movie settings
set movie_fps, 15
mset 1 -100

# Render frames
set ray_trace_frames, 1
set cache_frames, 0

# For quick preview (no ray tracing)
# mpng active_site_frames/frame_, 0, 100

# For high quality (ray traced) - slower
# mpng active_site_frames_hq/frame_, 0, 100, ray=1
