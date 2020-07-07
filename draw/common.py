import os

output_path = "./draw_examples_output"

def create_output_folder():
    os.makedirs(output_path, exist_ok=True)
