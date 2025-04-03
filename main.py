from dataclasses import dataclass
from statistics import mean
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

from utils import Option
from synths_utils import Player

WEBCAM = 1
WINDOW_NAME = "Theremime"

@dataclass
class Posn:
    """
    Reprsents a 3-d coordinate.
    """
    x: float
    y: float
    z: float


class Seer:
    """
    Accesses the webcam and gets the hand positioning as input.
    """
    def __init__(self):
        # Create Landmarker
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(base_options=base_options,
                                            num_hands=2)
        self.detector = vision.HandLandmarker.create_from_options(options)


        cv2.namedWindow(WINDOW_NAME)
        self.vc = cv2.VideoCapture(WEBCAM)
        
        if self.vc.isOpened(): # try to get the first frame
            rval, _frame = self.vc.read()
        else:
            print("Error: Can access webcam, but not read from it. Maybe it's being used by other softare?")
            rval = False  

        self.is_going = rval


    @staticmethod
    def mark_hands(rgb_image, hands):
        """
        Draws the average hand positions on the image.
        This method is unused at the moment, but is a more accurate representation of what's going on.
        """
        def draw_hand(image, hand, color):
            if hand is None:
                return image

            x, y = int(hand.x * image.shape[1]), int(hand.y * image.shape[0])
            cv2.circle(image, (x, y), 10, color, -1)
            return image

        image = np.copy(rgb_image)
        image = draw_hand(image, hands[0], (255, 0, 0))
        image = draw_hand(image, hands[1], (0, 0, 255))
        return image
     
    @staticmethod
    def draw_landmarks_on_image(rgb_image, detection_result):
        """
        Draws hand landmarks and handedness on the image. 
        This method is adapted from a function in Mediapipe's official hand tracking example.
        """
        def flip_lr_names(name):
            match name:
                case "Left":
                    return "Right"
                case "Right":
                    return "Left"

        MARGIN = 10  # pixels
        FONT_SIZE = 1
        FONT_THICKNESS = 1
        HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = np.copy(rgb_image)

        # Loop through the detected hands to visualize.
        for handedness, hand_landmarks in zip(handedness_list, hand_landmarks_list):
            # hand_landmarks = hand_landmarks_list[idx]
            # handedness = handedness_list[idx]

            # Draw the hand landmarks.
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{flip_lr_names(handedness[0].category_name)}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

        return annotated_image

    def get_hands(self):
        """
        Gets hand positions from the webcam.
        """
        rval, frame = self.vc.read()
        self.is_going |= rval
        if not rval:
            print("Can no longer read from webcam.")
            return Option(), Option()
        
        frame = cv2.flip(frame, 1) # much better for visualisation. 
        image = mp.Image(data=np.array(frame), image_format=mp.ImageFormat.SRGB)
        detection_result = self.detector.detect(image)

        annotated_image = self.draw_landmarks_on_image(image.numpy_view(), detection_result)
        # annotated_image = self.mark_hands(image.numpy_view(), self.parse_hands(detection_result))
        cv2.imshow(WINDOW_NAME, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2RGBA))

        key = cv2.waitKey(1)
        if key in [27, 32]:
            self.is_going = False

        return self.parse_hands(detection_result)

    @staticmethod
    def hand_to_posn(hand_landmarks):
        """
        Takes the hand landmarks and returns the average position of the hand.
        """
        xs = []
        ys = []
        zs = []
        for point in hand_landmarks:
            xs.append(point.x)
            ys.append(point.y)
            zs.append(point.z)

        return Posn(mean(xs), mean(ys), mean(zs))

    def parse_hands(self, detection_result) -> tuple[Option, Option]:
        """
        Gets the average hand positions, if available.
        """
        left_points = Option()
        right_points = Option()

        for handedness, hand_landmarks in zip(detection_result.handedness, detection_result.hand_landmarks):
            if handedness[0].category_name == 'Left': # don't forget, the image is mirrored.
                right_points.inner = hand_landmarks
            else:
                left_points.inner = hand_landmarks

        return left_points.map(self.hand_to_posn), right_points.map(self.hand_to_posn)
        
    def __del__(self):
        """
        I know this I should be doing this via a context manager but this is frankly far nicer.
        """
        self.vc.release()
        cv2.destroyWindow(WINDOW_NAME)

    
def theremin(left, right) -> tuple[float, float]:
    """
    Takes the hand positions and returns the desired frequency and volume.
    """
    
    KEY = 261.63
    SCALE_FACTOR = 72
    HALF_TONE = 2 ** (1/12)
    SHIFT = 0.3

    def tune(x):
        """
        My musician friends tell me this is an aberration and I'll undo it 
        once the actual wave generated sound good or if I can get glissando
        working.
        """
        if x >= 1:
            return round(x)
        else:
            denom = round(1/x)
            if denom == 0:
                return x
            return 1 / denom


    volume = left.map(lambda x: x.y).inner

    frequency = right \
    .map(lambda x: x.x - SHIFT) \
    .map(lambda x: KEY * (HALF_TONE ** tune(x * SCALE_FACTOR))) \
    .inner

    return frequency, volume

    

def main():
    synth = Player(duration=0.2)
    seer = Seer()

    while seer.is_going:
        hands = seer.get_hands()
        try:
            frequency, volume = theremin(*hands)
            synth.play_note(frequency, volume)
        except TypeError:
            print(hands)
        
    
    
if __name__ == "__main__":
    main()