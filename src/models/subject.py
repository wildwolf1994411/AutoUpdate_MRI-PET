import os
import pandas as pd
import numpy as np
import pdb
from src.common.command import Command
from src.common.process import Kaiba
from src.common.process import Designer
from src.common.process import Freesurfer
from src.common.process import Register_aseg

class Subject(object):
    def __init__(self, subject, path, freesurfer_path, kaiba_path, designer_path, pet_path, pet_norm_region):
        """
        We expected each processed subject have same file structrue 
        """
        self.subject = subject
        self.path = path
        self.freesurfer_path = freesurfer_path
        self.kaiba_path = kaiba_path
        self.designer_path = designer_path
        self.pet_path = pet_path
        self.pet_norm_region = pet_norm_region

    def __repr__(self):
        return '<subject {} in {}>'.format(self.subject, self.path)

    def update_all(self):
        self._update_freesurfer()
        self._update_kaiba()
        self._update_pet_suv()
        self._update_designer()
        self._update_designer_table()

    def _update_freesurfer(self, update_pons=True):
        # update FreeSurfer
        freesurfer_require = ['*HEAD_SAG_3D*']
        if not os.path.exists('{}/{}'.format(self.freesurfer_path, self.subject)):
            print 'freesurfer for subject {} not found, will update now'.format(self.subject)

            file_lst = Command.find_files(self.path, freesurfer_require)
            if file_lst:
                print 'required file found now processing {}'.format(file_lst[0])
                if os.path.isdir(file_lst[0]):
                    image_file = os.listdir(file_lst[0])[0]
                Freesurfer.run('{}/{}'.format(file_lst[0], image_file), 
                               '{}/{}'.format(self.freesurfer_path, self.subject), 
                               subject_name=self.subject)
                print 'finished \n'
            else:
                print 'required file not exist, please check require files {}'.format(freesurfer_require)
        else:
            print 'freesurfer already exist....will check status of brainstem'
            if update_pons:
                print 'now update......'
                Freesurfer.update_pons(self.freesurfer_path, self.subject)
                print 'finished \n'
            else:
                print 'check next subject\n'
        return

    def _update_kaiba(self):
        # update Kaiba
        kaiba_require = ['*HEAD_SAG_3D*']
        if not os.path.exists('{}/{}'.format(self.kaiba_path, self.subject)):
            print 'Kaiba for subject {} not found, will update now'.format(self.subject)
            file_lst = Command.find_files(self.path, kaiba_require)
            if file_lst:
                print 'required file found now processing {}'.format(file_lst[0])
                Kaiba.run(file_lst[0], '{}/{}'.format(self.kaiba_path, self.subject))
                print 'finished \n'
            else:
                print 'required file not exist, please check require files {}\n'.format(kaiba_require)
        else:
            print 'Kaiba already exist....check next\n'

    def _update_designer(self):  
        # update Designer
        dki44_require = ['HEAD_DKI*44DIR_AP_BETA_*']
        dki45_require = ['HEAD_DKI*45DIR_AP_BETA_*']
        dki48_require = ['HEAD_DKI*48DIR_AP_BETA_*']
        dki_expection = ['_ADC_', '_COLFA_', '_FA_', '_TENSOR_', '_TRACEW_']
        dkipa_require = ['HEAD_DKI_*_PA_*']

        if not os.path.exists('{}/{}'.format(self.designer_path, self.subject)):
            print 'Designer for subject {} not found, will update now'.format(self.subject)
            dki44_lst = Command.find_files(self.path, dki44_require, dki_expection)
            dki45_lst = Command.find_files(self.path, dki45_require, dki_expection)
            dki48_lst = Command.find_files(self.path, dki48_require, dki_expection)
            dkipa_lst = Command.find_files(self.path, dkipa_require)

            if dki44_lst and dki45_lst and dki48_lst and dkipa_lst:
                print 'required file found now processing'
                dir_list = [dki44_lst[0], dki45_lst[0], dki48_lst[0]]
                dkipa = dkipa_lst[0]
                Designer.run(dir_list, dkipa, '{}/{}'.format(self.designer_path, self.subject))
            else:
                print 'required file not exist, please check require files \n'
        else:
            print 'Designer already exist....check next\n'
    
    def _update_designer_table(self, register=False):
        parameter_path = '{}/{}/designer_parameters/'.format(self.designer_path, self.subject)
        designer_parameter_images = Command.find_files(parameter_path, ['*.nii'])
        fs_subject_path = '{}/{}'.format(self.freesurfer_path, self.subject)
        aseg_require = ['aparc+aseg.mgz']
        norm_require = ['norm.mgz']
        aseg_lst = Command.find_files(fs_subject_path, aseg_require)
        norm_lst = Command.find_files(fs_subject_path, norm_require)
        for nii_image in designer_parameter_images:
            nii_image_name = os.path.basename(nii_image).rstrip('.nii')
            output_tabel_path = '{}/{}/designer_parameters_tabel/{}'.format(self.designer_path, self.subject, nii_image_name)
            if aseg_lst and norm_lst and os.path.exists(nii_image):
                print 'required file found now processing'
                if not os.path.exists(output_tabel_path):
                    os.makedirs(output_tabel_path)
                Register_aseg.run(nii_image, output_tabel_path, 
                                  self.subject, self.freesurfer_path, 
                                  aseg_lst[0], norm_lst[0],
                                  register)
            else:
                print 'cannot find require file' 

    def _update_designer_label(self):
        designer_parameters_path = '{}/{}/designer_parameters/'.format(self.designer_path, self.subject)
        designer_label_path = '{}/{}/WMroi/'.format(self.designer_path, self.subject)
        if not os.path.exists(designer_parameters_path):
            print 'designer not exist for subject {}, please update DESIGNER first'.format(self.subject)
        
        Designer.wm_extraction_fa(designer_parameters_path, designer_label_path)

    def _update_pet_suv(self, register=False):
        correction_require = ['*MIN*ATLAS*', '*MIN*HIRES*', '*ATLAS*MIN*', '*HIRES*MIN*']
        correction_expection = ['NAC']
        aseg_require = ['aparc+aseg.mgz']
        norm_require = ['norm.mgz']

        fs_subject_path = '{}/{}'.format(self.freesurfer_path, self.subject)
        
        pet_lst = Command.find_files(self.path, correction_require, correction_expection)
        aseg_lst = Command.find_files(fs_subject_path, aseg_require) # only have one for each subject
        norm_lst = Command.find_files(fs_subject_path, norm_require) # only have one for each subject
        
        if pet_lst and aseg_lst and norm_lst:
            print 'required file found now processing'
            for pet in pet_lst:
                for aseg in aseg_lst:
                    for norm in norm_lst:
                        output_path = '{}/{}/{}/'.format(self.pet_path, self.subject, os.path.basename(pet))
                        if not os.path.exists(output_path):
                            os.makedirs(output_path)

                        Register_aseg.run(pet, output_path, 
                                        self.subject, self.freesurfer_path, 
                                        aseg, norm, 
                                        register)
                        print 'save file to {}'.format(output_path)
                        pet_nii = '{}/{}_transform.nii'.format(output_path, os.path.basename(pet))
                        if self.pet_norm_region == ['Pons']:
                            pass
                        else:
                            self._pet_normalize_aseg_label(output_path, pet_nii)

            if self.pet_norm_region == ['Pons']:
                self._pet_normalize_brainstem_pons(output_path, pet_nii)
            else:
                pass
                                
        else:
            print 'cannot find require file' 

    def _pet_normalize_aseg_label(self, input_path, pet_nii):
        mean_file = Command.find_files(input_path, ['*_mean.csv'])[0]
        std_file = Command.find_files(input_path, ['*_std.csv'])[0]
        df_mean = pd.read_csv(mean_file, sep='\t', index_col=0)
        df_std = pd.read_csv(std_file, sep='\t', index_col=0)   
            
        mean_value = np.mean([df_mean['0'][r]*1.0 for r in self.pet_norm_region])
        df_mean_norm = df_mean/mean_value
        df_std_norm = df_std/mean_value

        mean_norm_file = mean_file.rstrip('.csv')+ '_norm.csv'
        std_norm_file = std_file.rstrip('.csv')+ '_norm.csv'
        df_mean_norm.to_csv(mean_norm_file, sep='\t')
        df_std_norm.to_csv(std_norm_file, sep='\t')
        
        pet_nii_norm = pet_nii.rstrip('.nii')+'_norm.nii'
        command = 'mrcalc -force \"{}\" {} -divide \"{}\"'.format(pet_nii, mean_value, pet_nii_norm)
        Command.excute(command)
        print 'finished normailize'
    
    def _pet_normalize_brainstem_pons(self, input_path, pet_nii, register=False):
        correction_require = ['*MIN*ATLAS*', '*MIN*HIRES*', '*ATLAS*MIN*', '*HIRES*MIN*']
        correction_expection = ['NAC']
        brainstem_require = ['brainstemSsLabels.v10.mgz']
        norm_require = ['norm.mgz']
        
        fs_subject_path = '{}/{}'.format(self.freesurfer_path, self.subject)

        pet_lst = Command.find_files(self.path, correction_require, correction_expection)
        brainstem_lst = Command.find_files(fs_subject_path, brainstem_require) # only have one for each subject
        norm_lst = Command.find_files(fs_subject_path, norm_require) # only have one for each subject

        if pet_lst and brainstem_lst and norm_lst:
            print 'required file found now processing'
            for pet in pet_lst:
                for brainstem in brainstem_lst:
                    for norm in norm_lst:
                        output_path = '{}/{}/{}/'.format(self.pet_path, self.subject, os.path.basename(pet))
                        if not os.path.exists(output_path):
                            os.makedirs(output_path)

                        Register_aseg.register_brainstem(pet, output_path, 
                                                         self.subject, self.freesurfer_path, 
                                                         brainstem, norm, 
                                                         register)
                        print 'save file to {}'.format(output_path)
                        pet_nii = '{}/{}_transform.nii'.format(output_path, os.path.basename(pet))

                        mean_file = Command.find_files(output_path, ['*_mean.csv'], expection=['brainstem'])[0]
                        std_file = Command.find_files(output_path, ['*_std.csv'], expection=['brainstem'])[0]
                        pons_mean_file = Command.find_files(output_path, ['*brainstem_mean.csv'])[0]
                        pons_std_file = Command.find_files(output_path, ['*brainstem_std.csv'])[0]
                        
                        df_mean = pd.read_csv(mean_file, sep='\t', index_col=0)
                        df_std = pd.read_csv(std_file, sep='\t', index_col=0)   
                        
                        df_pons_mean = pd.read_csv(pons_mean_file, sep='\t', index_col=0)
                        df_pons_std = pd.read_csv(pons_std_file, sep='\t', index_col=0)

                        df_mean = df_mean.append(df_pons_mean)
                        df_std = df_std.append(df_pons_std)

                        pons_value = float(df_mean['0']['Pons'])
                        df_mean_norm = df_mean/pons_value
                        df_std_norm = df_std/pons_value

                        mean_norm_file = mean_file.rstrip('.csv')+ '_norm.csv'
                        std_norm_file = std_file.rstrip('.csv')+ '_norm.csv'

                        df_mean.to_csv(mean_file, sep='\t')
                        df_std.to_csv(std_file, sep='\t')
                        print mean_norm_file
                        print std_norm_file
                        df_mean_norm.to_csv(mean_norm_file, sep='\t')
                        df_std_norm.to_csv(std_norm_file, sep='\t')
                        
                        pet_nii_norm = pet_nii.rstrip('.nii')+'_norm.nii'
                        command = 'mrcalc -force \"{}\" {} -divide \"{}\"'.format(pet_nii, pons_value, pet_nii_norm)
                        Command.excute(command)
                        print 'finished normailize'
