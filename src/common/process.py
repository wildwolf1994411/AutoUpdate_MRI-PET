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

    
    JHU_TEMPLATE = './const/wm_roi/JHU-ICBM-FA-1mm.nii.gz'
    JHU_LABEL = './const/wm_roi/JHU-ICBM-labels-1mm.nii.gz'
    LABEL_REFERENCE_TABLE = './const/wm_roi/label_reference_table.txt'

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

    @staticmethod
    def wm_extraction_init(template, label, label_reference_table):
        """
            template: JHU file JHU-ICBM-FA-1mm.nii.gz
            label: JHU file JHU-ICBM-labels-1mm.nii.gz
            label_reference_table: label_reference_table.txt file
        """
        Designer.JHU_TEMPLATE = template
        Designer.JHU_LABEL = label
        Designer.LABEL_REFERENCE_TABLE = label_reference_table

    @staticmethod
    def wm_extraction_fa(input_path, output_path):
        """
        input_path: designer parameter path
        output_path: output path, will create if not exist
        """
        if not Designer.JHU_TEMPLATE or not Designer.JHU_LABEL or not Designer.LABEL_REFERENCE_TABLE:
            print 'please initial first'
            return
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        fa_lst = Command.find_files(input_path, ['fa.nii'])
        paras = Command.find_files(input_path, ['*.nii'], ['fa.nii'])

        if not fa_lst or not paras:
            print 'required file not found'
            return

        fa = fa_lst[0]
        fa_noNaN = fa.rstrip('.nii') + '_noNaN.nii'
        Command.excute('mrcalc -force \"{}\" -finite \"{}\" 0 -if \"{}\"'.format(fa, fa, fa_noNaN))

        # need modify
        fa2jhu_affine = '{}/{}'.format(output_path, 'fa2jhu_affine.txt')
        Command.excute('flirt -in \"{}\" -ref \"{}\" -omat \"{}\" -dof 12'.format(fa_noNaN, 
                                                                                  Designer.JHU_TEMPLATE, 
                                                                                  fa2jhu_affine))
        
        cout = '{}/{}'.format(output_path, 'fa2jhu_nonlin')
        iout = '{}/{}'.format(output_path, 'fa2jhu_nonlin_fa')
        Command.excute('fnirt --in=\"{}\" --ref=\"{}\" --aff=\"{}\" --cout=\"{}\" --iout=\"{}\" --config=FA_2_FMRIB58_1mm'.format(fa_noNaN, 
                                                                                                                                   Designer.JHU_TEMPLATE, 
                                                                                                                                   fa2jhu_affine, 
                                                                                                                                   cout, 
                                                                                                                                   iout))
        jhu2fa_nonlin = '{}/{}'.format(output_path, 'jhu2fa_nonlin')
        Command.excute('invwarp -w \"{}\" -o \"{}\" -r \"{}\"'.format(cout, jhu2fa_nonlin, fa_noNaN))
        
        jhulabels = '{}/{}'.format(output_path, 'jhulabels.nii')
        Command.excute('applywarp --in=\"{}\" --ref=\"{}\" --warp=\"{}\" --out=\"{}\" --interp=nn'.format(Designer.JHU_LABEL, 
                                                                                                          fa_noNaN, 
                                                                                                          jhu2fa_nonlin, 
                                                                                                          jhulabels.rstrip('.nii')))
        
        for para in paras:
            para_name = os.path.basename(para).rstrip('.nii')
            para_noNaN = para.rstrip('.nii') + '_noNaN.nii'
            para_sum = '{}/jhulabel_{}.sum'.format(output_path, para_name)
            Command.excute('mrcalc -force \"{}\" -finite \"{}\" 0 -if \"{}\"'.format(para, para, para_noNaN))
            Command.excute('mri_segstats --robust 5 --seg-erode 1 --seg \"{}\" --ctab \"{}\" --excludeid 0 --i \"{}\" --sum \"{}\"'.format(jhulabels, 
                                                                                                                                           Designer.LABEL_REFERENCE_TABLE, 
                                                                                                                                           para_noNaN, 
                                                                                                                                           para_sum))

class Freesurfer(object):

    @staticmethod
    def run(input_path, output_path, subject_name, subjects_dir='/home/shihong/Desktop/Qi_Chen/data/PROCESSED/FREESURFER_PONS/'):
        os.environ['SUBJECTS_DIR'] = subjects_dir
        command = 'recon-all -all -i \"{}\" -s \"{}\"  -brainstem-structures -parallel -openmp 6'.format(input_path, subject_name)
        Command.excute(command)
        try:
            Command.copy_files('{}/{}'.format(subjects_dir, subject_name), output_path)
        except:
            print 'Oppps! something happend'

    @staticmethod
    def update_pons(input_path, subject_name):
        """
        input_path: string, the freesurfer path
        subject_name: string, the name of subject
        return: None
        """
        if os.path.exists('{}/{}'.format(input_path, subject_name)):
            file_lst = Command.find_files('{}/{}/mri', ['brainstem*'])
            if not file_lst:
                print 'brainstem files not exists'
                print 'freesurfer for subject exists now update {}'.format(subject_name)
                os.environ['SUBJECTS_DIR'] = input_path
                command = 'recon-all -s "{}" -brainstem-structures'.format(subject_name)
                Command.excute(command)
        else:
            print 'cannot find the suject, please use Freesurfer.run() first'

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


    @staticmethod
    def register_brainstem(input_path, output_path, subject, subject_dir, brainstem, norm, register=False):
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

            brainstem_register = '{}/brainstem-in-target.nii'.format(output_path)
            Command.excute('mri_label2vol --seg \"{}\" --temp \"{}\" --o \"{}\" --reg \"{}\"'.format(brainstem, 
                                                                                                 input_nii, 
                                                                                                 brainstem_register,
                                                                                                 register_dat))
            
            inv_nii ='{}/{}_norm_inv.nii'.format(output_path, os.path.basename(input_path))
            Command.excute('mri_vol2vol --inv --targ \"{}\" --o \"{}\" --mov \"{}\" --reg \"{}\"'.format(norm, 
                                                                                                        inv_nii, 
                                                                                                        input_nii,
                                                                                                        register_dat))
        else:
            brainstem_register = '{}/brainstem-in-target.nii'.format(output_path)
            Command.excute('mri_label2vol --seg \"{}\" --temp \"{}\" --o \"{}\" --regheader'.format(brainstem, 
                                                                                                    input_nii, 
                                                                                                    brainstem_register))
            
            inv_nii ='{}/{}_norm_inv.nii'.format(output_path, os.path.basename(input_path))
            Command.excute('mri_vol2vol --inv --targ \"{}\" --o \"{}\" --mov \"{}\" --regheader'.format(norm, 
                                                                                                        inv_nii, 
                                                                                                        input_nii))
        freesurfer_home = '/usr/local/freesurfer/FreeSurferColorLUT.txt'
        brainstem_pvc_sum = '{}/{}.brainstem_pvc.sum'.format(output_path, os.path.basename(input_path))
        Command.excute('mri_segstats --robust 5 --seg-erode 1 --pv \"{}\" --seg \"{}\" --ctab \"{}\" --excludeid 0 --i \"{}\" --sum \"{}\"'.format(inv_nii, 
                                                                                                                                                   brainstem_register, 
                                                                                                                                                   freesurfer_home, 
                                                                                                                                                   input_nii, 
                                                                                                                                                   brainstem_pvc_sum))
        output_csv_mean = '{}/{}_brainstem_mean.csv'.format(output_path, 
                                                os.path.basename(input_path))
        output_csv_std = '{}/{}_brainstem_std.csv'.format(output_path, 
                                                os.path.basename(input_path))
        Command.excute('asegstats2table -i \"{}\" --transpose -m mean --all-segs -t \"{}\"'.format(brainstem_pvc_sum, 
                                                                                                   output_csv_mean))
        Command.excute('asegstats2table -i \"{}\" --transpose -m std --all-segs -t \"{}\"'.format(brainstem_pvc_sum, 
                                                                                                  output_csv_std))
