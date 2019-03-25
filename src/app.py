import os
from src.models.update import Update
from src.models.subject import Subject

CHOICE = ['mean', 'mean_norm', 'std', 'std_norm']

def run(update_path, update_ignore, source_path, freesurfer_path, kaiba_path, designer_path, pet_path, pet_windows, pet_norm_region):
    Update.initialize(update_path, update_ignore, source_path)
    subjects = Update.check_update_subjects()
    # for subject_name in subjects:
    #     subject = Subject(subject_name, update_path, freesurfer_path, kaiba_path, designer_path, pet_path, pet_norm_region)
    #     subject.update_all()
    # all_subjects = os.listdir(update_path)
    # for w in pet_windows:
    #     for c in CHOICE:
    #         Update.update_sum_pet(all_subjects, pet_path, w, c)
    
