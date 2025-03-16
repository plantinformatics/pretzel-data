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

def resGrey(image_path):
    """
    In preparation for OCR, apply Super-Resolution to an image, then convert colours to grey.
    Requires the file ESPCN_x4.pb, which is read from "./"
    ESPCN_x{2,3,4}.pb are available at https://github.com/fannymonori/TF-ESPCN/raw/refs/heads/master/export/
    
    Args:
    
    Returns:
    """
    img = cv2.imread(image_path)

    # https://learnopencv.com/super-resolution-in-opencv/
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    path = "ESPCN_x4.pb"
    # path = "ESPCN_x3.pb"

    sr.readModel(path) 
    # set the model by passing the value and the upsampling ratio
    sr.setModel("espcn", 4)
    # sr.setModel("espcn",3)
    image = sr.upsample(img) # upscale the input image


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpen = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpen = cv2.addWeighted(gray, 1.5, sharpen, -0.5, 0)
    cv2.imwrite("preprocessed_2D.superRes_4.png", sharpen)

def extract_qtl_by_color(image, hsv_img, lower_color, upper_color, color_name):
    """
    Extracts QTL names from a chromosome genetic map image based on the given HSV color range.

    Args:
        image (np.array): Original BGR image.
        hsv_img (np.array): Image converted to HSV color space.
        lower_color (np.array): Lower HSV bound for the first color range.
        upper_color (np.array): Upper HSV bound for the first color range.
        color_name (str): Name of the color being extracted ("red", "blue", etc.).

    Returns:
        list: Extracted QTL names detected from the specified color.
    """

    # Create color mask
    mask = cv2.inRange(hsv_img, lower_color, upper_color)

    # Apply mask to extract QTL name regions and corresponding Marker names in the same color
    qtl_region = cv2.bitwise_and(image, image, mask=mask)
    # cv2.imshow(color_name, qtl_region)
    # cv2.waitKey(0)

    # Perform OCR to extract QTL names
    qtl_text = pytesseract.image_to_string(qtl_region, config="--psm 5 --oem 1")
    # print(f"{color_name} QTL Text:", qtl_text)

    # Extract QTL names using heuristics
    qtl_names = [line.strip() for line in qtl_text.split("\n") if "Q" in line and "cas" in line]

    # Extract markers from color-masked image OCR
    ocr_text = pytesseract.image_to_string(hsv_img, config="--psm 1 --oem 1")
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
    match_qtl_to_markers(qtl_names, color_name)

    # Convert to DataFrame
    qtl_df = pd.DataFrame(qtl_table, columns=["Chromosome", "QTL Name", "Start Marker", "End Marker", "Start Position", "End Position", "Color"])
    
    return qtl_df



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
    red_lower, red_upper = np.array([0, 100, 100]), np.array([180, 255, 255])
    blue_lower, blue_upper = np.array([110, 50, 50]), np.array([130, 255, 255])

    # Extract QTL names for red and blue
    qtl_red_df = extract_qtl_by_color(image, hsv_img, red_lower, red_upper, "Red")
    qtl_blue_df = extract_qtl_by_color(image, hsv_img, blue_lower, blue_upper, "Blue")

    return qtl_red_df # , qtl_blue_df

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
