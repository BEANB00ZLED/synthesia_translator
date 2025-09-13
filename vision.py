import cv2
from data_types import AdvancedOptions
from matplotlib import pyplot as plt
import numpy as np


def determineKeyLocations(
    frame: cv2.typing.MatLike, advancedOptions: AdvancedOptions
) -> list[tuple[int, int]]:
    frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)
    keySlice = [
        int(pixel[2])
        for pixel in frame[
            frame.shape[0] - int(frame.shape[0] * advancedOptions.keyOffset / 100)
        ]
    ]
    keyBoundaries = []
    leftEdge = 0
    i = 0
    windowSize = 3
    isSettled = False
    while i < len(keySlice) - windowSize + 1:
        window = keySlice[i : i + windowSize]
        maxDiff = max(window) - min(window)
        # If there is a big jump in value, assume edge of key
        if maxDiff >= advancedOptions.keyDifferenceThreshold and isSettled:
            keyBoundaries.append((leftEdge, i + 1))
            leftEdge = i
            isSettled = False
        elif maxDiff <= advancedOptions.keyDifferenceThreshold and not isSettled:
            isSettled = True
            leftEdge = i
        i += 1
    keyBoundaries.append((leftEdge, len(keySlice) - 1))
    keyLocations = [
        (
            (keyBoundary[1] + keyBoundary[0]) // 2,
            frame.shape[0] - int(frame.shape[0] * advancedOptions.keyOffset / 100),
        )
        for keyBoundary in keyBoundaries
    ]
    return keyLocations


def readKeys(
    video: cv2.VideoCapture,
    keyLocations: list[tuple[int, int]],
    advancedOptions: AdvancedOptions,
):
    pass


def transcribeVideo():
    pass


def main():
    videoCapture = cv2.VideoCapture("./Hercules -.mp4")
    if not videoCapture.isOpened():
        print("Error: Unable to open video file.")
        return
    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, 1000)
    ret, frame = videoCapture.read()
    if not ret:
        print("Error: Unable to read frame.")
        return
    advanced_options = AdvancedOptions()
    keyLocations = determineKeyLocations(frame, advanced_options)
    videoCapture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
