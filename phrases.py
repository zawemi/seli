import os
import os.path
from numpy import random
import re
import csv
import pandas as pd

#data_directories = ["lexemes/data/fixed", "lexemes/data/inflected", "lexemes/data/base", "generated_phrases"]
data_directories = ["lexemes/data/inflected-beauty", "lexemes/data/inflected-base","lexemes/data/beauty"]
rules_file_name = "./rules_Service.tab"
output_file = "./Service.tab"
output_file_sample = "./Service_sample.tab"
final = []
consonants = ["b", "c", "ć", "d", "f", "g", "h", "j", "k", "l", "ł", "m", "n", "p", "r", "s", "t", "w", "z", "ż", "ź"]
beauty_attributes_csv = "/home/emilia/PJWSTK/selidor/scrpt/seli/service/beauty_attributes-2021-01-22.csv"
beauty_attributes_excel = "/home/emilia/PJWSTK/selidor/scrpt/seli/service/beauty_attributes-2021-01-22.xlsx"

class Phrases(object):
    def find_file_path_old(self, file_name):
        file_path=''
        for data_dir in data_directories:
            for dirpath, dirnames, filenames in os.walk("/home/emilia/PJWSTK/selidor/DialogueSystem/NLU/" + data_dir):
                for filename in [f for f in filenames if f.endswith(file_name + ".tab")]:
                    file_path = os.path.join(dirpath, filename)
        if len(file_path) == 0:
            print("No such file (", file_name, ") in provided catalogues.")
        else:
            return file_path

    def find_file_path(self, file_name):
        file_paths=[]
        filename_parts = file_name.split(".")
        filename_elements = len(filename_parts)

        for data_dir in data_directories:
            for dirpath, dirnames, filenames in os.walk("/home/emilia/PJWSTK/selidor/DialogueSystem/NLU/" + data_dir):
                for filename in filenames:
                    filename_match = 0
                    for filename_part in filename_parts:
                        
                        if filename.count(filename_part):
                            filename_match+=1
                        else: 
                            break

                        if filename_match == filename_elements:
                            file_paths.append(os.path.join(dirpath, filename))
        #print("\n".join(file_paths))                

        if len(file_paths) == 0:
            print("No such file (", file_name, ") in provided catalogues.")
        else:
            return file_paths

    def load_lexemes_list_old(self, file_name):
        data_file = open(file_name)
        lexes = data_file.read().splitlines()
        return lexes

    def load_lexemes_list(self, file_names):
        lexes = []
        for file_name in file_names:
            data_file = open(file_name)
            lexes_tmp = lexes + data_file.read().splitlines()
            lexes = lexes_tmp
        return lexes

    def find_case(self, rule):
        for element in rule:
            print(element)
            if element.find(".") >= 0:
                case = element[element.find("."):]
        return case

    def read_rules(self, rules_file_name=rules_file_name):
        #odczytuje reguły z podanego pliku
        #{RULE:[_Prep.loc,@Location_big.np.loc],RULE_PERCENT=10,LOC_PERCENT=20}
        rules = []
        rules_nr=0
        loc_rules_file = open(rules_file_name)
        loc_rules = loc_rules_file.read().splitlines()
        for loc_rule in loc_rules:
            if len(loc_rule)>0 and loc_rule[0]!="#" and loc_rule[1:5]=="RULE":
                rule = re.search(r"\[([\w\W]+)\]", loc_rule) #find everything in []
                rules.append(rule.group(1).split(sep=","))
                rules_nr+=1
        if rules_nr==0:
            print("No rules in file: ", rules_file_name)

        return rules

    def read_group(self, group_name, rules_file_name=rules_file_name):
        #odczytuje grupy fraz z podanego pliku
        #{GROUP:Prep.nom,PHRASES:["w lokalizacji","w mieście"]}
        groups = []
        group_nr=0
        loc_groups_file = open(rules_file_name)
        loc_groups = loc_groups_file.read().splitlines()

        for loc_group in loc_groups:
            print(loc_group)
            if len(loc_group)>0 and loc_group[0]!="#" and loc_group[1:6]=="GROUP":
                loc_group_name = re.search(r"GROUP:([\w\W]+),PHRASES:", loc_group).group(1)
                if loc_group_name == group_name:
                    group = re.search(r"\[([\w\W]+)\]", loc_group)
                    groups = group.group(1).split(sep=",")
                    group_nr+=1
        if group_nr==0:
            print("No group", group_name ,"in file: ", rules_file_name)
        return groups

    def add_next_rule_phrase(self, final, rules_words):
        final_new = []
        if len(final) == 0:
            final = rules_words
        else:
            for word in rules_words:
                for fin in final:
                    fin_new = fin + " " + word
                    final_new.append(fin_new) 
            final=final_new

        return final

    def apply_rule(self, rule):
    #recognize the rule (@file,_word_group, word) and create proper phrase base on that
        rules_words = [] #wszystkie elementy danej części reguły, np. zawartość pliku, zawartość grupy]
        final = [] #cała lista wyrażeń na podst. reguły
        
        print("Processing rule: " + ' '.join([str(elem) for elem in rule]))

        for rule_part in rule:
            if rule_part[0]=="@": #plik
                rule_part_name = rule_part[1:]
                rules_words = self.load_lexemes_list(self.find_file_path(rule_part_name))
                final = self.add_next_rule_phrase(final, rules_words)
                
            elif rule_part[0]=="_": #grupa
                group_name = rule_part[1:]
                group_words = self.read_group(group_name)
                final = self.add_next_rule_phrase(final, group_words)
                
            elif rule_part[0].isalpha(): #wyrażenie
                words = []
                words.append(rule_part[:])
                final = self.add_next_rule_phrase(final, words)
            else:
                print("Unknown part of rule: ", rule_part)
        return final


    def write_to_file(self, phrases, filename=output_file):
        res_file = open(filename, "a")
        for phrase in phrases:
            res_file.write(phrase)
            res_file.write("\n")
        res_file.close()

    def write_to_sample_file(self, phrases, filename=output_file_sample, nr_samples=1000):
        res_file = open(filename, "a")
        samples = random.randint(len(phrases), size=(nr_samples))
        for sample in samples:
            res_file.write(phrases[sample])
            res_file.write("\n")
        res_file.close()

class Location(Phrases):
    def add_next_rule_phrase(self, final, rules_words):
        final_new = []
        if len(final) == 0:
            final = rules_words
        else:
            for word in rules_words:
                for fin in final:
                    if fin[-1] == "w" and (len(fin)==1 or fin[-2]==" ") and word.lower()[0] in ["w","f"] and word[1].lower() in consonants:
                        fin_new = fin + "e" + " " + word
                        final_new.append(fin_new)
                    else:
                        fin_new = fin + " " + word
                        final_new.append(fin_new) 
            final=final_new

        return final

class Service(Phrases):
    print("Service")

    def read_beauty_attributes_csv(self, csv_path):
        with open(csv_path, 'rt') as csvbeauty:
            data_beauty = csv.reader(csvbeauty)
            for row in data_beauty:
                print(row)

    def read_beauty_attributes_excel(self, excel_path):
        beauty_attributes_df = pd.read_excel(excel_path, index_col=None, sheet_name="Uniwer.ista usług-beauty now", skiprows=1, header=0, engine="openpyxl") 
        beauty_attributes_filled_df = self.fill_blank_categories( beauty_attributes_df)
        print(beauty_attributes_filled_df)
        return beauty_attributes_filled_df

    def fill_blank_categories(self, df):
        df[['Branża', 'Kategoria', 'Usługa1', 'Id1']] = df[['Branża', 'Kategoria', 'Usługa1', 'Id1']].fillna(method='ffill')
        return(df)



#loc1 = Location()
#for rule in loc1.read_rules():
#    data = loc1.apply_rule(rule)
#    loc1.write_to_file(data)
#    loc1.write_to_sample_file(data)

#serv1 = Service()
#for rule in serv1.read_rules():
#    print("RULE: ",rule)
#    data = serv1.apply_rule(rule)
#    serv1.write_to_file(data)
#    serv1.write_to_sample_file(data)

serv2 = Service()
serv2.read_beauty_attributes_excel(beauty_attributes_excel)

