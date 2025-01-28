import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk
import json
import sys
import math

# Import tkinterdnd2 for drag-and-drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    messagebox.showerror("Error", "The tkinterdnd2 library is required for drag-and-drop support. Open Powershell and type pip install tkinterdnd2")
    sys.exit(1)

class TextBubble:
    def __init__(self, canvas, x, y, text, width=100, height=50, id=None, app=None):
        self.canvas = canvas
        self.text = text
        self.id = id  # Unique identifier for the bubble
        self.width = width  # Set width from the start
        self.height = height  # Set height from the start
        self.font_size = 12  # Default font size (small)
        self.app = app  # Reference to the CanvasApp instance

        # Draw the rectangle and text
        self.rect = canvas.create_rectangle(x, y, x + self.width, y + self.height, fill="white", outline="black")
        
        # Draw the ID
        # self.label = canvas.create_text( x , y , text=id, fill="black", width=30, anchor="w", font=("Arial", self.font_size))
        
        self.label = canvas.create_text(
            x + self.width / 2, y + self.height / 2, text=text, fill="black", width=self.width - 10, anchor="center", font=("Arial", self.font_size)
        )  # Center-align text

        # Add resize handles
        self.resize_handles = [
            canvas.create_rectangle(x + self.width - 5, y + self.height - 5, x + self.width + 5, y + self.height + 5, fill="blue")
        ]

        self.lines = []  # Store lines connected to this bubble

        # Bind drag, resize, and edit functionality
        self.canvas.tag_bind(self.rect, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.rect, "<Double-Button-1>", self.edit_text)
        self.canvas.tag_bind(self.label, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.label, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.label, "<Double-Button-1>", self.edit_text)
        for handle in self.resize_handles:
            self.canvas.tag_bind(handle, "<Button-1>", self.start_resize)
            self.canvas.tag_bind(handle, "<B1-Motion>", self.on_resize)

        # Bind hover events
        self.canvas.tag_bind(self.rect, "<Enter>", self.on_hover)
        self.canvas.tag_bind(self.rect, "<Leave>", self.on_leave)
        self.canvas.tag_bind(self.label, "<Enter>", self.on_hover)
        self.canvas.tag_bind(self.label, "<Leave>", self.on_leave)

    def get_position(self):
        return self.canvas.coords(self.rect)

    def start_drag(self, event):
        self.drag_data = {"x": event.x, "y": event.y}
        # Bring the bubble and its label to the top
        self.canvas.tag_raise(self.rect)
        self.canvas.tag_raise(self.label)
        for handle in self.resize_handles:
            self.canvas.tag_raise(handle)

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if dx != 0 or dy != 0:  # Only update if the bubble has moved
            self.canvas.move(self.rect, dx, dy)
            self.canvas.move(self.label, dx, dy)
            for handle in self.resize_handles:
                self.canvas.move(handle, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            # Add a small delay to prevent excessive updates
            self.canvas.after(10, self.update_connected_lines)  # Update lines after 10ms

    def start_resize(self, event):
        self.resize_data = {"x": event.x, "y": event.y}

    def on_resize(self, event):
        dx = event.x - self.resize_data["x"]
        dy = event.y - self.resize_data["y"]
        
        # Calculate the minimum height based on the font size
        min_height = self.font_size * 2  # Minimum height is twice the font size
        
        # Ensure the new height is at least the minimum height
        new_height = self.height + dy
        if new_height < min_height:
            new_height = min_height
            dy = new_height - self.height  # Adjust dy to enforce the minimum height
        
        self.width += dx
        self.height = new_height  # Use the adjusted height
        self.resize_data["x"] = event.x
        self.resize_data["y"] = event.y

        # Update the rectangle and text
        x1, y1, _, _ = self.canvas.coords(self.rect)
        self.canvas.coords(self.rect, x1, y1, x1 + self.width, y1 + self.height)
        self.canvas.coords(self.label, x1 + self.width / 2, y1 + self.height / 2)
        self.canvas.itemconfig(self.label, width=self.width - 10)  # Update text wrapping

        # Update the resize handle position
        self.canvas.coords(self.resize_handles[0], x1 + self.width - 5, y1 + self.height - 5, x1 + self.width + 5, y1 + self.height + 5)

        self.update_connected_lines()

    def update_connected_lines(self):
        for line in self.lines:
            line.update_position()

    def edit_text(self, event):
        # Create a larger text input dialog
        edit_window = tk.Toplevel(self.canvas)
        edit_window.title("Edit Text")
        
        # Center the edit window on the parent window
        parent_x = self.canvas.winfo_rootx()
        parent_y = self.canvas.winfo_rooty()
        parent_width = self.canvas.winfo_width()
        parent_height = self.canvas.winfo_height()
        
        window_width = 400  # Width of the edit window
        window_height = 300  # Increased height for the edit window
        
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create a text widget for multi-line input
        text_box = tk.Text(edit_window, width=50, height=10, wrap=tk.WORD)
        text_box.pack(padx=10, pady=10)
        text_box.insert(tk.END, self.text)  # Pre-fill with current text
        
        # Add a font size dropdown menu
        font_size_label = tk.Label(edit_window, text="Font Size:")
        font_size_label.pack(pady=5)
        
        # Determine the current font size option based on the bubble's font size
        if self.font_size == 12:
            current_font_size = "Small"
        elif self.font_size == 24:
            current_font_size = "Medium"
        elif self.font_size == 36:
            current_font_size = "Large"
        else:
            current_font_size = "Small"  # Default to Small if font size is unexpected
        
        font_size_var = tk.StringVar(value=current_font_size)  # Set the default value
        font_size_menu = ttk.Combobox(edit_window, textvariable=font_size_var, values=["Small", "Medium", "Large"])
        font_size_menu.pack(pady=5)
        
        # Button frame for Save and Delete buttons
        button_frame = tk.Frame(edit_window)
        button_frame.pack(pady=10)
        
        # Save button
        def save_text():
            new_text = text_box.get("1.0", tk.END).strip()  # Get all text from the text box
            if new_text:
                self.text = new_text
                # Update font size based on selection
                if font_size_var.get() == "Medium":
                    self.font_size = 24  # Double the default size
                elif font_size_var.get() == "Large":
                    self.font_size = 36  # Triple the default size
                else:
                    self.font_size = 12  # Default size
                self.canvas.itemconfig(self.label, text=new_text, font=("Arial", self.font_size))
            edit_window.destroy()
        
        save_button = tk.Button(button_frame, text="Save", command=save_text)
        save_button.pack(side=tk.LEFT, padx=5)

    def reset_position(self):
        # Move the bubble to the center of the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        new_x = (canvas_width // 2) - (self.width // 2)
        new_y = (canvas_height // 2) - (self.height // 2)
        self.canvas.coords(self.rect, new_x, new_y, new_x + self.width, new_y + self.height)
        self.canvas.coords(self.label, new_x + self.width / 2, new_y + self.height / 2)
        for handle in self.resize_handles:
            self.canvas.coords(handle, new_x + self.width - 5, new_y + self.height - 5, new_x + self.width + 5, new_y + self.height + 5)
        self.update_connected_lines()

    def delete_all_connections(self):
        for line in self.lines:
            line.delete()
            if line.start_bubble == self:
                line.end_bubble.lines.remove(line)
            else:
                line.start_bubble.lines.remove(line)
            if self.app and line in self.app.lines:
                self.app.lines.remove(line)
        self.lines.clear()

    def on_hover(self, event):
        for line in self.lines:
            line.set_highlight(True)
        for bubble in self.get_connected_bubbles():
            self.canvas.itemconfig(bubble.rect, outline="red", width=4)
        self.canvas.itemconfig(self.rect, outline="blue", width=4)

    def on_leave(self, event):
        for line in self.lines:
            line.set_highlight(False)
        for bubble in self.get_connected_bubbles():
            self.canvas.itemconfig(bubble.rect, outline="black", width=1)
        self.canvas.itemconfig(self.rect, outline="black", width=1)

    def get_connected_bubbles(self):
        # Get all bubbles connected to this bubble
        connected_bubbles = set()
        for line in self.lines:
            if line.start_bubble == self:
                connected_bubbles.add(line.end_bubble)
            else:
                connected_bubbles.add(line.start_bubble)
        return connected_bubbles

class ConnectionLine:
    def __init__(self, canvas, start_bubble, end_bubble):
        self.canvas = canvas
        self.start_bubble = start_bubble
        self.end_bubble = end_bubble
        self.line = None
        self.arrow1 = None
        self.arrow2 = None
        self.update_position()
        start_bubble.lines.append(self)
        end_bubble.lines.append(self)

    def update_position(self):
        # Get the perimeter intersection points
        start_pos = self.get_perimeter_intersection(self.start_bubble, self.end_bubble)
        end_pos = self.get_perimeter_intersection(self.end_bubble, self.start_bubble)

        # Validate coordinates
        if not all(isinstance(coord, (int, float)) for coord in start_pos + end_pos):
            print("  Error: Invalid coordinates detected. Skipping line update.")
            return

        # Check if the line has a non-zero length
        if start_pos[0] != end_pos[0] or start_pos[1] != end_pos[1]:
            if self.line is None:
                # Draw the line beneath the text bubbles
                self.line = self.canvas.create_line(start_pos[0], start_pos[1], end_pos[0], end_pos[1], fill="black", width=2)
                self._create_arrowheads(start_pos, end_pos)
                self.canvas.lower(self.line)  # Ensure the line is below all bubbles
            else:
                self.canvas.coords(self.line, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
                self._update_arrowheads(start_pos, end_pos)
                # Re-lower the arrowheads to ensure they stay below bubbles
                self.canvas.lower(self.arrow1)
                self.canvas.lower(self.arrow2)
        else:
            # Delete the line and arrowheads if they exist
            if self.line is not None:
                self.canvas.delete(self.line)
                self.line = None
            if self.arrow1 is not None:
                self.canvas.delete(self.arrow1)
                self.arrow1 = None
            if self.arrow2 is not None:
                self.canvas.delete(self.arrow2)
                self.arrow2 = None

    def _create_arrowheads(self, start_pos, end_pos):
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]

        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return

        unit_dx = dx / length
        unit_dy = dy / length

        angle = math.radians(45)
        arrow_length = 10

        # Calculate arrowhead directions
        arrow1_dx = unit_dx * math.cos(angle) - unit_dy * math.sin(angle)
        arrow1_dy = unit_dx * math.sin(angle) + unit_dy * math.cos(angle)
        arrow2_dx = unit_dx * math.cos(-angle) - unit_dy * math.sin(-angle)
        arrow2_dy = unit_dx * math.sin(-angle) + unit_dy * math.cos(-angle)

        arrow1_end_x = mid_x + arrow1_dx * arrow_length
        arrow1_end_y = mid_y + arrow1_dy * arrow_length
        arrow2_end_x = mid_x + arrow2_dx * arrow_length
        arrow2_end_y = mid_y + arrow2_dy * arrow_length

        # Create arrowheads
        self.arrow1 = self.canvas.create_line(mid_x, mid_y, arrow1_end_x, arrow1_end_y, fill="black", width=2)
        self.arrow2 = self.canvas.create_line(mid_x, mid_y, arrow2_end_x, arrow2_end_y, fill="black", width=2)

        # Ensure arrowheads are below all bubbles
        self.canvas.lower(self.arrow1)
        self.canvas.lower(self.arrow2)

    def _update_arrowheads(self, start_pos, end_pos):
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        dx = start_pos[0] - end_pos[0]
        dy = start_pos[1] - end_pos[1]

        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return

        unit_dx = dx / length
        unit_dy = dy / length

        angle = math.radians(45)
        arrow_length = 10

        # Calculate arrowhead directions
        arrow1_dx = unit_dx * math.cos(angle) - unit_dy * math.sin(angle)
        arrow1_dy = unit_dx * math.sin(angle) + unit_dy * math.cos(angle)
        arrow2_dx = unit_dx * math.cos(-angle) - unit_dy * math.sin(-angle)
        arrow2_dy = unit_dx * math.sin(-angle) + unit_dy * math.cos(-angle)

        arrow1_end_x = mid_x + arrow1_dx * arrow_length
        arrow1_end_y = mid_y + arrow1_dy * arrow_length
        arrow2_end_x = mid_x + arrow2_dx * arrow_length
        arrow2_end_y = mid_y + arrow2_dy * arrow_length

        self.canvas.coords(self.arrow1, mid_x, mid_y, arrow1_end_x, arrow1_end_y)
        self.canvas.coords(self.arrow2, mid_x, mid_y, arrow2_end_x, arrow2_end_y)

    def get_perimeter_intersection(self, source_bubble, target_bubble):
        # Get the center of the target bubble
        x1, y1, x2, y2 = target_bubble.get_position()
        target_center = ((x1 + x2) / 2, (y1 + y2) / 2)

        # Get the center of the source bubble
        x1, y1, x2, y2 = source_bubble.get_position()
        source_center = ((x1 + x2) / 2, (y1 + y2) / 2)

        # Calculate the intersection points on all four sides of the source bubble
        intersections = [
            self._intersect_with_side(source_bubble, source_center, target_center, "top"),    # N
            self._intersect_with_side(source_bubble, source_center, target_center, "bottom"), # S
            self._intersect_with_side(source_bubble, source_center, target_center, "left"),   # W
            self._intersect_with_side(source_bubble, source_center, target_center, "right"),  # E
        ]

        # Filter out None values (invalid intersections)
        valid_intersections = [point for point in intersections if point is not None]

        # Choose the intersection point that is closest to the target center
        if valid_intersections:
            return min(valid_intersections, key=lambda p: self._distance(p, target_center))
        else:
            # Fallback to the center if no valid intersections are found
            return source_center

    def _intersect_with_side(self, source_bubble, source_center, target_center, side):
        # Get the source bubble's position
        x1, y1, x2, y2 = source_bubble.get_position()

        if side == "top":  # N
            # Intersection with the top side (y = y1)
            y_intersect = y1
            if target_center[1] == source_center[1]:
                # Target is directly above or below, return the midpoint of the top side
                x_intersect = (x1 + x2) / 2
            else:
                x_intersect = source_center[0] + (y_intersect - source_center[1]) * (target_center[0] - source_center[0]) / (target_center[1] - source_center[1])
        elif side == "bottom":  # S
            # Intersection with the bottom side (y = y2)
            y_intersect = y2
            if target_center[1] == source_center[1]:
                # Target is directly above or below, return the midpoint of the bottom side
                x_intersect = (x1 + x2) / 2
            else:
                x_intersect = source_center[0] + (y_intersect - source_center[1]) * (target_center[0] - source_center[0]) / (target_center[1] - source_center[1])
        elif side == "left":  # W
            # Intersection with the left side (x = x1)
            x_intersect = x1
            if target_center[0] == source_center[0]:
                # Target is directly to the left or right, return the midpoint of the left side
                y_intersect = (y1 + y2) / 2
            else:
                y_intersect = source_center[1] + (x_intersect - source_center[0]) * (target_center[1] - source_center[1]) / (target_center[0] - source_center[0])
        elif side == "right":  # E
            # Intersection with the right side (x = x2)
            x_intersect = x2
            if target_center[0] == source_center[0]:
                # Target is directly to the left or right, return the midpoint of the right side
                y_intersect = (y1 + y2) / 2
            else:
                y_intersect = source_center[1] + (x_intersect - source_center[0]) * (target_center[1] - source_center[1]) / (target_center[0] - source_center[0])
        else:
            return None

        # Ensure the intersection point is within the bubble's bounds
        if x1 <= x_intersect <= x2 and y1 <= y_intersect <= y2:
            return (x_intersect, y_intersect)
        else:
            return None

    def set_highlight(self, highlighted):
        color = "red" if highlighted else "black"
        width = 4 if highlighted else 2
        if self.line:
            self.canvas.itemconfig(self.line, fill=color, width=width)
        if self.arrow1:
            self.canvas.itemconfig(self.arrow1, fill=color, width=width)
        if self.arrow2:
            self.canvas.itemconfig(self.arrow2, fill=color, width=width)

    def delete(self):
        if self.line:
            self.canvas.delete(self.line)
        if self.arrow1:
            self.canvas.delete(self.arrow1)
        if self.arrow2:
            self.canvas.delete(self.arrow2)
    
    def _distance(self, p1, p2):
        # Calculate the Euclidean distance between two points
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

class CanvasApp:
    def __init__(self, root, file_path=None):
        self.root = root
        self.root.title("yuruCanvas")  # Set the window title

        # Track the last loaded file path
        self.last_loaded_file_path = file_path

        # Create a frame to hold the canvas and scrollbars
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create the canvas with scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, width=400, height=200, bg="lightgray", scrollregion=(0, 0, 400, 200))
        self.hscroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vscroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set)

        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.hscroll.grid(row=1, column=0, sticky="ew")
        self.vscroll.grid(row=0, column=1, sticky="ns")

        # Configure the frame to expand with the window
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.text_bubbles = []
        self.lines = []
        self.next_bubble_id = 0  # Unique ID for each bubble
        self.right_click_start_bubble = None  # Track the bubble where right-click was pressed

        # Add a menu bar at the top
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Canvas", command=self.new_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Load Canvas", command=self.load_canvas, accelerator="Ctrl+L")
        file_menu.add_command(label="Save Canvas", command=self.save_canvas, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_canvas, accelerator="Ctrl+Shift+S")

        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Text Bubble", command=self.add_text_bubble)
        edit_menu.add_command(label="Resize Canvas", command=self.change_canvas_size, accelerator="Ctrl+R")

        # Debug menu
        debug_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Debug", menu=debug_menu)
        debug_menu.add_command(label="Open Debug Window", command=self.open_debug_window)

        # Bind mouse events for drawing lines
        self.canvas.bind("<Button-3>", self.start_line)  # Right-click press
        self.canvas.bind("<B3-Motion>", self.draw_line)  # Right-click drag
        self.canvas.bind("<ButtonRelease-3>", self.end_line)  # Right-click release

        # Bind double-click event for creating bubbles
        self.canvas.bind("<Double-Button-1>", self.create_bubble_on_canvas)

        # Enable drag-and-drop for JSON files
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind("<<Drop>>", self.on_drop)

        # Setup right-click context menu for the canvas
        self.setup_canvas_context_menu()

        self.current_line = None
        self.start_bubble = None
        self.selected_bubble = None  # Track the selected bubble for context menu

        # Bind keys
        self.root.bind("<Control-n>", lambda event: self.new_canvas())
        self.root.bind("<Control-l>", lambda event: self.load_canvas())
        self.root.bind("<Control-s>", lambda event: self.save_canvas())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as_canvas())     
        self.root.bind("<Control-r>", lambda event: self.change_canvas_size())

        # Load a file if provided as an argument
        if file_path:
            self.load_canvas_from_file(file_path)

    def create_bubble_on_canvas(self, event):
        # Check if the user clicked on a blank part of the canvas (not on a bubble)
        clicked_on_bubble = False
        for bubble in self.text_bubbles:
            x1, y1, x2, y2 = bubble.get_position()
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                clicked_on_bubble = True
                break

        # If the user clicked on a blank part of the canvas, create a new bubble
        if not clicked_on_bubble:
            # Open a dialog to input text
            text = simpledialog.askstring("Input", "Enter text for the bubble:", parent=self.root)
            if text:
                # Create a new bubble at the double-click location
                bubble = TextBubble(self.canvas, event.x, event.y, text, id=self.next_bubble_id)
                self.next_bubble_id += 1
                self.text_bubbles.append(bubble)

    def change_canvas_size(self):
        # Get the current canvas dimensions
        current_width = self.canvas.winfo_width()
        current_height = self.canvas.winfo_height()

        # Open a dialog to get new canvas width, pre-populated with the current width
        new_width = simpledialog.askinteger(
            "Canvas Width", 
            "Enter new canvas width:", 
            parent=self.root, 
            minvalue=100, 
            initialvalue=current_width
        )

        # If the user cancels the width dialog, stop here
        if new_width is None:
            return

        # Use a small delay to ensure the height dialog is focused
        self.root.after(100, self._open_height_dialog, new_width, current_height)

    def _open_height_dialog(self, new_width, current_height):
        # Open a dialog to get new canvas height, pre-populated with the current height
        new_height = simpledialog.askinteger(
            "Canvas Height", 
            "Enter new canvas height:", 
            parent=self.root, 
            minvalue=100, 
            initialvalue=current_height
        )

        # If the user cancels the height dialog, stop here
        if new_height is None:
            return

        # Update the canvas size and scroll region
        self.canvas.config(width=new_width, height=new_height, scrollregion=(0, 0, new_width, new_height))

    def add_text_bubble(self):
        text = simpledialog.askstring("Input", "Enter text for the bubble:", parent=self.root)
        if text:
            # Place the new bubble in the center of the canvas
            x = (self.canvas.winfo_width() // 2) - 50
            y = (self.canvas.winfo_height() // 2) - 25
            bubble = TextBubble(self.canvas, x, y, text, id=self.next_bubble_id, app=self)
            self.next_bubble_id += 1
            self.text_bubbles.append(bubble)

    def start_line(self, event):
        # Find the text bubble clicked on
        for bubble in self.text_bubbles:
            x1, y1, x2, y2 = bubble.get_position()
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.right_click_start_bubble = bubble  # Track the bubble
                self.start_bubble = bubble
                break

    def draw_line(self, event):
        if self.start_bubble and not self.current_line:
            self.current_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill="black", width=2)

    def end_line(self, event):
        if self.start_bubble and self.current_line:
            # Find the text bubble released on
            for bubble in self.text_bubbles:
                x1, y1, x2, y2 = bubble.get_position()
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    if bubble != self.start_bubble:
                        # Create a connection line
                        line = ConnectionLine(self.canvas, self.start_bubble, bubble)
                        self.lines.append(line)
                    else:
                        # If released on the same bubble, open the context menu
                        self.selected_bubble = bubble
                        self.show_canvas_context_menu(event)
                    break
            self.current_line = None
            self.start_bubble = None
            self.right_click_start_bubble = None  # Reset tracking

    def save_canvas(self):
        if self.last_loaded_file_path:
            # Save to the last loaded file path
            self._save_canvas_to_file(self.last_loaded_file_path)
        else:
            # Prompt the user to choose a file path
            self.save_as_canvas()

    def save_as_canvas(self):
        # Prompt the user to choose a file path
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self._save_canvas_to_file(file_path)
            self.last_loaded_file_path = file_path  # Update the last loaded file path

    def _save_canvas_to_file(self, file_path):
        # Serialize the canvas state
        canvas_state = {
            "canvas_width": self.canvas.winfo_width(),  # Save canvas width
            "canvas_height": self.canvas.winfo_height(),  # Save canvas height
            "text_bubbles": [],
            "connections": [],
        }

        # Save text bubbles
        for bubble in self.text_bubbles:
            x1, y1, x2, y2 = bubble.get_position()
            canvas_state["text_bubbles"].append({
                "id": bubble.id,
                "x": x1,
                "y": y1,
                "width": bubble.width,
                "height": bubble.height,
                "text": bubble.text,
                "font_size": bubble.font_size,
            })

        # Save connections
        for line in self.lines:
            canvas_state["connections"].append({
                "start_id": line.start_bubble.id,
                "end_id": line.end_bubble.id,
            })

        # Save to the file
        try:
            with open(file_path, "w") as f:
                json.dump(canvas_state, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            
    def new_canvas(self):
        self.canvas.delete("all")
        self.text_bubbles = []
        self.lines = []
        self.next_bubble_id = 0
        self.last_loaded_file_path = ""
        self.root.title("yuruCanvas")

    def load_canvas(self):
        # Load the canvas state from a file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        print(file_path)
        if file_path:
            self.load_canvas_from_file(file_path)
            self.last_loaded_file_path = file_path  # Update the last loaded file path

    def load_canvas_from_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                canvas_state = json.load(f)

            # Clear the current canvas
            self.canvas.delete("all")
            self.text_bubbles = []
            self.lines = []
            self.next_bubble_id = 0
            
            self.root.title("yuruCanvas - " + file_path)  # Set the window title

            # Recreate text bubbles
            id_to_bubble = {}
            for bubble_data in canvas_state["text_bubbles"]:
                bubble = TextBubble(
                    self.canvas, bubble_data["x"], bubble_data["y"], bubble_data["text"],
                    width=bubble_data["width"], height=bubble_data["height"], id=bubble_data["id"], app=self
                )
                # Set the font size and update the label
                bubble.font_size = bubble_data.get("font_size", 12)  # Default to 12 if not present
                self.canvas.itemconfig(bubble.label, font=("Arial", bubble.font_size))  # Apply the font size
                self.text_bubbles.append(bubble)
                id_to_bubble[bubble_data["id"]] = bubble
                if bubble_data["id"] >= self.next_bubble_id:
                    self.next_bubble_id = bubble_data["id"] + 1

            # Recreate connections
            for connection in canvas_state["connections"]:
                start_bubble = id_to_bubble[connection["start_id"]]
                end_bubble = id_to_bubble[connection["end_id"]]
                line = ConnectionLine(self.canvas, start_bubble, end_bubble)
                self.lines.append(line)

            # Update the canvas size and scroll region based on the loaded content
            canvas_width = canvas_state.get("canvas_width", 800)  # Default to 800 if not present
            canvas_height = canvas_state.get("canvas_height", 600)  # Default to 600 if not present
            self.canvas.config(width=canvas_width, height=canvas_height)

            # Update the scroll region based on the loaded content
            max_x = max(bubble.get_position()[2] for bubble in self.text_bubbles) if self.text_bubbles else canvas_width
            max_y = max(bubble.get_position()[3] for bubble in self.text_bubbles) if self.text_bubbles else canvas_height
            self.canvas.config(scrollregion=(0, 0, max_x, max_y))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def on_drop(self, event):
        # Handle file drop event
        file_path = event.data.strip("{}")  # Remove curly braces added by tkinterdnd2
        if file_path.lower().endswith(".json"):
            self.load_canvas_from_file(file_path)
            self.last_loaded_file_path = file_path  # Update the last loaded file path
        else:
            messagebox.showerror("Error", "Only JSON files are supported.")

    def open_debug_window(self):
        # Create a new window for debugging
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Debug Window")
        debug_window.geometry("400x300")  # Set a fixed width for the debug window

        # Center the debug window on the parent window
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        window_width = 400  # Width of the debug window
        window_height = 300  # Height of the debug window

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        debug_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create a listbox to display text bubbles
        listbox = tk.Listbox(debug_window)
        listbox.pack(fill=tk.BOTH, expand=True)

        # Populate the listbox with text bubbles
        for bubble in self.text_bubbles:
            listbox.insert(tk.END, bubble.text)

        # Add a context menu for listbox items
        context_menu = tk.Menu(listbox, tearoff=0)
        context_menu.add_command(label="Reset Position to Center", command=lambda: self.reset_bubble_position(listbox))
        context_menu.add_command(label="Delete All Connections", command=lambda: self.delete_bubble_connections(listbox))

        # Bind right-click to open the context menu
        listbox.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu))

    def show_context_menu(self, event, menu):
        # Show the context menu at the cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def reset_bubble_position(self, listbox):
        # Reset the selected bubble's position to the center
        selected_index = listbox.curselection()
        if selected_index:
            bubble = self.text_bubbles[selected_index[0]]
            bubble.reset_position()

    def delete_bubble_connections(self, listbox):
        # Delete all connections for the selected bubble
        selected_index = listbox.curselection()
        if selected_index:
            bubble = self.text_bubbles[selected_index[0]]
            # Remove lines from the global list
            for line in bubble.lines:
                if line in self.lines:
                    self.lines.remove(line)
            bubble.delete_all_connections()

    def setup_canvas_context_menu(self):
        # Create a context menu for the canvas
        self.canvas_context_menu = tk.Menu(self.canvas, tearoff=0)
        self.canvas_context_menu.add_command(label="Edit Text", command=self.edit_selected_bubble)
        self.canvas_context_menu.add_command(label="Delete Bubble", command=self.delete_selected_bubble)
        self.canvas_context_menu.add_command(label="Delete Connections", command=self.delete_selected_bubble_connections)

        # Bind right-click press and release events
        self.canvas.bind("<Button-3>", self.start_line)  # Right-click press
        self.canvas.bind("<ButtonRelease-3>", self.end_line)  # Right-click release

    def show_canvas_context_menu(self, event):
        # Show the context menu at the cursor position
        if self.selected_bubble:
            try:
                self.canvas_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.canvas_context_menu.grab_release()

    def edit_selected_bubble(self):
        if self.selected_bubble:
            self.selected_bubble.edit_text(None)  # Call the edit_text function

    def delete_selected_bubble(self):
        if self.selected_bubble:
            # Delete all connections first
            self.selected_bubble.delete_all_connections()
            # Remove the bubble from the canvas
            self.canvas.delete(self.selected_bubble.rect)
            self.canvas.delete(self.selected_bubble.label)
            for handle in self.selected_bubble.resize_handles:
                self.canvas.delete(handle)
            # Remove the bubble from the list
            self.text_bubbles.remove(self.selected_bubble)

    def delete_selected_bubble_connections(self):
        if self.selected_bubble:
            self.selected_bubble.delete_all_connections()

if __name__ == "__main__":
    # Use TkinterDnD for the root window
    root = TkinterDnD.Tk()
    # Check for file argument
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = CanvasApp(root, file_path)
    root.mainloop()