import os
import os.path
from numpy import random
import re

loc_directories = ["lexemes/data/fixed", "lexemes/data/inflected", "lexemes/data/base", "generated_phrases"]
rules_file_name_old = "/home/emilia/PJWSTK/selidor/scrpt/seli/location_rules.tab"
rules_file_name = "./rules.tab"
loc_phrases = "/home/emilia/PJWSTK/selidor/scrpt/seli/Location.tab"
loc_phrases_sample = "/home/emilia/PJWSTK/selidor/scrpt/seli/Location_sample.tab"
final = []
consonants = ["b", "c", "ć", "d", "f", "g", "h", "j", "k", "l", "ł", "m", "n", "p", "r", "s", "t", "w", "z", "ż", "ź"]

class Location(object):
    def find_file_path(self, file_name):
        file_path=''
        for loc_dir in loc_directories:
            for dirpath, dirnames, filenames in os.walk("/home/emilia/PJWSTK/selidor/DialogueSystem/NLU/" + loc_dir):
                for filename in [f for f in filenames if f.endswith(file_name + ".tab")]:
                    file_path = os.path.join(dirpath, filename)
        if len(file_path) == 0:
            print("No such file (", file_name, ") in provided catalogues.")
        else:
            return file_path

    def load_lexemes_list(self, file_name):
        loc_file = open(file_name)
        locs = loc_file.read().splitlines()
        return locs

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
                rule = re.search(r"\[([\w\W]+)\]", loc_rule)
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
                    if fin[-1] == "w" and (len(fin)==1 or fin[-2]==" ") and word.lower()[0] in ["w","f"] and word[1].lower() in consonants:
                        fin_new = fin + "e" + " " + word
                        final_new.append(fin_new)
                    else:
                        fin_new = fin + " " + word
                        final_new.append(fin_new) 
            final=final_new

        return final

    def apply_rule(self, rule):
    #recognize the rule (@file,_word_group, word) and create proper phrase base on that
        rules_words = []
        final = []
        
        print("Processing rule: " + ' '.join([str(elem) for elem in rule]))

        for rule_part in rule:
            if rule_part[0]=="@":
                rule_part_name = rule_part[1:]
                rules_words = self.load_lexemes_list(self.find_file_path(rule_part_name))
                final = self.add_next_rule_phrase(final, rules_words)
                
            elif rule_part[0]=="_":
                group_name = rule_part[1:]
                group_words = self.read_group(group_name)
                final = self.add_next_rule_phrase(final, group_words)
                
            elif rule_part[0].isalpha():
                words = []
                words.append(rule_part[:])
                final = self.add_next_rule_phrase(final, words)
            else:
                print("Unknown part of rule: ", rule_part)
        return final


    def write_to_file(self, phrases, filename=loc_phrases):
        res_file = open(filename, "a")
        for phrase in phrases:
            res_file.write(phrase)
            res_file.write("\n")
        res_file.close()

    def write_to_sample_file(self, phrases, filename=loc_phrases_sample, nr_samples=1000):
        res_file = open(filename, "a")
        samples = random.randint(len(phrases), size=(nr_samples))
        for sample in samples:
            res_file.write(phrases[sample])
            res_file.write("\n")
        res_file.close()

loc1 = Location()
for rule in loc1.read_rules():
    data = loc1.apply_rule(rule)
    loc1.write_to_file(data)
    loc1.write_to_sample_file(data)



