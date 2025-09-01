import cv2
from data_types import AdvancedOptions
from matplotlib import pyplot as plt


def determineKeyLocations(
    frame, advancedOptions: AdvancedOptions
) -> list[tuple[int, int]]:
    cv2.line(
        frame,
        (0, frame.shape[0] - int(frame.shape[0] * advancedOptions.keyOffset / 100)),
        (
            frame.shape[1],
            frame.shape[0] - int(frame.shape[0] * advancedOptions.keyOffset / 100),
        ),
        (0, 0, 255),
        2,
    )
    cv2.imshow("Frame", frame)
    waitKey = cv2.waitKey(0)
    return


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
