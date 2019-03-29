from src.app import run
from src.models.update import Update
from src.models.subject import Subject
import config 
import os

CHOICE = ['mean', 'mean_norm', 'std', 'std_norm']

for item in config.CONFIG:
    print '{}:     {}'.format(item, config.CONFIG[item])

def run(update_path, update_ignore, source_path, freesurfer_path, kaiba_path, designer_path, pet_path, pet_windows, pet_norm_region):
#     Update.initialize(update_path, update_ignore, source_path)
#     subjects = Update.check_update_subjects()
    update_subject_lst = os.listdir(update_path)
    for ui in update_ignore:
        try:
            update_subject_lst.remove(ui)
        except:
            pass
    for u in update_subject_lst:
        subject_path = '{}/{}'.format(update_path, u)
        subject = Subject(u, subject_path, freesurfer_path, kaiba_path, designer_path, pet_path, pet_norm_region)
        print subject
        subject._update_freesurfer()

if __name__ == '__main__':
    run(**config.CONFIG)