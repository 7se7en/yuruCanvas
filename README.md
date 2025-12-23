Program made with DeepSeek-R1 (AI)

Just posting online to maybe share with others. Though as complexity increases, so does the inefficiency. As is the nature with a fully-AI-created program.

# What is it?

Blank canvas where you can create text bubbles and then link them together with directional arrows. Upon mousing over a text bubble with arrows linked to it, text bubbles it's connected to will become red, text bubbles connecting to it will become orange, and any children from those highlighted text bubbles will become highlighted black.

# How to run

Requires Python and tkinterdnd2 to have access to drag and drop load functionality

`pip install tkinterdnd2`

# How to use

* Double Click : Add new bubble
* Left Click and Drag : Move bubble around
* Right Click and Drag to another Bubble: Connect to bubbles together with a line
* Double Click on Bubble -> Edit -> Toggleable : Makes a bubble function as a switch that shows/hide its connection lines, bubbles connected to it, and connection lines coming from those bubbles. Ex: [[[ (TOGGLE, A)->(B)-> ]]](C)->D
* Mouse Wheel : Scroll up and down (if canvas is bigger than window)
* Ctrl + Mouse Wheel : Scroll left to right (if canvas is bigger than window)

# Quick Way to Load files

Drag .JSON files onto the .pyw file in the folder itself or into the canvas while the program is open to quickly load files.
