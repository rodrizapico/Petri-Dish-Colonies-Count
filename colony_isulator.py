import cv2
import numpy as np

def colonyIsolator(source, Xoffset, Yoffset, radius):
    # Store a copy of the image in RGB and grayscale
    original = source.copy()
    image_GS = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    center = (int(image_GS.shape[1] / 2 + Xoffset), int(image_GS.shape[0] / 2 + Yoffset))

    # Create a circular mask and apply it to the image in grayscale and RGB
    circularmask = np.zeros(image_GS.shape[:2], dtype="uint8")
    cv2.circle(circularmask, center, radius, 255, -1)
    masked_GS = cv2.bitwise_and(image_GS, image_GS, mask=circularmask)
    masked_RGB = cv2.bitwise_and(original, original, mask=circularmask)

    # Substract noise from the grayscale image and use it to generate a mask
    blurred = cv2.bilateralFilter(masked_GS, 9, 100, 100)
    threshInv = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 6)

    # Apply isolating mask to the image in grayscale and RGB
    isolated_RGB = cv2.bitwise_and(masked_RGB, masked_RGB, mask=threshInv)
    isolated_GS = cv2.bitwise_and(masked_GS, masked_GS, mask=threshInv)

    return isolated_RGB, isolated_GS

# -- TEST --   (hardcoded)

image = cv2.imread("colonias.jpg")
image = cv2.resize(image, (int(image.shape[1]/5), int(image.shape[0]/5)))

processed_RGB, processed_GS = colonyIsolator(image, -25, 0, 260)
cv2.imshow("Image", image)
cv2.imshow("Processed Image GS", processed_GS)
cv2.imshow("Processed Image RGB", processed_RGB)


cv2.waitKey(0)
