import pygame
import os
from pose_templates import PoseTemplates

def load_poses(directory="assets/poses"):
    """
    Load pose images along with names and descriptions from PoseTemplates.
    Returns a list of (image_surface, name, description).
    """
    poses = []
    template = PoseTemplates()

    if not os.path.exists(directory):
        print(f"Warning: Pose directory '{directory}' not found. Using placeholder poses.")
        images = create_placeholder_poses()
    else:
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        desired_order = [
            "normal_standing_stance.png",
            "star_pose.png",
            "tandem_stance.png",
            "heel_raise.png",
            "flamingo_left.png",
            "flamingo_right.png"
        ]
        files = [f for f in desired_order if os.path.exists(os.path.join(directory, f))]

        images = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                try:
                    image_path = os.path.join(directory, file)
                    image = pygame.image.load(image_path)
                    images.append(image)
                    print(f"Loaded pose image: {file}")
                except pygame.error as e:
                    print(f"Failed to load pose image {file}: {e}")

        if not images:
            print("No valid pose images found. Using placeholder poses.")
            images = create_placeholder_poses()

    for i, img in enumerate(images):
        pose_info = template.get_pose_description(i)
        if pose_info:
            poses.append((img, pose_info["name"], pose_info["description"]))
        else:
            poses.append((img, f"Pose {i+1}", "No description"))

    return poses

def create_placeholder_poses():
    """Create placeholder poses as colored rectangles."""
    poses = []
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255)
    ]

    for color in colors:
        pose_surface = pygame.Surface((400, 400))
        pose_surface.fill(color)
        pygame.draw.circle(pose_surface, (255, 255, 255), (200, 100), 50)
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 150, 100, 150))
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 300, 40, 100))
        pygame.draw.rect(pose_surface, (255, 255, 255), (210, 300, 40, 100))
        pygame.draw.rect(pose_surface, (255, 255, 255), (100, 150, 50, 100))
        pygame.draw.rect(pose_surface, (255, 255, 255), (250, 150, 50, 100))
        poses.append(pose_surface)

    return poses
