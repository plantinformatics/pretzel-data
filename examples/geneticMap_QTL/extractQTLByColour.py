'''
Question:26
Thanks. I have run that script and it extracts the Marker table successfully, although not the QTL information.
In this section : `    # Match QTL names to start & end markers`
the script tries to match QTL names with Marker names, which is not going to work because there is no name correspondence between QTLs and Markers.
In the image, a QTL name is shown in the same colour as its start and end markers.  This is probably the easiest way to extract that relationship.
Each chromosome genetic map has 1 or 2 QTLs, and the colours used for them are :
```
#e1321f	red QTL
#2f2c57	blue QTL
```
Those colours will vary slightly, so we should filter for colours close to those.

We can mask the image for the red text, and extract the information for one QTL, then repeat for the blue text, for the other QTL.
If the image has only 1 QTL it may be either red or blue.
It is possible to have 3 QTLs, with 2 having the same colour; in this case you can associate the first QTL name with the first 2 marker names, and the 2nd QTL name with the 3rd and 4th marker names.
I'll upload an image which I have applied super-resolution to. You should not apply cv2.COLOR_BGR2GRAY to convert the image to grayscale, because the colour information is required.


Here's a **Python script** to extract **QTL information** from a **single-chromosome genetic map image** by detecting colored QTL names and their corresponding markers.

### **Python Script: Extract QTL Information Based on Color**
```python
'''

import cv2
import pytesseract
import numpy as np
import pandas as pd

def extract_qtl_from_image(image_path):
    """
    Extracts QTL names and their associated markers from a chromosome genetic map image.
    
    Args:
        image_path (str): Path to the chromosome image file.
    
    Returns:
        pd.DataFrame: DataFrame containing QTL information:
                      ["Chromosome", "QTL Name", "Start Marker", "End Marker"]
    """

    # Extract chromosome name from filename (e.g., "4A.png" → "4A")
    chromosome_name = image_path.split("/")[-1].replace(".png", "")

    # Load image
    image = cv2.imread(image_path)

    # Convert image to HSV color space (better for color filtering)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define HSV color ranges for detecting red and blue QTL labels
    lower_red1, upper_red1 = np.array([0, 100, 100]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([170, 100, 100]), np.array([180, 255, 255])
    lower_blue, upper_blue = np.array([110, 50, 50]), np.array([130, 255, 255])

    # Create masks for red and blue QTL labels
    mask_red1, mask_red2 = cv2.inRange(hsv_img, lower_red1, upper_red1), cv2.inRange(hsv_img, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv_img, lower_blue, upper_blue)

    # Combine red masks
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Extract QTL name regions using masks
    qtl_red_region = cv2.bitwise_and(image, image, mask=mask_red)
    # cv2.imshow("red", qtl_red_region)
    qtl_blue_region = cv2.bitwise_and(image, image, mask=mask_blue)
    # cv2.imshow("blue", qtl_blue_region)

    # Perform OCR on extracted QTL name regions
    qtl_red_text = pytesseract.image_to_string(qtl_red_region, config="--psm 5 --oem 1")
    qtl_blue_text = pytesseract.image_to_string(qtl_blue_region, config="--psm 5 --oem 1")
    print ('red', qtl_red_text);
    print ('blue', qtl_blue_text);
    # ... 1 for marker names
    marker_red_text = pytesseract.image_to_string(qtl_red_region, config="--psm 1 --oem 1")
    marker_blue_text = pytesseract.image_to_string(qtl_blue_region, config="--psm 1 --oem 1")
    print ('red', marker_red_text);
    print ('blue', marker_blue_text);


    # Extract QTL names from OCR results
    qtl_red_names = [line.strip() for line in qtl_red_text.split("\n") if "Q" in line and "cas" in line]
    qtl_blue_names = [line.strip() for line in qtl_blue_text.split("\n") if "Q" in line and "cas" in line]

    # Extract markers from full image OCR
    ocr_text = pytesseract.image_to_string(image, config="--psm 1 --oem 1")
    marker_data = []
    
    for line in ocr_text.split("\n"):
        parts = line.strip().split()
        if len(parts) > 1 and parts[0].replace(".", "", 1).isdigit():
            try:
                position = float(parts[0])
                marker_name = " ".join(parts[1:])
                marker_data.append((position, marker_name))
            except ValueError:
                continue

    marker_df = pd.DataFrame(marker_data, columns=["Position", "Marker Name"])

    # Associate QTLs with their closest markers
    qtl_table = []
    
    def match_qtl_to_markers(qtl_names, color_label):
        """ Matches QTL names to markers based on proximity in the image. """
        if len(qtl_names) == 0:
            return
        
        qtl_markers = marker_df[marker_df["Marker Name"].str.contains("_", regex=False, na=False)]
        qtl_markers = qtl_markers.sort_values(by="Position").reset_index(drop=True)

        # Assign each QTL to two consecutive markers
        for i, qtl_name in enumerate(qtl_names):
            if i * 2 + 1 < len(qtl_markers):
                start_marker = qtl_markers.iloc[i * 2]["Marker Name"]
                end_marker = qtl_markers.iloc[i * 2 + 1]["Marker Name"]
                start_position = qtl_markers.iloc[i * 2]["Position"]
                end_position = qtl_markers.iloc[i * 2 + 1]["Position"]
                qtl_table.append((chromosome_name, qtl_name, start_marker, end_marker, start_position, end_position, color_label))

    # Match QTLs with markers
    match_qtl_to_markers(qtl_red_names, "Red")
    match_qtl_to_markers(qtl_blue_names, "Blue")

    # Convert to DataFrame
    qtl_df = pd.DataFrame(qtl_table, columns=["Chromosome", "QTL Name", "Start Marker", "End Marker", "Start Position", "End Position", "Color"])
    
    return qtl_df

# Example Usage:
qtl_table = extract_qtl_from_image("4A.png")
qtl_table.to_csv("QTL_Table_4A.csv", index=False)  # Save as CSV
print(qtl_table)
'''
```

---

### **How This Script Works**
1. **Detects red and blue QTL names** by filtering the image using **HSV color thresholds**.
2. **Applies OCR** to extract **QTL names from the color-masked regions**.
3. **Performs OCR on the full image** to extract **marker names and positions**.
4. **Matches QTL names to their closest markers** to determine **start and end positions**.
5. **Outputs a structured QTL Table** with **chromosome, QTL name, start marker, end marker, start position, end position, and color**.

### **How to Use**
1. **Run the script** in Python.
2. **Replace `"4A.png"`** with any chromosome image.
3. **Get the output CSV file (`QTL_Table_4A.csv`)**.


'''
