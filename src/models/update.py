import os
import pandas as pd
from src.common.command import Command

# update raw data
class Update(object):

    UPADATE_PATH = None
    SOURCE_PATH = None
    UPDATE_IGNORE = None

    @staticmethod
    def initialize(update_path, update_ignore, source_path):
        Update.UPADATE_PATH = update_path
        Update.SOURCE_PATH = source_path
        Update.UPDATE_IGNORE = update_ignore
    @staticmethod
    def check_update_subjects(copy=False):

        if not os.path.exists(Update.SOURCE_PATH):
            print 'source folder not found please check {}'.format(Update.SOURCE_PATH)
            return []
        update_set = set([os.path.basename(subject) for subject in os.listdir(Update.UPADATE_PATH)])
        source_set = set([os.path.basename(subject) for subject in os.listdir(Update.SOURCE_PATH)])
        
        updated_set = source_set - update_set
        for ui in Update.UPDATE_IGNORE:
            updated_set.discard(ui)
        for u in updated_set:
            print 'subject {} need update'.format(u)
        if copy:
            for subject in updated_set:
                source_folder = Update.SOURCE_PATH + subject
                Command.copy_files(source_folder, Update.UPADATE_PATH)
        else:
            print 'please copy subjects {} to {}'.format(updated_set, Update.UPADATE_PATH)
        return list(updated_set)
            
    @staticmethod
    def update_sum_pet(subjects, pet_path, window, choice):
        file_lst = Command.find_files(pet_path, ['*{}*_{}.csv'.format(window, choice)], ['brainstem'])
        file_dic = {}
        df_window = []
        col = []
        for f in file_lst:
            for s in subjects:
                if s in f:
                    file_dic[s] = pd.read_csv(f, sep='\t', index_col=0)
        col = sorted(file_dic.keys())
        for subject in col:
            df_window.append(file_dic[subject])
        df_window = pd.concat(df_window, axis=1, sort=False)
        df_window.columns = col
        df_window.to_csv('{}/{}_{}.csv'.format(pet_path, window, choice), sep='\t')
        print 'pet {} updated'.format(choice)
        return df_window