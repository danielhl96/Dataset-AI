import cv2
import argparse
import os
import numpy as np
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button,Entry,Scale,Radiobutton
import subprocess
from filedialogs import save_file_dialog, open_file_dialog, open_folder_dialog
from readFile import readFile




ix, iy = -1, -1
drawing = False
finalList = []
name = ""
selected_mode = None

img = None
copyImg = None
img_display = None

def draw_rectangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, img_display, copyImg, finalList
    id = 0
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        
        for rect in finalList:
            xp1,yp1 = rect[0]
            xp2,yp2 = rect[1]
            if is_point_in_rect(ix,iy,xp1,yp1,xp2,yp2) == True:
                finalList.pop(id)
            id+=1

   
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_display = copyImg.copy()
            #draw the previous rectangles 
            for rect in finalList:
                cv2.rectangle(img_display, rect[0], rect[1], (0, 255, 0), 2)
            #draw new rectangle
            cv2.rectangle(img_display, (ix, iy), (x, y), (0, 0, 255), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if(x-ix > 5):
            finalList.append(((ix, iy), (x, y)))
        img_display = copyImg.copy()
        for rect in finalList:
            cv2.rectangle(img_display, rect[0], rect[1], (0, 255, 0), 2)

#Show pictures and start callback function
def showPictures():
    global img_display, copyImg, finalList
    cv2.namedWindow("Title of Popup Window")
    cv2.setMouseCallback("Title of Popup Window", draw_rectangle_with_drag)

    while True:
        cv2.imshow("Title of Popup Window", img_display)
        key = cv2.waitKey(10)

        if key == 27:  # ESC
            print("Finale Liste:", finalList)
            break
        elif key == ord('d'):
            if finalList:
                finalList.pop()
                img_display = copyImg.copy()
                for rect in finalList:
                    cv2.rectangle(img_display, rect[0], rect[1], (0, 255, 0), 2)

    cv2.destroyAllWindows()


# Write the coordinates and path, status and index in file
def write_file(path,mode):
    global finalList
    with open(name, mode) as f:
        f.write(path + '\n')
        f.write("w:"+ str(w) + ",""h:" + str(h) + "\n")
        if len(finalList) == 0:
            f.write("index=1\n")
            f.write("0,0,0,0\n")
            f.write("Status:0\n") #0: There is no object
        else:
            f.write(f"index={len(finalList)}\n") #Count the objects
            for rect in finalList:
                x1, y1 = rect[0]
                x2, y2 = rect[1]
                f.write(f"{x1},{y1},{x2},{y2}\n")
                f.write("Status:1\n") #1: There is the object
    finalList.clear()
# Read the picture
def readImg(path):
    global img, copyImg, img_display, finalList,w,h,selected_mode

    dim = (w, h)
    imgList = [x for x in os.listdir(path) if x.lower().endswith((".jpg", ".jpeg",".png"))]
    print(f"{len(imgList)} Found pictures")

    for idx, filename in enumerate(imgList):
        full_path = os.path.join(path, filename)
        img = cv2.imread(full_path)
        if img is None:
            print(f"Picture could not load: {filename}")
            continue

        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        copyImg = img.copy()
        img_display = img.copy()
        finalList.clear()
        print(f"[{idx+1}/{len(imgList)}] Work on: {filename}")
        showPictures()
        if selected_mode.get() == "Default":
            write_file(full_path,"a")
        else:
            write_yolo(finalList,filename)
       
        print(f"Progress: {((idx + 1) / len(imgList)) * 100:.2f}%")

def read_consist_data(list):
    global img_display, copyImg,w,h,name,finalList
    print(list)
    os.remove(name)
    for elem in list:
        imgname = elem["name"]
        img = cv2.imread(imgname)
        w = elem["w"]
        h = elem["h"]
        img = cv2.resize(img, (int(w),int(h)), interpolation=cv2.INTER_AREA)
        img_display = img.copy()
        copyImg = img.copy()
        for box in elem["box"]:
            x1,y1,x2,y2 = box
            finalList.append(((x1,y1),(x2,y2)))
            cv2.rectangle(img_display, (x1, y1),(x2,y2), (0, 255, 0), 2)
        showPictures()
        write_file(imgname,"a")
    finalList.clear()

def is_point_in_rect(px, py, x1, y1, x2, y2):
    if x1 <= px <= x2 and y1 <= py <= y2:
        return True
    return False

def read_yolo(filename):
    global copyImg, img_display
    print(filename)
    with open(filename, 'r') as data_file:
        for line in data_file:
            yolo_list = line.split(" ")
            status = yolo_list[0]
            x1 = float(yolo_list[1])*float(yolo_list[5])
            x2 = float(yolo_list[3])*float(yolo_list[5])
            y1 = float(yolo_list[2])*float(yolo_list[6])
            y2 = float(yolo_list[4])*float(yolo_list[6])
            imgname = os.path.splitext(filename)[0]
            img_path_png = imgname + ".png"
            img = cv2.imread(img_path_png)
            if img is None:
                img_path_jpg = imgname + ".jpg"
                if os.path.exists(img_path_jpg):
                    img = cv2.imread(img_path_jpg)
    
            img = cv2.resize(img, (int(yolo_list[5]),int(yolo_list[6])), interpolation=cv2.INTER_AREA)
            print(img)
            img_display = img.copy()
            copyImg = img.copy()
            cv2.rectangle(img_display, (int(x1), int(y1)),(int(x2),int(y2)), (0, 255, 0), 2)
            showPictures()
            print(status,x1,x2,y1,y2)

def write_yolo(list,filename):
    yolo_lines = []
    global w,h,name
    open_path = open_folder_dialog()
    for elem in list:
        x1 = elem[0][0]
        y1 = elem[0][1]
        x2 = elem[1][0]
        y2 = elem[1][1]
        x_center = ((x1 + x2) / 2) / w
        y_center = ((y1 + y2) / 2) / h
        width = (x2 - x1) / w
        height = (y2 - y1) / h
        class_id = 1
        yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f} {w} {h}"
        yolo_lines.append(yolo_line)
    filename = os.path.splitext(filename)[0]
    filename +=".txt"
    output_path = os.path.join(open_path, filename)
    with open(output_path, "w") as f:
            f.write("\n".join(yolo_lines))

def open_folder(name_entry,w1,h1):
    global name,w,h
    open_folder = open_folder_dialog()
    name = name_entry + ".txt"
    w,h = int(w1),int(h1)
    readImg(open_folder)

def open_file():
    global name, selected_mode
    open_path = open_file_dialog()
    name = os.path.basename(open_path)
    dataset = readFile(open_path)
    read_consist_data(dataset)

def menu():
    global selected_mode
    root = tk.Tk()
    root.title("Annotation")
    root.geometry("400x400")
    style = Style(theme='superhero')
    selected_mode = tk.StringVar()
    selected_mode.set("Default")

    button_width = 20

    # Create a frame for the main menu
    main_menu_frame = tk.Frame(root)
    main_menu_frame.pack(fill='both', expand=True)

    # Function to show the dataset menu
    def show_dataset_menu():
        main_menu_frame.pack_forget()  # Hide the main menu
        dataset_menu_frame.pack(fill='both', expand=True)  # Show dataset menu
    
    def cancel_and_show_main_menu():
        dataset_menu_frame.pack_forget()  # Hide the dataset menu
        main_menu_frame.pack(fill="both", expand=True)  # Show the main menu
        entry.delete(0, tk.END)

    def update_width_label_width(value):
        value = round(float(value)) 
        entry_label_scale.config(text=f"Width: {value}")  # Update the label text with the rounded value

    
    def update_width_label_height(value):
        value = round(float(value))
        entry_label_scale_height.config(text=f"Height: {value}")  # Update the label text with the rounded value

    def forget_data_entry():
        entry_label.config(state="disabled")
        entry.config(state="disabled")

    def pack_entry():
        entry_label.config(state="normal")
        entry.config(state="normal")

    # Button to go to the dataset menu
    entry_label2 = tk.Label(main_menu_frame, text="Create a new dataset:", font=("Arial", 10))
    entry_label2.pack(pady=0)
    button1 = Button(main_menu_frame, text="Create dataset", bootstyle="primary", width=button_width, command=show_dataset_menu)
    button1.pack(pady=10)

    # Button to load dataset
    entry_label3 = tk.Label(main_menu_frame, text="Load an existing dataset:", font=("Arial", 10))
    entry_label3.pack(pady=0)
    button2 = Button(main_menu_frame, text="Load dataset", bootstyle="primary", width=button_width, command=lambda: open_file())
    button2.pack(pady=10)

    # Create a frame for the dataset menu
    dataset_menu_frame = tk.Frame(root)

    entry_label_format = tk.Label(dataset_menu_frame, text="Choose your format:", font=("Arial", 10))
    entry_label_format.pack(pady=5)

    radio_frame = tk.Frame(dataset_menu_frame)
    radio_frame.pack(pady=20)

    radio1 = Radiobutton(radio_frame, text='Default', value="Default", variable=selected_mode, command = pack_entry ,style='Toolbutton')
    radio2 = Radiobutton(radio_frame, text='Yolo', value="Yolo", variable=selected_mode,command = forget_data_entry, style='Toolbutton')
    radio1.pack(side="left", padx=5)
    radio2.pack(side="left", padx=5)

    # Button to open folder (in dataset menu)
    entry_label = tk.Label(dataset_menu_frame, text="Enter dataset name:", font=("Arial", 10))
    entry_label.pack(pady=5)
   

    entry = Entry(dataset_menu_frame, bootstyle="success", width=25)  # width defines horizontal size
    entry.pack(pady=10)

    entry_label_scale = tk.Label(dataset_menu_frame, text="Width:", font=("Arial", 10))
    entry_label_scale.pack(pady=5)
    scale_width = Scale(dataset_menu_frame, command = update_width_label_width, from_=0, to=2000, value=300)
    scale_width.set(500)
    scale_width.pack(fill="x", padx=20)

    entry_label_scale_height = tk.Label(dataset_menu_frame, font=("Arial", 10))
    entry_label_scale_height.pack(pady=5)
    scale_height = Scale(dataset_menu_frame, from_=0, to=2000, value=300,command = update_width_label_height)
    scale_height.set(500)
    scale_height.pack(fill="x", padx=20)

    button_frame = tk.Frame(dataset_menu_frame)
    button_frame.pack(pady=20)
    
    button3 = Button(button_frame, text="Select folder", bootstyle="primary", width=button_width, command=lambda: open_folder(entry.get(),scale_width.get(),scale_height.get()))
    button3.pack(side="left", padx=5)

    # Cancel button
    cancel_button = Button(button_frame, text="Cancel", bootstyle="danger", width=button_width, command=cancel_and_show_main_menu)
    cancel_button.pack(side="left", padx=5)

    root.mainloop()
menu()
