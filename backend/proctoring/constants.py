# proctoring/constants.py

# Maximum violations before auto-submission
MAX_VIOLATIONS = 3

# Event types for logging
EVENT_TYPES = {
    'tab_switch': 'Student switched browser tab',
    'window_blur': 'Student clicked outside browser window',
    'webcam_denied': 'Student denied webcam access',
    'webcam_disconnected': 'Webcam disconnected during exam',
    'multiple_faces': 'Multiple faces detected in webcam',
    'no_face': 'No face detected in webcam',
    'suspicious_movement': 'Suspicious movement detected',
}