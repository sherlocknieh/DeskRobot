"""
    The model inference code in this file is modified from
    https://gist.github.com/fyr91/83a392ffd22342d4e5f8866b01fafb30 Thanks to the
    original authur: fyr91
"""

from onnx_tf.backend import prepare
import cv2
import numpy as np
import onnx
import onnxruntime as ort


def area_of(left_top, right_bottom):
    """
    Compute the areas of rectangles given two corners.
    Args:
        left_top (N, 2): left top corner.
        right_bottom (N, 2): right bottom corner.
    Returns:
        area (N): return the area.
    """
    hw = np.clip(right_bottom - left_top, 0.0, None)
    return hw[..., 0] * hw[..., 1]


def iou_of(boxes0, boxes1, eps=1e-5):
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Args:
        boxes0 (N, 4): ground truth boxes.
        boxes1 (N or 1, 4): predicted boxes.
        eps: a small number to avoid 0 as denominator.
    Returns:
        iou (N): IoU values.
    """
    overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
    overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])

    overlap_area = area_of(overlap_left_top, overlap_right_bottom)
    area0 = area_of(boxes0[..., :2], boxes0[..., 2:])
    area1 = area_of(boxes1[..., :2], boxes1[..., 2:])
    return overlap_area / (area0 + area1 - overlap_area + eps)


def hard_nms(box_scores, iou_threshold, top_k=-1, candidate_size=200):
    """
    Perform hard non-maximum-supression to filter out boxes with iou greater
    than threshold
    Args:
        box_scores (N, 5): boxes in corner-form and probabilities.
        iou_threshold: intersection over union threshold.
        top_k: keep top_k results. If k <= 0, keep all the results.
        candidate_size: only consider the candidates with the highest scores.
    Returns:
        picked: a list of indexes of the kept boxes
    """
    scores = box_scores[:, -1]
    boxes = box_scores[:, :-1]
    picked = []
    indexes = np.argsort(scores)
    indexes = indexes[-candidate_size:]
    while len(indexes) > 0:
        current = indexes[-1]
        picked.append(current)
        if 0 < top_k == len(picked) or len(indexes) == 1:
            break
        current_box = boxes[current, :]
        indexes = indexes[:-1]
        rest_boxes = boxes[indexes, :]
        iou = iou_of(rest_boxes, np.expand_dims(current_box, axis=0),)
        indexes = indexes[iou <= iou_threshold]

    return box_scores[picked, :]


def predict(
    width, height, confidences, boxes, prob_threshold, iou_threshold=0.5, top_k=-1
):
    """
    Select boxes that contain human faces
    Args:
        width: original image width
        height: original image height
        confidences (N, 2): confidence array
        boxes (N, 4): boxes array in corner-form
        iou_threshold: intersection over union threshold.
        top_k: keep top_k results. If k <= 0, keep all the results.
    Returns:
        boxes (k, 4): an array of boxes kept
        labels (k): an array of labels for each boxes kept
        probs (k): an array of probabilities for each boxes being in corresponding labels
    """
    boxes = boxes[0]
    confidences = confidences[0]
    picked_box_probs = []
    picked_labels = []
    for class_index in range(1, confidences.shape[1]):
        probs = confidences[:, class_index]
        mask = probs > prob_threshold
        probs = probs[mask]
        if probs.shape[0] == 0:
            continue
        subset_boxes = boxes[mask, :]
        box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
        box_probs = hard_nms(box_probs, iou_threshold=iou_threshold, top_k=top_k,)
        picked_box_probs.append(box_probs)
        picked_labels.extend([class_index] * box_probs.shape[0])
    if not picked_box_probs:
        return np.array([]), np.array([]), np.array([])
    picked_box_probs = np.concatenate(picked_box_probs)
    picked_box_probs[:, 0] *= width
    picked_box_probs[:, 1] *= height
    picked_box_probs[:, 2] *= width
    picked_box_probs[:, 3] *= height
    return (
        picked_box_probs[:, :4].astype(np.int32),
        np.array(picked_labels),
        picked_box_probs[:, 4],
    )


onnx_path = "ultra_light_320.onnx"
onnx_model = onnx.load(onnx_path)
predictor = prepare(onnx_model, device="GPU")
ort_session = ort.InferenceSession(onnx_path)
input_name = ort_session.get_inputs()[0].name


def detect_first_face(frame):
    """The function will detect and return the first found face in camera frame.

    Args:
        frame: the camera frame for face detection.

    Returns:
        (x, y): returns the center of the face coordinate in NDC space [-1, 1].
        The function will return None if no face is found.
    """
    h, w, _ = frame.shape

    # Preprocess the image for the model input.
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img = cv2.resize(img, (320, 240))  # Resize
    img_mean = np.array([127, 127, 127])
    img = (img - img_mean) / 128
    img = np.transpose(img, [2, 0, 1])
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    confidences, boxes = ort_session.run(None, {input_name: img})
    boxes, _, _ = predict(w, h, confidences, boxes, 0.7)

    for i in range(boxes.shape[0]):
        box = boxes[i, :]
        x1, y1, x2, y2 = box

        # Draw box to visualize the face position.
        cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 18, 236), 2)
        cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (80, 18, 236), cv2.FILLED)
        cv2.putText(
            frame,
            "Face",
            (x1 + 6, y2 - 6),
            cv2.FONT_HERSHEY_DUPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        return (((x1 + x2) * 0.5 / w - 0.5) * 2.0, ((y1 + y2) * 0.5 / h - 0.5) * 2.0)

    return None



from modules.mod_face_tracking import detect_first_face
from simple_pid import PID
from urllib import request
import cv2
import numpy as np
import socketio
import time

SERVER_ADDR = "192.168.0.18"

sio = socketio.Client()
sio.connect("http://%s:5000" % SERVER_ADDR)


def read_from_mjpg_stream():
    stream = request.urlopen("http://%s:8080/?action=stream" % SERVER_ADDR)
    bytes = b""
    while True:
        bytes += stream.read(1024)
        a = bytes.find(b"\xff\xd8")
        b = bytes.find(b"\xff\xd9")
        if a != -1 and b != -1:
            jpg = bytes[a : b + 2]
            bytes = bytes[b + 2 :]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            yield frame

            cv2.imshow("rpi-robot - face tracking", frame)
            if cv2.waitKey(1) == 27:
                exit(0)


if __name__ == "__main__":
    pid = PID(0.5, 0.2, 0.0, setpoint=0)

    # Control loop
    for frame in read_from_mjpg_stream():
        face_center_ndc = detect_first_face(frame)

        in_ = face_center_ndc[0] if (face_center_ndc is not None) else 0.0
        out = pid(in_)
        print("in=%.2f  out=%.2f" % (in_, out))

        # Only rotate the robot without moving forward and backward (y is set to 0).
        sio.emit("set_axis", {"x": -out, "y": 0.0})
