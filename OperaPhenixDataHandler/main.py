import datetime
import os
import fnmatch
import re
import timeit
import tifffile
import numpy as np
from ConfigReader import ConfigReader

def build_timelapse_image_filename(dir_path: str, well_name: str, field_name: str, plane: int, channel: int, time_point: int):
    filename = f"{well_name}{field_name}p{plane:02d}-ch{channel}sk{time_point}fk1fl1.tiff"
    return os.path.join(dir_path, filename)


def build_image_filename(dir_path: str, well_name: str, field_name: str, plane: int, channel: int):
    filename = f"{well_name}\{well_name}{field_name}p{plane:02d}-ch{channel:02d}t01.tiff"
    return os.path.join(dir_path, filename)


def create_max_projection(number_of_planes, number_of_channels, images):
    images = np.stack(images)
    image_x_dim = np.size(images, 2)
    image_y_dim = np.size(images, 1)

    projected_images = np.max(np.reshape(images, (number_of_channels, number_of_planes, image_y_dim, image_x_dim)), axis=1)
    return projected_images

def convert_to_8bit(images):
    image_8bit = []
    for image in images:
        image_8bit.append(np.uint8((image/np.max(image)) * 255))
    return np.array(image_8bit)


def process_well(well_name, load_path, save_path, number_of_fields, number_of_planes, number_of_channels,
                 number_of_timepoints, convert_8bit, run_timelapse ,max_projection):
    print(f"Processing {well_name} - {datetime.datetime.now()}")

    if not run_timelapse:
        for field in range(1, number_of_fields + 1):
            field_name = f'f{field:02d}'
            print(f"Processing {field_name} - {datetime.datetime.now()}")

            image_data = get_images(load_path, well_name, field_name, number_of_planes,
                                    number_of_channels) 
            

            image_size_x = image_data.shape[-1]
            image_size_y = image_data.shape[-2]

            if convert_8bit:
                image_data = convert_to_8bit(image_data)


            if max_projection:
                image_data = create_max_projection(number_of_planes, number_of_channels, image_data)


            save_name = f'{well_name}{field_name}_max_projection.tiff'
                
            tifffile.imwrite(f'{save_path}/{save_name}',
                                image_data,
                                imagej=True,
                                metadata={'axes': 'CYX'})

            print(f"Finished {field_name} - {datetime.datetime.now()}")   
         
    else:
        for field in range(1, number_of_fields + 1):
            field_name = f'f{field:02d}'
            print(f"Processing {field_name} - {datetime.datetime.now()}")
            try:
                timelapse = get_timelapse_images(load_path, well_name, field_name, number_of_planes,
                                                                number_of_channels, number_of_timepoints)

                image_size_x = timelapse.shape[-1]
                image_size_y = timelapse.shape[-2]

                if convert_8bit:
                    timelapse = convert_to_8bit(timelapse)

                # Reshape the array if there are multiple fields
                if number_of_fields > 1:
                    timelapse = np.reshape(timelapse, (number_of_timepoints * number_of_channels,
                                                    number_of_planes, image_size_y, image_size_x)).max(axis=1)

                save_name = f'{well_name}{field_name}_timelapse.tiff'
                tifffile.imwrite(f'{save_path}/{save_name}',
                                np.swapaxes(np.reshape(timelapse, (
                                number_of_channels, number_of_timepoints, image_size_y, image_size_x)),
                                            0, 1),
                                imagej=True,
                                metadata={'axes': 'TCYX'})

                print(f"Finished {field_name} - {datetime.datetime.now()}")
        
            except FileNotFoundError as e:
                print(f"Error processing {field_name}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {field_name}: {e}")

    print(f"Finished {well_name} - {datetime.datetime.now()}")


def main():
    params = ConfigReader("../config.json").get_config()

    # define parameters
    load_path = params["load_directory"]
    save_path = params["save_directory"]
    print(load_path)

    convert_8bit = params["convert_to_8bit"]
    run_timelapse = params["timelapse_data"]
    max_projection = params["max_projection"]

    number_of_timepoints = params["number_of_timepoints"]
    number_of_channels = params["number_of_channels"]
    number_of_planes = params["number_of_planes"]
    number_of_fields = params["number_of_fields"]

    create_dir(save_path)
    start = timeit.default_timer()

    well_names = generate_well_names(load_path)
    print(well_names)
    start_time = timeit.default_timer()

    for well_name in well_names:
        process_well(well_name, load_path, save_path, number_of_fields, number_of_planes, number_of_channels,
                     number_of_timepoints, convert_8bit, run_timelapse, max_projection)

    final_time = timeit.default_timer()
    print(f"All images took {final_time-start_time:.2f}s to merge")


if __name__ == "__main__":
    main()











