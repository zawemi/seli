import os
import os.path

loc_directories = ["fixed", "location", "inflected", "base"]
rules_file_name = "/home/emilia/PJWSTK/selidor/scrpt/location_rules.tab"
loc_phrases = "/home/emilia/PJWSTK/selidor/scrpt/phrases_loc.tab"
final = []

class Location(object):
    def find_file_path(self, file_name):
        for loc_dir in loc_directories:
            for dirpath, dirnames, filenames in os.walk("/home/emilia/PJWSTK/selidor/DialogueSystem/NLU/lexemes/data/" + loc_dir):
                for filename in [f for f in filenames if f.endswith(file_name + ".tab")]:
                    return os.path.join(dirpath, filename)

    def load_lexemes_list(self, file_name):
        loc_file = open(file_name)
        locs = loc_file.read().splitlines()
        return locs

    def read_rules(self, rules_file_name=rules_file_name):
        rules = []
        loc_rules_file = open(rules_file_name)
        loc_rules = loc_rules_file.read().splitlines()
        for loc_rule in loc_rules:
            rules.append(loc_rule.split(sep=","))
        return rules

    def apply_rule(self, rule):
        rules_words = []
        final = []
        final_new=[]
        print("Processing rule: " + ' '.join([str(elem) for elem in rule]))

        for rule_part in rule:
            rules_words = self.load_lexemes_list(self.find_file_path(rule_part))
            if len(final) == 0:
                final = rules_words
            else:
                for word in rules_words:
                    for fin in final:
                        fin_new = fin + " " + word
                        final_new.append(fin_new) 
                final=final_new
        return final

    def write_to_file(self, phrases, filename=loc_phrases):
        res_file = open(filename, "w")
        for phrase in phrases:
            res_file.write(phrase)
            res_file.write("\n")
        res_file.close()


loc1 = Location()
for rule in loc1.read_rules():
    loc1.write_to_file(loc1.apply_rule(rule))



