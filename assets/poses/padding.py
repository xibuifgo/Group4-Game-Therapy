from PIL import Image

def pad_to_aspect_ratio(image_path, output_path, target_width, target_height):
    image = Image.open(image_path).convert("RGBA")  # Preserve transparency

    original_width, original_height = image.size
    target_aspect = target_width / target_height
    original_aspect = original_width / original_height

    if original_aspect > target_aspect:
        # Image is too wide, add transparent space to top and bottom
        new_width = original_width
        new_height = int(original_width / target_aspect)
    else:
        # Image is too tall, add transparent space to sides
        new_height = original_height
        new_width = int(original_height * target_aspect)

    # Create a new transparent image with target size
    new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

    # Calculate top-left corner position to paste the original image centered
    paste_x = (new_width - original_width) // 2
    paste_y = (new_height - original_height) // 2

    new_image.paste(image, (paste_x, paste_y))

    new_image.save(output_path)
    print(f"Saved padded image to: {output_path}")


pad_to_aspect_ratio(
    "assets/poses/normal_standing_stance.PNG", 
    "assets/poses/normal_standing_stance.PNG", 
    400, 400
    )

pad_to_aspect_ratio(
    "assets/poses/star.PNG", 
    "assets/poses/star.PNG", 
    400, 400
    )
pad_to_aspect_ratio(
    "assets/poses/tandem_stance.PNG", 
    "assets/poses/tandem_stance.PNG", 
    400, 400
    )

pad_to_aspect_ratio(
    "assets/poses/heel_raise.PNG", 
    "assets/poses/heel_raise.PNG",
    400, 400
    )


pad_to_aspect_ratio(
    "assets/poses/left_flamingo.PNG", 
    "assets/poses/left_flamingo.PNG", 
    400, 400
    )

pad_to_aspect_ratio(
    "assets/poses/right_flamingo.PNG", 
    "assets/poses/right_flamingo.PNG", 
    400, 400
    )