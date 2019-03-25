import os
import pdb
from src.common.command import Command

class Kaiba(object):

    @staticmethod
    def run(input_path, output_path, output_csv='foo'):
        if not os.path.exists(input_path):
            print 'path not exist'
            return
        elif input_path.endswith('.nii'):
            input_nii = input_path
        elif input_path.endswith('.nii.gz'):
            input_nii = Command.unzip_file(input_path)
        elif os.path.isdir(input_path):
            input_nii = Command.dicom2nii(input_path, output_path)
        command = 'kaiba -i \"{}\" -v -o \"{}\"'.format(input_nii, output_csv)
        Command.excute(command)   

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        outputs = Command.find_files('./', [os.path.basename(input_nii.rstrip('.nii')) + '*', output_csv+'*'])
        for o in outputs:
            try:
                Command.copy_files(o, output_path)
            except:
                print 'somthing happend'
            Command.remove_file(o)


class Designer(object):   

    @staticmethod
    def run(dir_list, dkipa, output_path):
        dir_str = ','.join(dir_list)
        command = "DESIGNER.py -mask -denoise -degibbs -rician -smooth 1.2 -eddy -rpe_pair \"{}\" \
                   -pe_dir AP -DTIparams -DKIparams -WMTIparams -nocleanup -akc -outliers\
                   -tempdir \"{}\" \"{}\" \"{}/designer_parameters\" ".format(dkipa, 
                                                                              output_path, 
                                                                              dir_str, 
                                                                              output_path)
        Command.excute(command)

class Freesurfer(object):

    @staticmethod
    def run(input_path, output_path, subject_name, subjects_dir='/home/shihong/Desktop/Qi_Chen/data/PROCESSED/FREESURFER_PONS/'):
        os.environ['SUBJECTS_DIR'] = subjects_dir
        command = 'recon-all -all -i \"{}\" -s \"{}\"  -brainstem-structures -parallel -openmp 6'.format(input_path, subject_name)
        Command.excute(command)
        try:
            Command.copy_files('{}/{}'.format(subjects_dir, subject_name), output_path)
        except:
            print 'something happend'

class Register_aseg(object):

    @staticmethod
    def run(input_path, output_path, subject, subject_dir, aseg, norm, register=False):
        os.environ['SUBJECTS_DIR'] = subject_dir
        if not os.path.exists(input_path):
            print 'path not exist'
            return
        elif input_path.endswith('.nii'):
            input_nii = input_path
        elif input_path.endswith('.nii.gz'):
            input_nii = Command.unzip_file(input_path)
        elif os.path.isdir(input_path):
            input_nii = Command.dicom2nii(input_path, '{}'.format(output_path))
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if register:
            register_dat = '{}/register_info/register.dat'.format(output_path)
            Command.excute('bbregister --s \"{}\" --mov \"{}\" --reg \"{}\" --dti'.format(subject, 
                                                                                          input_nii, 
                                                                                          register_dat))
            aseg_register = '{}/aparc+aseg-in-target.nii'.format(output_path)
            Command.excute('mri_label2vol --seg \"{}\" --temp \"{}\" --o \"{}\" --reg \"{}\"'.format(aseg, 
                                                                                                 input_nii, 
                                                                                                 aseg_register,
                                                                                                 register_dat))
            
            inv_nii ='{}/{}_norm_inv.nii'.format(output_path, os.path.basename(input_path))
            Command.excute('mri_vol2vol --inv --targ \"{}\" --o \"{}\" --mov \"{}\" --reg \"{}\"'.format(norm, 
                                                                                                        inv_nii, 
                                                                                                        input_nii,
                                                                                                        register_dat))
        else:
            aseg_register = '{}/aparc+aseg-in-target.nii'.format(output_path)
            Command.excute('mri_label2vol --seg \"{}\" --temp \"{}\" --o \"{}\" --regheader'.format(aseg, 
                                                                                                    input_nii, 
                                                                                                    aseg_register))
            
            inv_nii ='{}/{}_norm_inv.nii'.format(output_path, os.path.basename(input_path))
            Command.excute('mri_vol2vol --inv --targ \"{}\" --o \"{}\" --mov \"{}\" --regheader'.format(norm, 
                                                                                                        inv_nii, 
                                                                                                        input_nii))
        freesurfer_home = '/usr/local/freesurfer/FreeSurferColorLUT.txt'
        aparc_aseg_pvc_sum = '{}/{}.aparc+aseg_pvc.sum'.format(output_path, os.path.basename(input_path))
        Command.excute('mri_segstats --robust 5 --seg-erode 1 --pv \"{}\" --seg \"{}\" --ctab \"{}\" --excludeid 0 --i \"{}\" --sum \"{}\"'.format(inv_nii, 
                                                                                                                                                   aseg_register, 
                                                                                                                                                   freesurfer_home, 
                                                                                                                                                   input_nii, 
                                                                                                                                                   aparc_aseg_pvc_sum))
        output_csv_mean = '{}/{}_mean.csv'.format(output_path, 
                                                  os.path.basename(input_path))
        output_csv_std = '{}/{}_std.csv'.format(output_path, 
                                                os.path.basename(input_path))
        Command.excute('asegstats2table -i \"{}\" --transpose -m mean --all-segs -t \"{}\"'.format(aparc_aseg_pvc_sum, 
                                                                                                   output_csv_mean))
        Command.excute('asegstats2table -i \"{}\" --transpose -m std --all-segs -t \"{}\"'.format(aparc_aseg_pvc_sum, 
                                                                                                  output_csv_std))