# # PIB data
# CONFIG = {
#     'update_path' : '/media/labspace/Qi_Chen/OSORIO_2019_3_5/OSORIO_C11PIB_S17-01005/ANONYMIZED/DICOMS/',
#     'update_ignore' : ['.DS_Store', '1_RAW'],
#     'source_path' : None, #'/run/user/1000/gvfs/smb-share:server=shares-cifs.nyumc.org,share=apps/petmrscan/1_PI_FOLDERS/KENT_FRIEDMAN/OSORIO_RICARDO/OSORIO_MK6240_S16-01529/ANONYMIZED/',
#     'freesurfer_path' : '/media/labspace/Qi_Chen/PROCESSED/FREESURFER/PIB/',
#     'kaiba_path' : '/media/labspace/Qi_Chen/PROCESSED/KAIBA/',
#     'designer_path' : '/media/labspace/Qi_Chen/PROCESSED/DESIGNER/PIB/',
#     'pet_path' : '/media/labspace/Qi_Chen/PROCESSED/PET/',
#     'pet_windows': ['70-90', '90-110', '90-120'], 
#     'pet_norm_region': ['Left-Cerebellum-Cortex', 'Right-Cerebellum-Cortex']
# }

# MK data
CONFIG = {
    'update_path' : '/media/labspace/Qi_Chen/OSORIO_2019_3_5/OSORIO_MK6240_S16-01529/ANONYMIZED/',
    'update_ignore' : ['.DS_Store', '1_RAW'],
    'source_path' : '', #'/run/user/1000/gvfs/smb-share:server=shares-cifs.nyumc.org,share=apps/petmrscan/1_PI_FOLDERS/KENT_FRIEDMAN/OSORIO_RICARDO/OSORIO_MK6240_S16-01529/ANONYMIZED/',
    'freesurfer_path' : '/media/labspace/Qi_Chen/PROCESSED/FREESURFER/MK6240/',
    'kaiba_path' : '/media/labspace/Qi_Chen/PROCESSED/KAIBA/',
    'designer_path' : '/media/labspace/Qi_Chen/PROCESSED/DESIGNER/',
    'pet_path' : '/media/labspace/Qi_Chen/PROCESSED/PET/MK6240_test/',
    'pet_windows': ['70-90', '90-110', '90-120'], 
    'pet_norm_region': ['Pons']
}