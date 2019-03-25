import shutil
import errno
import subprocess
import shlex
from glob import glob
import os
import sys

PATH = os.environ['PATH'].split(":")
mrtrixbin = [s for s in PATH if "mrtrix3" in s][0]
if not mrtrixbin:
    print("cannot find path to mrtrix3, please make sure <path/to/mrtrix3/bin> is in your PATH")
mrtrixlib = "".join(mrtrixbin)[:-3]+'lib'
print(mrtrixlib)
sys.path.insert(0, mrtrixlib)
from mrtrix3 import image as mrimage

class Command(object):
    
    @staticmethod
    def copy_files(src, dest):
        try:
            shutil.copytree(src, dest)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                print('Directory not copied. Error: %s' % e)

    @staticmethod
    def move_files(src, dest, replace=True):
        if replace:
            shutil.move(src, '{}/{}'.format(dest, src))
        else:
            try:
                shutil.move(src, dest)
            except:
                print ('file {} already exist will not modify it'.format(src))

    @staticmethod
    def find_files(path, require, expection=[]):
        if type(require) != list:
            print 'require have to be list!'
            return []
        file_lst =  [y for x in os.walk(path) 
                     for r in require 
                     for y in glob(os.path.join(x[0], r))]
        res = []
        for f in file_lst:
            flag = False
            for e in expection:
                if e in f:
                    flag = True
            if flag:
                continue
            res.append(f)
        return res

    @staticmethod
    def excute(command):
        subprocess.call(shlex.split(command))#, stdout=subprocess.PIPE)

    @staticmethod
    def unzip_file(file_path):
        if file_path.endswith('.gz'):
            command = 'gunzip {}'.format(file_path)
            Command.command_excute(command)
            return file_path.rstrip('.gz')
        return file_path

    @staticmethod
    def dicom2nii(input_path, output_path):
        if not os.path.exists(input_path) or mrimage.Header(input_path).format() != 'DICOM':
            return ''
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_name = '{}/{}_transform.nii'.format(output_path, os.path.basename(input_path))
        command = "mrconvert {} {}".format(input_path, output_name)
        Command.excute(command)
        return output_name

    @staticmethod
    def remove_file(input_path):
        os.remove(input_path)