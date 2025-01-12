import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import csv
import os
import pandas as pd
from pygam import LinearGAM

def uncurve_text(input_path, output_path, n_splines = 5):
  # Load image, grayscale it, Otsu's threshold
  image = cv2.imread(input_path)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

  # Dilation & Erosion to fill holes inside the letters
  kernel = np.ones((3, 3), np.uint8)
  thresh = cv2.erode(thresh, kernel, iterations=1)
  thresh = cv2.dilate(thresh, kernel, iterations=1)

  black_pixels = np.where(thresh == 0)
  leftmost_x = np.min(black_pixels[1])
  rightmost_x = np.max(black_pixels[1])

  # Open csv file
  f = open('./scatterplot_records.csv', 'w')

  # Create the csv writer
  writer = csv.writer(f)
  writer.writerow(['X', 'Y'])

  # Write in csv file
  for x in range(thresh.shape[0]):
    for y in range(leftmost_x, rightmost_x):
      # Search for black pixels
      if (thresh[x][y] <= 128):
        #writer.writerow([y, x])                        # reverse/mirrored scatter-plot image
        writer.writerow([y, thresh.shape[0] - x])       # normal scatter-plot image

  # Close csv file
  f.close()

  # Read CSV file and extract info
  df = pd.read_csv('./scatterplot_records.csv', sep = ",")

  # Delete csv file
  os.remove('./scatterplot_records.csv')

  # Build GAM & define its parameters
  predictors = ['X']
  outcome = ['Y']
  X = df[predictors].values
  y = df[outcome]
  gam = LinearGAM(n_splines = n_splines)
  gam.gridsearch(X, y)

  # Create the offset necessary to un-curve the text
  y_hat = gam.predict(np.linspace(leftmost_x, rightmost_x - 1, num = rightmost_x - leftmost_x))

  # Plot the image with text curve overlay
  plt.imshow(image[:,:,::-1])
  plt.plot(np.linspace(leftmost_x, rightmost_x - 1, num = rightmost_x - leftmost_x), (thresh.shape[0] - y_hat), color='red')
  plt.show()

  # Roll each column to align the text
  for i in range(leftmost_x, rightmost_x):
    image[:, i, 0] = np.roll(image[:, i, 0], round(y_hat[i - leftmost_x] - thresh.shape[0]/2))
    image[:, i, 1] = np.roll(image[:, i, 1], round(y_hat[i - leftmost_x] - thresh.shape[0]/2))
    image[:, i, 2] = np.roll(image[:, i, 2], round(y_hat[i - leftmost_x] - thresh.shape[0]/2))

  # Plot the final image
  plt.imshow(image[:,:,::-1])
  plt.show()

  # Save image to desired directory
  cv2.imwrite(output_path, image)

if __name__ == "__main__":
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    uncurve_text(input_path, output_path)
