import re#for finding keywords
from collections import defaultdict#for creating a dictionary with default values
import time#for timing script
from dotenv import load_dotenv
from groq import Groq
load_dotenv()#load api key from .env file
import json


client = Groq()
start_time = time.time()


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

def extract_json_from_text(text):
    #find JSON array between [ ... ]
    json_match = re.search(r"(\[.*\])", text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

def analyze_grammar_groq(sentences_by_keyword, model="deepseek-r1-distill-llama-70b"):
    output = {}

    keywords_to_process = [k for k in sentences_by_keyword.keys() if sentences_by_keyword[k]]
    keywords_to_process = keywords_to_process[:5]

    #prompt with 5 sentences from 5 keywords (one sentence each)
    prompt_parts = []
    index_map = []
    for keyword in keywords_to_process:
        sentence_data = sentences_by_keyword[keyword][0]#take first sentence only for now
        index, sentence, matched_word = sentence_data
        prompt_parts.append(
            f'Keyword: {keyword}\n'
            f'Satz: "{sentence}"\n'
            f'Gefundene Schlüsselwörter: {matched_word}\n'
        )
        index_map.append((keyword, sentence, matched_word))

    prompt = (
        "Bitte analysiere die folgenden deutschen Sätze. "
        "Für jeden Satz gib bitte an, ob er eine oder mehrere der folgenden grammatikalischen Strukturen enthält: Passiv, Konjunktiv oder Relativsatz. "
        "Gib das Ergebnis als JSON-Liste zurück, wobei jedes Element die Schlüssel 'keyword', 'sentence', 'matched_keyword' und 'grammar' enthält.\n\n"
        + "\n---\n".join(prompt_parts)
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent, der deutsche grammatikalische Strukturen erkennt."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0,
        max_completion_tokens=1024,
        stream=False,
    )

    raw_content = response.choices[0].message.content
    # print(f"Raw response content: {raw_content}")
    parsed = extract_json_from_text(raw_content)
    if parsed is None:
        print("Could not parse JSON from the response.")
        parsed = []

    for res in parsed:
        keyword = res.get("keyword")
        if keyword not in output:
            output[keyword] = []
        output[keyword].append({
            "sentence": res.get("sentence"),
            "matched_keyword": res.get("matched_keyword"),
            "grammar": res.get("grammar", [])
        })

    #Format output like you requested
    for keyword in output.keys():
        for entry in output[keyword]:
            print(f"Keyword: {keyword}")
            print(f"Sentence: {entry['sentence']}")
            print(f"Matched keywords: {entry['matched_keyword']}")
            print(f"Detected grammar: {entry['grammar']}")
            print('--------------------------------------------------------------')

    return output


medical_keywords = [
"Infektion", "Diagnose", "Therapie", "Symptom", "Pflege", "Krankheit",
"Medikation", "Anamnese", "Behandlung", "Apotheke", "Patient", "Klinik",
"Chirurgie", "Arzt", "Medizin", "Blutdruck", "Operation", "Fieber", "Impfung", "Tumorerkrankungen"
]

parsed_data = parse_file('data/deu-de_web-public_2019_10K-sentences.txt')
matched_results = find_medical_keywords(parsed_data, medical_keywords)
# print(matched_results['Pflege'])
results_with_grammar = analyze_grammar_groq(matched_results)
# print(results_with_grammar)
# print("Medical keywords:", medical_keywords)

# client = Groq()

# stream = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant."
#         },
#         {
#             "role": "user",
#             "content": "Explain the importance of fast language models",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
#     temperature=0,
#     max_completion_tokens=1024,
#     stop=None,
#     stream=True,
# )

# for chunk in stream:
#     print(chunk.choices[0].delta.content, end="")




end_time = time.time()
print(f"\n Script finished in {end_time - start_time:.2f} seconds.")