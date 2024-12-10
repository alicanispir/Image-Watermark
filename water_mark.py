from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont

# ---------------------------- CONSTANTS ------------------------------- #

LIGHT_GRAY = "#d3d3d3"
DARK_GRAY = "#a9a9a9"

# ---------------------------- LIMITS FOR THE UPLOADED PICTURE ------------------------------- #
MAX_WIDTH = 1280  # You can set maximum width
MAX_HEIGHT = 720  # You can set maximum height

# ---------------------------- SETTINGS --------------------------------------#
global image_ok
image_ok = False

# ---------------------------- UPLOAD FUNCTION ------------------------------- #
def upload_image():
    global original_image, modified_image, backup_image, image_ok
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if file_path:
        original_image = Image.open(file_path)

        original_width, original_height = original_image.size

        scaling_factor = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height, 1)

        if scaling_factor < 1:
            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)
            modified_image = original_image.resize((new_width, new_height), Image.LANCZOS)
        else:
            modified_image = original_image

        backup_image = modified_image.copy()

        uploaded_img = ImageTk.PhotoImage(modified_image)

        canvas.config(width=uploaded_img.width(), height=uploaded_img.height())
        canvas.create_image(uploaded_img.width() // 2, uploaded_img.height() // 2, image=uploaded_img)
        canvas.image = uploaded_img

        image_ok = True
        picture_upload_label.grid_forget()

# ---------------------------- ADDING FUNCTIONS ------------------------ #
def add_watermark():
    global image_ok
    watermark = watermark_input.get()
    fontsize = fontsize_input.get()
    selected_font = dropdown_font_type.get()
    not_allowed = False
    if len(watermark) == 0 or len(fontsize) == 0 or selected_font == "Fonts":
        not_allowed = True
        messagebox.showerror(title="Oops", message="Please don't leave any fields box empty!")
    else:
        is_ok = messagebox.askokcancel(title=watermark,
                                       message=f"These are the details entered: \nWatermark: {watermark} \nFont size and type are: {fontsize} and {selected_font} \nIs it ok to generate the watermark on your picture?")
        if is_ok:
            dropdown_watermark.grid(column=0, row=5)
            dropdown_watermark.config(state="normal")


def generate_watermark(option):
    global modified_image
    if modified_image is not None:
        draw = ImageDraw.Draw(modified_image)
        watermark = watermark_input.get()
        selected_font = dropdown_font_type.get()
        font_path = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Calibri": "calibri.ttf",
        }
        font_size = int(fontsize_input.get())
        font = ImageFont.truetype(font_path[selected_font], font_size)

        # Calculate the bounding box for the text
        text_bbox = draw.textbbox((0, 0), watermark, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if option == 1:
            x = 10
            y = 10
            draw.text((x, y), watermark, fill="black", font=font)
        elif option == 2:
            x = 10
            y = modified_image.height - text_height - 10
            draw.text((x, y), watermark, fill="black", font=font)
        elif option == 3:
            x = modified_image.width - text_width - 10
            y = modified_image.height - text_height - 10
            draw.text((x, y), watermark, fill="black", font=font)
        elif option == 4:
            for y in range(0, modified_image.height, text_height + 40):
                for x in range(0, modified_image.width, text_width + 40):
                    draw.text((x, y), watermark, fill="gray", font=font)

        uploaded_img = ImageTk.PhotoImage(modified_image)
        canvas.create_image(uploaded_img.width() // 2, uploaded_img.height() // 2, image=uploaded_img)
        canvas.image = uploaded_img  # Keep a reference to avoid garbage collection
    else:
        messagebox.showerror(title="Error", message="No image uploaded to add watermark.")


def on_dropdown_select(event):
    global image_ok
    if image_ok == False:
        messagebox.showerror(title="Error", message="No image uploaded to add watermark. \nPlease upload an image and press on the add button again!")
    elif dropdown_watermark.current() != -1:
        clear_watermark()
        messagebox.showinfo(title="Info", message=f"{dropdown_watermark.current() + 1}. option is selected!")
        generate_watermark(option=dropdown_watermark.current() + 1)
        download_button.grid(column=2, row=5)
        clear_button.grid(column=1, row=5)

def download_watermark():
    if modified_image is not None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp")],
            title="Save watermarked image"
        )
        if file_path:
            try:
                modified_image.save(file_path)
                messagebox.showinfo(title="Success", message="Image saved successfully!")
            except Exception as e:
                messagebox.showerror(title="Error", message=f"Failed to save image. {e}")
    else:
        messagebox.showerror(title="Error", message="No watermarked image to save.")


def clear_watermark():
    global backup_image, modified_image
    if backup_image is not None:
        modified_image = backup_image.copy()
        uploaded_img = ImageTk.PhotoImage(modified_image)
        canvas.config(width=uploaded_img.width(), height=uploaded_img.height())
        canvas.create_image(uploaded_img.width() // 2, uploaded_img.height() // 2, image=uploaded_img)
        canvas.image = uploaded_img


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Add Your Watermark")
window.config(padx=100, pady=50, bg=LIGHT_GRAY)

canvas = Canvas(bg=DARK_GRAY, highlightthickness=0)
canvas.grid(column=1, row=1)

# Font type label
picture_upload_label = Label(text="Upload your \npicture here!", width=20, height=2, font=("Arial", 14), bg=DARK_GRAY)
picture_upload_label.grid(column=1, row=1)

Upload_button = Button(text="Upload", command=upload_image, highlightthickness=0)
Upload_button.grid(column=1, row=2)

add_watermark_button = Button(text="Add your watermark", command=add_watermark, highlightthickness=0)
add_watermark_button.grid(column=2, row=4)

watermark_input = Entry(width=15, font=("Arial", 16), bg="white")
watermark_input.grid(column=2, row=3)

# Dropdown (Combobox) options
options = ["Option 1", "Option 2", "Option 3", "Option 4"]

# Create Combobox
dropdown_watermark = ttk.Combobox(window, values=options)
dropdown_watermark.grid(column=0, row=5)
dropdown_watermark.set("WaterMark Options")
dropdown_watermark.config(state="disabled")

# Bind the dropdown selection event
dropdown_watermark.bind("<<ComboboxSelected>>", on_dropdown_select)

# Font type label
FontSize_label = Label(text="Pick up a font type 👇🏼", width=20, height=1, font=("Arial", 14), bg=DARK_GRAY)
FontSize_label.grid(column=0, row=3)

options_font = ["Arial", "Times New Roman", "Calibri"]

# Create Combobox
dropdown_font_type = ttk.Combobox(window, values=options_font)
dropdown_font_type.grid(column=0, row=4)
dropdown_font_type.set("Fonts")

# Font size label
FontSize_label = Label(text="Determine font size 👇🏼", width=20, height=1, font=("Arial", 14), bg=DARK_GRAY)
FontSize_label.grid(column=1, row=3)

fontsize_input = Entry(width=15, font=("Arial", 16), bg="white")
fontsize_input.grid(column=1, row=4)

#Download button
download_button = Button(text="Download", command=download_watermark, highlightthickness=0)
download_button.grid(column=2, row=5)
download_button.grid_forget()

clear_button = Button(text="Clear", command=clear_watermark, highlightthickness=0)
clear_button.grid(column=1, row=5)
clear_button.grid_forget()

window.mainloop()
