import re#for finding keywords
from collections import defaultdict#for creating a dictionary with default values
import time#for timing script
# import spacy
import stanza
# stanza.download("de")#only need to run once, downloads the German model for Stanza


start_time = time.time()

nlp = stanza.Pipeline("de")

#This is part 1, finds medical keywords in a text file with sentences.

#parsing into dicstionary
def parse_file(filename = 'data/deu-de_web-public_2019_10K-sentences.txt'):
    data = {'index': [], 'sentence': []}

    with open (filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip('\n').split('\t')#remove \n at the end and split index + sentence
            data['index'].append(line[0])
            data['sentence'].append(line[1])
        print(data["index"][5])                 #6
        print(data["sentence"][5])              #Ab 1931 machte Schuhmann alle Atelieraufnahmen mit Kunstlicht.
    return data

#finding medical keywords in sentences
def find_medical_keywords(data,keywords):
    keyword_pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\w*', flags=re.IGNORECASE)
    matches,count = defaultdict(list),0
    for index, sentence in zip(data['index'], data['sentence']):
        found_words = keyword_pattern.findall(sentence)# findall returns all occurrences of the pattern in the string
        if found_words:
            count += 1
            for matched_word in found_words:#
                matched_in_sentence = re.search(matched_word + r'\w*', sentence, flags=re.IGNORECASE)
                if matched_in_sentence:
                    full_matched = matched_in_sentence.group(0)
                    matches[matched_word.capitalize()].append([index, sentence, full_matched])#medizin : 1, ich habe medizinische Probleme, medizinische

    print(f"Found {count} sentences with medical terms:\n\n")


    for i,keyword in enumerate(matches.keys()):
        if i == 5:
            break#for now print only 5 keywords
        for index, sentence,full_matched in matches[keyword]:
            print(f"Word [[{keyword}]] -> [[{full_matched}]] found in Sentence [[{sentence}]] at Index [[{index}]].\n")
            print(f"Total matches for {keyword} = {len(matches[keyword])}")
            print('--------------------------------------------------------------')
            break#for now print one of each keyword match
    return matches

#detect grammar structures in sentences
def detect_grammar_features(sentence):
    features = set()
    doc = nlp(sentence)
    for word in doc.sentences[0].words:
        feats = word.feats or ""

        #Passiv
        if "Voice=Pass" in feats:
            features.add("Passiv")
        #Konjunktiv
        if "Mood=Sub" in feats:
            features.add("Konjunktiv")
        #Relativsatz
        if "PronType=Rel" in feats or word.deprel == "acl:relcl":
            features.add("Relativsatz")

    return list(features)

#call the above functions to find  grammar features
def find_sentences_with_grammar(matched_results):
    count = 0
    filtered_results = defaultdict(list)
    for original_keyword in matched_results.keys():#symptom
        for i in range(len(matched_results[original_keyword])):#list of symptom matched sentences
            if original_keyword in filtered_results.keys():#diff word being used instead of the same each time for the 5 examples
                continue
            grammar = detect_grammar_features(matched_results[original_keyword][i][1])#sentence
            if grammar or 1:                                                                                #change this later******
                count += 1
                print(count)
                if count == 6:
                    return count, filtered_results
                filtered_results[original_keyword].append({
                    "index": matched_results[original_keyword][i][0],
                    "sentence": matched_results[original_keyword][i][1],
                    "keyword_matched_in_sentence": matched_results[original_keyword][i][2],
                    "grammar": grammar
                })
                
    return count,filtered_results



medical_keywords = [#i would say the keywords need to be lemmatized, e.g "Genitalbereich = Genital", which would find words like Genitalwarzen and Genitalverstümmelung
"Infektion", "Diagnose", "Therapie", "Symptom", "Pflege", "Krankheit",
"Medikation", "Anamnese", "Behandlung", "Apotheke", "Patient", "Klinik",
"Chirurgie", "Arzt", "Medizin", "Blutdruck", "Operation", "Fieber", "Impfung", "Tumorerkrankungen"
]

parsed_data = parse_file('data/deu-de_web-public_2019_10K-sentences.txt')
matched_results = find_medical_keywords(parsed_data, medical_keywords)
# print("Medical keywords:", medical_keywords)

total,grammar_results = find_sentences_with_grammar(matched_results)
print(f"\nFound {total} sentences with both medical term and grammar structure:\n")
# print(grammar_results)

count = 0
for key in grammar_results:
    for entry in grammar_results[key]:
        if count == 5:
            break
        print(f"Keyword: {key}")
        print(f"Sentence: {entry['sentence']}")
        print(f"Matched keywords: {entry['keyword_matched_in_sentence']}")
        print(f"Detected grammar: {entry['grammar']}")
        print('--------------------------------------------------------------')
        count += 1


end_time = time.time()
print(f"\n Script finished in {end_time - start_time:.2f} seconds.")