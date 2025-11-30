import cv2
from data_types import AdvancedOptions, PianoKey, Notation
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
import numpy as np
import pandas as pd
from app_logging import logger, LogLevel


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
    debug: bool = False,
) -> pd.DataFrame:
    data = []
    video = video
    while True:
        ret, frame = video.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)
        pianoKeyRange = [
            key for key in PianoKey if key.value >= advancedOptions.startingKey.value
        ]
        if len(keyLocations) != len(pianoKeyRange):
            logger.sendLog(
                "Number of detected keys is not equal to expected number of keys based on starting key, this may cause errors in transcription.",
                LogLevel.WARNING,
            )
        row = {
            key.name: frame[y][x] for (x, y), key in zip(keyLocations, pianoKeyRange)
        }
        data.append(row)
    df = pd.DataFrame(data)
    if debug:
        df.to_csv("keys.csv", index=True)
    return df


def determineKeyPressesGMM(keyData: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    # Flatten hsv values
    hsvFlattened = np.vstack(keyData.values.flatten()).astype(float)
    # Threshold out dark pixels (S and H because too noisy at low V)
    darkValueThreshold = 50
    darkMask = hsvFlattened[:, 2] < darkValueThreshold
    hsvFlattened[darkMask] = np.array([0, 0, darkValueThreshold / 2])

    # Use gaussian mixture model to cluster keys
    numGroups = 4  # 4 groups: black keys, white keys, left hand color, right hand color
    gmm = GaussianMixture(
        n_components=numGroups, covariance_type="full", random_state=42
    )
    gmm.fit(hsvFlattened)
    labels = gmm.predict(hsvFlattened)
    centers = gmm.means_

    if debug:
        # --------------------------
        # Convert HSV → RGB for plotting
        # --------------------------
        hsvUint8 = hsvFlattened.astype(np.uint8).reshape(-1, 1, 3)
        rgb = cv2.cvtColor(hsvUint8, cv2.COLOR_HSV2RGB).reshape(-1, 3) / 255.0

        # --------------------------
        # Subsample points for plotting
        # --------------------------
        plotSampleFraction = 1
        numPoints = len(hsvFlattened)
        sampleSize = int(numPoints * plotSampleFraction)
        if sampleSize < 1:
            sampleSize = 1
        sampleIndices = np.random.choice(numPoints, sampleSize, replace=False)

        sampledHsv = hsvFlattened[sampleIndices]
        sampledRgb = rgb[sampleIndices]
        sampledLabels = labels[sampleIndices]

        # --------------------------
        # 3D scatter plot
        # --------------------------
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

        scatter = ax.scatter(
            sampledHsv[:, 0],
            sampledHsv[:, 1],
            sampledHsv[:, 2],
            c=sampledRgb,
            s=20,
            edgecolors="black",
            linewidths=0.3,
        )

        # Plot cluster centers
        centers_uint8 = centers.astype(np.uint8).reshape(-1, 1, 3)
        centers_rgb = (
            cv2.cvtColor(centers_uint8, cv2.COLOR_HSV2RGB).reshape(-1, 3) / 255.0
        )

        ax.scatter(
            centers[:, 0],
            centers[:, 1],
            centers[:, 2],
            c=centers_rgb,
            marker="X",
            s=300,
            edgecolors="black",
            linewidths=1.5,
            label="Cluster Centers",
        )

        ax.set_xlabel("Hue (H)")
        ax.set_ylabel("Saturation (S)")
        ax.set_zlabel("Value (V)")
        ax.set_title(
            f"GMM Clustering of HSV Values (sampled {plotSampleFraction*100:.1f}%)"
        )
        ax.legend()
        plt.show()

    # Turn labels into dataframe
    originalShape = keyData.shape
    labelMatrix = labels.reshape(originalShape)
    labeledDf = pd.DataFrame(labelMatrix, index=keyData.index, columns=keyData.columns)

    # Determine which groups are left hand and right hand

    # The two most frequent labels should belong to unpressed keys
    uniqueLabels, counts = np.unique(labels, return_counts=True)
    labelFrequencyMap = {}
    for label, count in zip(uniqueLabels, counts):
        labelFrequencyMap[label] = count
    unpressedKeyLabels = sorted(
        labelFrequencyMap, key=labelFrequencyMap.get, reverse=True
    )[:2]
    pressedKeyLabels = sorted(
        labelFrequencyMap, key=labelFrequencyMap.get, reverse=True
    )[2:]
    # Determine the average location of each played label to determine whether it is L/R hand
    averageLabelLocation = {}
    for label in pressedKeyLabels:
        for key in PianoKey:
            mask = (labeledDf[key.name] == label).astype(int)
            averageLabelLocation[label] = (
                mask.sum(axis=0) * key.value
            ) + averageLabelLocation.get(label, 0)
        averageLabelLocation[label] = (
            averageLabelLocation[label] / labelFrequencyMap[label]
        )
    # Create a map to change labels from numeric to hand notation
    labelMap = {}
    for unpressedKeyLabel in unpressedKeyLabels:
        labelMap[unpressedKeyLabel] = Notation.Unpressed.value
    leftHandLabel = min(averageLabelLocation, key=averageLabelLocation.get)
    rightHandLabel = max(averageLabelLocation, key=averageLabelLocation.get)
    labelMap[leftHandLabel] = Notation.LeftHand.value
    labelMap[rightHandLabel] = Notation.RightHand.value
    labeledDf = labeledDf.replace(labelMap)

    if debug:
        labeledDf.to_csv("labeledKeys.csv", index=True)

    return labeledDf


def transcribeVideo():
    pass


# Just for local debugging
def main():
    videoCapture = cv2.VideoCapture("./Hercules -.mp4")
    if not videoCapture.isOpened():
        print("Error: Unable to open video file.")
        return
    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, frame = videoCapture.read()
    if not ret:
        print("Error: Unable to read frame.")
        return
    advancedOptions = AdvancedOptions()
    keyLocations = determineKeyLocations(frame, advancedOptions)
    df = readKeys(videoCapture, keyLocations, advancedOptions, True)
    keyPressDf, centers = determineKeyPressesGMM(df, True)
    videoCapture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
