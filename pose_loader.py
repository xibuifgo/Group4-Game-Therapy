import pygame
import os

from pose_templates import PoseTemplates

def load_poses(directory="poses"):
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
        files = sorted(os.listdir(directory))
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
        pose_info = template.get_pose(i)
        if pose_info:
            poses.append((img, pose_info["name"], pose_info["description"]))
        else:
            poses.append((img, f"Pose {i+1}", "No description"))

    return poses


def create_placeholder_poses():
    """Create placeholder poses as colored rectangles."""
    poses = []
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255)   # Magenta
    ]
    
    for color in colors:
        pose_surface = pygame.Surface((400, 400))
        pose_surface.fill(color)
        
        pygame.draw.circle(pose_surface, (255, 255, 255), (200, 100), 50)  # Head
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 150, 100, 150))  # Body
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 300, 40, 100))  # Left leg
        pygame.draw.rect(pose_surface, (255, 255, 255), (210, 300, 40, 100))  # Right leg
        pygame.draw.rect(pose_surface, (255, 255, 255), (100, 150, 50, 100))  # Left arm
        pygame.draw.rect(pose_surface, (255, 255, 255), (250, 150, 50, 100))  # Right arm
        
        poses.append(pose_surface)
    
    return poses