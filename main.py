from quize_creator.pdf_to_text_Conversion import pdftotxt
import os
from nltk.corpus import wordnet
import nltk
import random
import re
import json
import sys

debug = False


def de_emojify(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def namedentitylist(tuplelist):
    entity = []

    for tuplist in tuplelist:
        for tup in tuplist:
            entity.append(tup[1])

    entity_set = set(entity)
    entity_dict = dict()

    for ent in entity_set:
        entity_dict[ent] = list()

    for tuplist in tuplelist:
        for tup in tuplist:
            if tup[0] not in entity_dict[tup[1]]:
                entity_dict[tup[1]].append(tup[0])
    # print(entity_dict)
    return entity_dict


def mcq_maker(sent_with_tags, tag_dict, tag_to_focus, number_of_options=5):
    flag = True
    question = ""
    correct = ""
    # print(sent_with_tags)
    for word, tag in sent_with_tags:
        wordforque = word
        if tag == tag_to_focus and flag:
            correct = wordforque
            wordforque = "________"
            flag = False
        question = question + " " + wordforque
    question = question + "."
    options = []
    option_number = random.randint(0, number_of_options - 1)

    trap_count = 0
    list_of_words_for_options = list(set(tag_dict[tag_to_focus]).union(set(similar_words(correct))))
    while len(options) < number_of_options:

        if len(options) == option_number:
            options.append(correct)
        else:
            option = list_of_words_for_options[random.randint(0, len(set(tag_dict[tag_to_focus])) - 1)]
            if option in options or option == correct:
                trap_count += 1
            else:
                options.append(option)
                trap_count = 0
        if trap_count == 700:
            if debug:
                print("Error:--> (debug_trap- options generation potential infinity loop): Cant generate the the MCQ "
                      "for the given statement.[X]")
            options = None
            correct = None
            break
    if correct == "":
        correct = None
    return question, options, correct


def wordtagger(sents):
    # print(sents)
    if not isinstance(sents, list):
        sents = [sents]
    sentwithtags = []
    for sent in sents:
        sentword = nltk.word_tokenize(sent)
        sentwithtags.append(nltk.pos_tag(sentword))
    return sentwithtags


def paratosent(para):
    sent = para.split(". ")
    return sent


def similar_words(word):
    synonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            if l.antonyms() is not True:
                synonyms.append(l.name())

    return list(set(synonyms))


def opposit_words(word):
    antonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

    return list(set(antonyms))


path_directory = os.getcwd() + "/book"
print(path_directory)
# pdftotxt(source=path_directory)

files = [path_directory + "/" + str(x) for x in os.listdir(path_directory)]

totalcontent = ""
for file in files:
    try:
        content = open(file).read()
        totalcontent += content
    except:
        print("Cant open the ", file)
totalcontent = de_emojify(totalcontent.replace("\n", " "))
sent = paratosent(totalcontent)

sent_with_tags = wordtagger(sent)
namedlistwithtags = namedentitylist(sent_with_tags)

tags = ["NN", "NNP", "NNS", "NNPS"]
question_number = 0
number_of_questions = 5000
questions_to_write = dict()
question_to_write = dict()
content = []
print("quiz generation started.")
for i in range(number_of_questions):  # range(len(sent_with_tags)):
    if i >= len(sent_with_tags):
        pass
    else:
        question, options, correct = mcq_maker(sent_with_tags[i], namedlistwithtags,
                                               tags[random.randint(0, len(tags) - 1)],
                                               number_of_options=4)
        if correct is None or options is None:
            pass
        else:
            # print("_____________________________________________________")
            # print("Question ", question_number + 1, ".", question)
            # for i in range(len(options)):
            #    print(i + 1, ". ", options[i])
            # print("Correct Answer is --> ", correct)

            options_dict = dict()
            for i in range(len(options)):
                options_dict[i] = options[i]

            question_to_write["Question"] = question
            question_to_write["Option"] = options_dict.copy()
            question_to_write["Correct Option"] = correct
            # print(questions_to_write)
            questions_to_write[question_number + 1] = question_to_write.copy()
            question_number += 1

with open('post/quiz.json', 'a') as convert_file:
    convert_file.write(json.dumps(questions_to_write))
sys.exit("post/quiz.json")
