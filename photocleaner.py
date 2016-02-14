#!/usr/bin/env python2.7

from __future__ import division
import argparse
import os
import stat
import sys
import time
from itertools import groupby
from PIL import Image
import psutil


class PhotoParser(object):
    def __init__(self, photo_info):
        self.photo_info = photo_info
        self.photos_by_histogram = self.__sort_by_histogram()
        self.photos_to_process = self.__get_photos_to_process()

    def __sort_by_histogram(self):
        print('Grouping images by histogram...')
        histograms = list({(p.get_histogram(), p) for p in self.photo_info})
        histograms.sort(key=lambda k: k[0])
        result = {}
        for key, values in groupby(histograms, key=lambda x: x[0]):
            result[key] = list(v[1] for v in values)
        return result

    def __get_photos_to_process(self):
        photos_to_process = []
        same_photos = 0
        print('Searching for identical photos...')

        for k, v in self.photos_by_histogram.items():
            photos_to_process.append(v[0])

            if len(v) > 1:
                print('Identical photos found:')
                for img in v:
                    print('\t' + img.get_file_name())
                same_photos = same_photos + 1

        if same_photos == 0:
            print("There are no identical photos, there's nothing to do.")
            sys.exit(-1)

        return photos_to_process

    def process(self):
        try:
            # Order photos by creation date
            tmp_photos = {}
            for i in self.photos_to_process:
                print(i)
            '''
                tmp_photos[i] = self.photo_info[i].get_file_date()
            photos_by_creation = sorted(tmp_photos.items())

            # Making of the directory tree

            result = {}
            # Calculate unique years
            unique_years = list(set([p[1][:4] for p in photos_by_creation]))

            # Associate months to years
            for uy in unique_years:
                months = []
                for p in photos_by_creation:
                    year = p[1][:4]
                    if year == uy:
                        months.append(p[1][5:7])
                result[uy] = list(set(months))
            '''

        except Exception, e:
            print('Error processing data:')
            print(repr(e))
            sys.exit(-1)


class PhotoInfo(object):
    def __init__(self, file_info):
        self.file_info = file_info
        self.histogram = None

    def set_histogram(self, histogram):
        self.histogram = histogram

    def get_histogram(self):
        return self.histogram

    def get_file_size(self):
        return self.file_info['fsize']

    def get_file_name(self):
        return self.file_info['fname']

    def get_file_date(self):
        return self.file_info['f_ct']

    def get_year(self):
        return self.file_info['f_ct'][:4]

    def get_month(self):
        return self.file_info['f_ct'][5:7]


class PhotoCleaner(object):
    def __init__(self, paths):
        self.photo_info = {}
        self.file_list = []
        self.input_path = paths[0]
        self.output_path = paths[1]
        self.images_found = 0
        self.__scan_path_for_images()
        self.photo_info = self.__create_photo_info_objects()
        self.__analyze_histogram()

    def __scan_path_for_images(self):
        self.file_list = [os.path.join(x[0], y) for x in os.walk(self.input_path) for y in x[2]]
        self.img_list = [file for file in self.file_list if file[-4:].lower() in ('jpeg', '.jpg', '.png')]
        self.images_found = len(self.img_list)

        if self.images_found == 0:
            print('There are no images in the specified path')
            sys.exit(-1)
        else:
            print('Found %d images' % self.images_found)

    def __create_photo_info_objects(self):
        needed_free_space = 0
        print('Calculating free space...')
        photo_info = []
        for f in self.img_list:
            file_stats = os.stat(f)
            file_info = {
                'fname': f,
                'fsize': file_stats[stat.ST_SIZE],
                'f_ct': time.strftime("%Y-%m-%d %I:%M:%S%p", time.localtime(file_stats[stat.ST_CTIME]))
            }
            needed_free_space += file_stats[stat.ST_SIZE]
            photo_info.append(PhotoInfo(file_info))

        free_space = self.__get_free_space()

        if free_space - needed_free_space < 0:
            print(
                '%ld free bytes on disk are needed to work, only %ld bytes are available' % (
                    needed_free_space, free_space))
            sys.exit(-1)
        else:
            print('%ld bytes of free disk space are available, %ld bytes needed' % (free_space, needed_free_space))

        return photo_info

    @staticmethod
    def __get_free_space():
        return psutil.disk_usage(".").free

    def __analyze_histogram(self):
        print('Analyzing histograms...')
        try:
            index = 0
            total = len(self.photo_info)
            for i in self.photo_info:
                image = Image.open(i.get_file_name())
                histogram = hash(str(image.histogram()))
                i.set_histogram(histogram)
                index += 1
                print('Completed %d%%' % ((100 * index) / total))
        except Exception, e:
            print('Error analyzing histograms')
            print(repr(e))
            sys.exit(-1)

    def get_photo_info(self):
        return self.photo_info


def main():
    paths = get_paths()
    prepare_paths(paths)
    pc = PhotoCleaner(paths)
    photo_info = pc.get_photo_info()
    ps = PhotoParser(photo_info)
    ps.process()


def prepare_paths(paths):
    # Input path
    if not os.path.isdir(paths[0]):
        print('Input a valid input directory')
        sys.exit(-1)

    # Output path
    if not os.path.isdir(paths[1]):
        # Trying to create the output_path
        create_output_path(paths[1])
    else:
        return
        # Directory exists, delete contents?
        result = raw_input('The directory ' + paths[1] + ' exists, do you want to delete its contents? (y/N)')

        if result.lower() == 'y':
            sure_result = raw_input('Are you totally sure? (y/N)')
            if sure_result.lower() == 'y':
                # Delete contents of directory
                delete_output_path(paths[1])
                return

        print('Aborting...')
        sys.exit(-1)


def get_paths():
    parser = argparse.ArgumentParser('photocleaner')
    parser.add_argument('input_path', help='input_path points the path for image searching')
    parser.add_argument('output_path', help='output_path where images will be saved when processed')
    args = parser.parse_args()
    return args.input_path, args.output_path


def create_output_path(output_path):
    try:
        os.mkdir(output_path)
    except Exception, e:
        print('Unable to make directory ' + output_path)
        sys.exit(-1)


def delete_output_path(output_path):
    try:
        os.rmdir(output_path)
        create_output_path(output_path)
    except Exception, e:
        print('Unable to delete directory ' + output_path)
        sys.exit(-1)


if __name__ == '__main__':
    main()
