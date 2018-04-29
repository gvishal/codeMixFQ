
import os
import sys
import time

from googletrans import Translator

sys.path.insert(0, '../')
#from codemix_qa_kb2.code import process_data
#from codemix_qa_kb2 import config

translator = Translator()
# translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], src='en', dest='hi')

# for translation in translations:
#     print(translation.origin, ' -> ', translation.text)

def translate_batch(source_sent_list, src, dest):
    '''Translate a given source sent list and return map of original to
    translated sentence.
    '''
    translations = translator.translate(source_sent_list, src=src, dest=dest)
    src_dest_list = []
    for translation in translations:
        src_dest_list.append(translation.origin.encode('utf8') + '\t' +translation.text.encode('utf8'))
    return src_dest_list


def translate_input_file(input_file, output_file, src, dest, batch_size=10):
    '''Translate the input file and write to output file.
    Input file format: separate sentence on every line.
    Output file format: orig sentence[tab]new sentence
    Also, we add functionality to resume from last shutdown.
    '''
    print(input_file,output_file)
    all_sentences_translated = set()
    # check if file exists, else touch file.
    try:
        open(output_file, 'r').close()
    except:
        open(output_file, 'a').close()

    with open(output_file, 'r') as fp1:
        for line in fp1:
            all_sentences_translated.add(line.strip().split('\t')[0])

    print('len(all_sentences_translated):', len(all_sentences_translated))

    def append_batch_to_file(output_file, batch_list):
        print('Unsafe to exit')
        with open(output_file, 'a') as fp:
            for line in batch_list:
                fp.write(line+'\n')
        print('Safe to exit')


    with open(input_file, 'r') as fp1:
        current_batch = []
        skipped = 0
        total_lines = 0
        for line in fp1:
            total_lines += 1
            sent = line.split('\t')
            for l in sent:
                l = l.strip()
                if l in all_sentences_translated:
                    skipped += 1
                    continue

                current_batch.append(l)

                if len(current_batch) == batch_size:
                    start = time.time()
                    ans_batch_list = translate_batch(current_batch, src=src, dest=dest)
                    print('Time for batch:', time.time()-start)
                    print('ans_batch_list:', ans_batch_list)
                    append_batch_to_file(output_file, ans_batch_list)
                    all_sentences_translated.update(current_batch)
                    current_batch = []
                    print('Processed/skipped:', total_lines, skipped)
                    time.sleep(5)

        # check if there were any unprocessed batch left
        if len(current_batch) != 0:
            ans_batch_list = translate_batch(current_batch, src=src, dest=dest)
            print(ans_batch_list)
            append_batch_to_file(output_file, ans_batch_list)
            all_sentences_translated.update(current_batch)
            current_batch = []

        print('Skipped: {}/{}'.format(skipped, total_lines))


def tokenize_vocab(file):
    '''Our vocab file was on non-tokenized words, later we tokenized our input, and
    we need to add translations for tokenized words.'''
    lang_map = process_data.load_language_map(file)
    new_map = {}
    print('Vocab size before:', len(lang_map))
    for word1, word2 in lang_map.items():
        print(word1, word2)
        word1_tokenized = process_data.clean_text(word1)
        word2_tokenized = process_data.clean_text(word2)
        if word1_tokenized in lang_map: continue
        new_map[word1_tokenized] = word2_tokenized
    lang_map.update(new_map)
    print('Vocab size after:', len(lang_map))
    with open(file, 'w') as fp:
        for word1, word2 in lang_map.items():
            fp.write('{}\t{}\n'.format(word1, word2))


def main():
    # ----------------
    # Note always give files that have single lines to be translated as input to
    # the translate method.
    # folder = '/home/jaspreet/vg/datasets/qa/SimpleQuestions_v2'
    # input_file = os.path.join(folder, 'simpleques_all_only_sentences')
    # # input_file = os.path.join(folder, 'sample')
    # output_file = os.path.join(folder, 'simpleques_translations')
    # translate_input_file(input_file, output_file, src='en', dest='hi', batch_size=20)

    # hindi words transliteration
    # input_file = config.HINDI_WORDS_LIST
    # output_file = config.HINDI_ENG_TRANS_MAP
    # translate_input_file(input_file, output_file, src='hi', dest='en', batch_size=50)

    # Hindi to english translation
    # input_file = config.HINDI_CORRECT_LIST
    # output_file = config.HINDI_CORRECT_ENG_GOOGLE_MAP
    # translate_input_file(input_file, output_file, src='hi', dest='en', batch_size=20)

    # Codemix to english translation
    # input_file = config.CODEMIX_LIST
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    translate_input_file(input_file, output_file, src='en', dest='hi', batch_size=20)

    # tokenize_vocab(output_file)


if __name__ == '__main__':
    main()