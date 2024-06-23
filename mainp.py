
import cv2
import os
import cvzone
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector

# Load background image
imgBackground = cv2.imread('Resources/Background.png')

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Import all modes
folderPathModes = 'Resources/Modes'
listImgModesPath = os.listdir(folderPathModes)
listImgModes = []
for imgMode in listImgModesPath:
    listImgModes.append(cv2.imread(os.path.join(folderPathModes, imgMode)))

# Import all icons
folderPathIcons = 'Resources/Icons'
listImgIconsPath = os.listdir(folderPathIcons)
listImgIcons = []
for imgIcon in listImgIconsPath:
    listImgIcons.append(cv2.imread(os.path.join(folderPathIcons, imgIcon)))

# Initialize variables for mode change and selection
modetype = 0
selection = -1
selectionSpeed = 7

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Mode positions
modePositions = [(1136, 196), (1000, 384), (1136, 581)]

# Counter for waiting between mode selections
counterPause = 0

# List of selections
selectionList = [-1, -1, -1]
finalorder = []

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1280, 720))

# Recording flag
isRecording = True

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    # Overlay webcam feed on background image
    imgBackground[139:139 + 480, 50:50 + 640] = img
    imgBackground[0:720, 847:1280] = listImgModes[modetype]

    if hands and counterPause == 0 and modetype < 3:
        hand1 = hands[0]
        fingers1 = detector.fingersUp(hand1)
        print(fingers1)
        if fingers1 == [0, 1, 0, 0, 0]:
            if selection != 1:
                counter = 1
            selection = 1
        elif fingers1 == [0, 1, 1, 0, 0]:
            if selection != 2:
                counter = 1
            selection = 2
        elif fingers1 == [0, 1, 1, 1, 0]:
            if selection != 3:
                counter = 1
            selection = 3
        elif fingers1 == [0, 1, 1, 1, 1]:
            isRecording = False
        else:
            selection = -1
            counter = 0

        if counter > 0:
            counter += 1
            print(counter)

            cv2.ellipse(imgBackground, modePositions[selection - 1], (103, 103), 0, 0, counter * selectionSpeed, (0, 255, 0), 20)

            if counter * selectionSpeed > 360:
                selectionList[modetype] = selection
                modetype += 1
                counter = 0
                selection = -1
                counterPause = 1

    if counterPause > 0:
        counterPause += 1
        if counterPause > 60:
            counterPause = 0

    # For the selection of icons in mode 1
    if selectionList[0] != -1:
        imgBackground[636:636 + 65, 133:133 + 65] = listImgIcons[selectionList[0] - 1]
    # For the selection of icons in mode 2
    if selectionList[1] != -1:
        imgBackground[636:636 + 65, 340:340 + 65] = listImgIcons[2 + selectionList[1]]
    # For the selection of icons in mode 3
    if selectionList[2] != -1:
        imgBackground[636:636 + 65, 542:542 + 65] = listImgIcons[5 + selectionList[2]]

    # If all selections are made, display the final order
    if modetype == 3:
        coffeeTypes = ["Latte", "Black", "Tea"]
        sugarLevels = ["1 Spoon", "2 Spoons", "3 Spoons"]
        sizes = ["Small", "Medium", "Large"]

        finalOrder = f"{coffeeTypes[selectionList[0] - 1]}, {sugarLevels[selectionList[1] - 1]}, {sizes[selectionList[2] - 1]}"

        cv2.putText(imgBackground, finalOrder, (850, 600), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)
    # Write the frame to the video file
    if isRecording:
        out.write(imgBackground)

    # Display the image
    cv2.imshow("Background", imgBackground)
    key = cv2.waitKey(1)
    if key == ord('q') or not isRecording:
        break

# Release everything when done
cap.release()
out.release()
cv2.destroyAllWindows()
