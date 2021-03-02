from typing import Union

from wpimath.geometry import Pose2d, Translation2d
from utils.math import ft_to_m
import cv2
import numpy as np

from utils.paths import CURRENT_PATH as PATH, GeneratedRoute
from utils.trajectory import generate_trajectory


def cone_to_pose(_cone: str):
    cone_x = int(_cone[1:]) * 2.5
    cone_y = "FEDCBA".index(_cone[0]) * 2.5
    return Pose2d(ft_to_m(cone_x), ft_to_m(12.5 - cone_y), 0)


def to_image_coord_pose(pose: Union[Pose2d, Translation2d]):
    return int(pose.X() * 80) + 80, int(pose.Y() * 80) + 80


def color_interp(k: float, c1, c2):
    return c2[0] * k + c1[0] * (1-k), \
           c2[1] * k + c1[1] * (1-k), \
           c2[2] * k + c1[2] * (1-k)


def plot_trajectory(_route: GeneratedRoute):
    low_color = 40
    high_color = 255
    total_time: float = _route.trajectory.totalTime()
    last_pose = _route.route.start_pos
    samples = 1000
    for i in range(samples):
        t = total_time * (i / samples)
        position = _route.trajectory.sample(t).pose
        cv2.line(
            trajectory_image,
            to_image_coord_pose(last_pose),
            to_image_coord_pose(position),
            color_interp(i / samples, (low_color, high_color, low_color), (low_color, low_color, high_color))
        )
        last_pose = position

    cv2.circle(trajectory_image, to_image_coord_pose(_route.route.end_pos), 4, (0, 0, 255), thickness=cv2.FILLED)
    cv2.circle(trajectory_image, to_image_coord_pose(_route.route.start_pos), 4, (0, 255, 0), thickness=cv2.FILLED)
    cv2.circle(trajectory_image, to_image_coord_pose(_route.route.end_pos), 2, (0, 0, 255), thickness=cv2.FILLED)

    for waypoint in _route.route.waypoints:
        cv2.circle(trajectory_image, to_image_coord_pose(waypoint), 3, (180, 180, 180), thickness=cv2.FILLED)


routes = generate_trajectory(PATH)

trajectory_image = np.zeros((500, 900, 3), np.uint8)

start_x1, start_y1 = to_image_coord_pose(cone_to_pose(PATH.start_zone[0]))
start_x2, start_y2 = to_image_coord_pose(cone_to_pose(PATH.start_zone[1]))
end_x1, end_y1 = to_image_coord_pose(cone_to_pose(PATH.end_zone[0]))
end_x2, end_y2 = to_image_coord_pose(cone_to_pose(PATH.end_zone[1]))
c_start_x1 = min(start_x1, start_x2) + 3
c_start_x2 = max(start_x1, start_x2) - 3
c_start_y1 = min(start_y1, start_y2) + 3
c_start_y2 = max(start_y1, start_y2) - 3

cv2.rectangle(trajectory_image, (start_x1, start_y1), (start_x2, start_y2), (0, 100, 0), thickness=cv2.FILLED)
cv2.rectangle(trajectory_image, (end_x1, end_y1), (end_x2, end_y2), (0, 0, 100), thickness=cv2.FILLED)
cv2.rectangle(trajectory_image, (c_start_x1, c_start_y1), (c_start_x2, c_start_y2), (0, 100, 0), thickness=cv2.FILLED)

for cone in PATH.cones:
    center = to_image_coord_pose(cone_to_pose(cone))
    pt1 = (center[0] - 5, center[1] - 5)
    pt2 = (center[0] + 5, center[1] + 5)
    cv2.rectangle(trajectory_image, pt1, pt2, (0, 255, 255), thickness=cv2.FILLED)

for special_cone in PATH.special_cones:
    center = to_image_coord_pose(cone_to_pose(special_cone))
    pt1 = (center[0] - 5, center[1] - 5)
    pt2 = (center[0] + 5, center[1] + 5)
    cv2.rectangle(trajectory_image, pt1, pt2, (80, 80, 255), thickness=cv2.FILLED)

for gen_route in routes:
    plot_trajectory(gen_route)

cv2.imshow("trajectory", trajectory_image)

cv2.waitKey()