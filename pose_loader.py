# pose_loader.py
import pygame
import os

def load_poses(directory="poses"):
    """
    Load pose images from the specified directory.
    Returns a list of pygame Surface objects representing poses.
    
    If no poses are found, returns placeholder colored rectangles.
    """
    poses = []
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Warning: Pose directory '{directory}' not found. Using placeholder poses.")
        return create_placeholder_poses()
    
    # Try to load images from directory
    valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
    files = os.listdir(directory)
    
    for file in files:
        # Check if file is an image
        ext = os.path.splitext(file)[1].lower()
        if ext in valid_extensions:
            try:
                image_path = os.path.join(directory, file)
                image = pygame.image.load(image_path)
                poses.append(image)
                print(f"Loaded pose image: {file}")
            except pygame.error as e:
                print(f"Failed to load pose image {file}: {e}")
    
    if not poses:
        print("No valid pose images found. Using placeholder poses.")
        return create_placeholder_poses()
    
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
        
        # Add some visual elements to make it look more like a pose
        pygame.draw.circle(pose_surface, (255, 255, 255), (200, 100), 50)  # Head
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 150, 100, 150))  # Body
        pygame.draw.rect(pose_surface, (255, 255, 255), (150, 300, 40, 100))  # Left leg
        pygame.draw.rect(pose_surface, (255, 255, 255), (210, 300, 40, 100))  # Right leg
        pygame.draw.rect(pose_surface, (255, 255, 255), (100, 150, 50, 100))  # Left arm
        pygame.draw.rect(pose_surface, (255, 255, 255), (250, 150, 50, 100))  # Right arm
        
        poses.append(pose_surface)
    
    return poses