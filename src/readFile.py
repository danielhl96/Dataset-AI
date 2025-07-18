import re
import argparse
import cv2
from unicodedata import numeric

def readFile(path):
    results = []
    boxes = []
    current_name = ""
    status = 0
    w = h = 0
    expected_count = -1
    index = 0

    with open(path, 'r') as data_file:
        for line in data_file:
            line = line.strip()

            # Breite und Höhe auslesen
            if line.startswith("w:"):
                try:
                    values = line.split(',')
                    w, h = [int(part.split(':')[1]) for part in values]
                except (IndexError, ValueError):
                    print(f"Fehler beim Parsen von Breite/Höhe: {line}")

            # Name-Zeile (z. B. Pfad)
            elif line.startswith("C:"):
                current_name = line

            # Status-Zeile
            elif "Status:" in line:
                try:
                    status = int(line.split(":")[1])
                except (IndexError, ValueError):
                    print(f"Fehler beim Parsen von Status: {line}")

            # Index-Zeile (Anzahl erwarteter Boxen)
            elif "index=" in line:
                try:
                    expected_count = int(line.split("=")[1])
                    index = 0
                    boxes = []
                except (IndexError, ValueError):
                    print(f"Fehler beim Parsen von Index: {line}")

            # Box-Zeile
            elif expected_count >= 0 and "," in line:
                try:
                    x, y, bw, bh = [int(val) for val in line.split(',')]
                    boxes.append((x, y, bw, bh))
                    index += 1
                except ValueError:
                    print(f"Fehler beim Parsen einer Box: {line}")

            # Wenn alle Boxen gelesen wurden
            if expected_count >= 0 and index == expected_count:
                results.append({
                    "name": current_name,
                    "box": boxes,
                    "status": status,
                    "w": w,
                    "h": h
                })
                boxes = []
                index = 0
                expected_count = -1

    return results

    
def display_list(s):
    w = 350
    h = 350
    dim = (w,h)
    for i in range(0,len(s)):
        img = cv2.imread(s[i]["name"])
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        for j in range(0,len(s[i]["box"])):
            list =s[i]["box"][j]
            for k in range(0,len(list)):
                cv2.rectangle(img,(list[0],list[1]),(list[2],list[3]),color =(0, 255, 255),thickness =1)
        while True:
            cv2.imshow("Title of Popup Window", img)
            if cv2.waitKey(10) == 27:
                break  
    cv2.destroyAllWindows()    
