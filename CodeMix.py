
import sys
import spacy
import time
from googletrans import Translator

nlp = spacy.load('en')
THRESHHOLD = 5
translator = Translator()
Prohibited_tag = ['VBZ','IN']
Prohibited_dep = ['aux','prep']
Prohibited_pos = ['NUM','SYM','ADP','PROPN']
# translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], src='en', dest='hi')

# for translation in translations:
#     print(translation.origin, ' -> ', translation.text)
def select_replace(sentences,base_sent,sub,rec,st=0):
    if rec==0:
        return
    tokens = base_sent.split()
    for i in xrange(st,len(tokens)):
        if tokens[i] not in sub.keys():
            continue
        tmp = tokens[i]
        tokens[i]=sub[tokens[i]]
        new_sent = " ".join(tokens)
        print 'new_Sent:',new_sent
        if new_sent not in sentences:
            sentences.append(new_sent)
        select_replace(sentences,new_sent,sub,rec-1,i+1)
        tokens[i] = tmp
        print 'tokens:',tokens



def codeMixSentence(src_sentence,base,mix_lang):
    '''Generate multiple codeMix sentence based on heuristics
    '''
    base_src_sentence = translator.translate(src_sentence, src='en', dest=base).text
    #base_src_sentence = base_src_sentence_trans[0].text
    try:
        tmp_tokens = nlp(unicode(src_sentence))
    except:
        return []
    src_tokens = []
    for token in tmp_tokens:
        # Write logic for allowing token to replace in base sentence.
        if token.tag_ not in Prohibited_tag and token.dep_ not in Prohibited_dep and token.pos_ not in Prohibited_pos:
            src_tokens.append(token)
    print 'src_token:',src_tokens
    base_tokens = base_src_sentence.split()
    sub = {}
    print 'base_token:', base_tokens
    translations = translator.translate(base_tokens, src=base, dest=mix_lang)
    for translation in translations:
        print(translation.origin, ' -> ', translation.text)
        trans_tokens = nlp(unicode(translation.text))
        print 'translates lemma_',trans_tokens[0].lemma_
        for token in src_tokens:
            print 'token lemma_',token.lemma_
            if token.lemma_ == trans_tokens[0].lemma_:
                sub[translation.origin] = token.text
                print 'subs:',translation.origin,token.text
                src_tokens.remove(token)
                break
    final_sent = []
    select_replace(final_sent,base_src_sentence,sub,min(THRESHHOLD,len(sub)),0)
    return final_sent

def writeSentences(output_file,src_sent,codeMix_sents):
    print('Unsafe to exit')
    with open(output_file, 'a') as fp:
        fp.write('\nsrc: '+src_sent.encode('utf-8')+'\n code-mix sentences:\n')
    with open(output_file, 'a') as fp:
        for line in codeMix_sents:
            fp.write(line.encode('utf-8')+'\n')
    print('Safe to exit')

def generateCodemixSentence(input_file, output_file,column_number=0,base='hi',mix_lang='en'):
    '''CodeMix the input file and write to output file.
    Input file format: separate sentence on every line.
    Output file format: orig sentence[tab]new sentence
    '''
    print input_file,output_file
    with open(output_file, 'w') as fp1:
        fp1.write('')

    with open(input_file, 'r') as fp:
        for line in fp:
            sents = line.split('\t')
            try:
                src_sent = sents[column_number].strip()
            except:
                continue
            print src_sent
            flag, attempt = True, 0
            while flag:
                try:
                    code_mix_sents = codeMixSentence(src_sent,base,mix_lang)
                    flag = False
                except:
                    print "Error occured trying in 5 sec"
                    if attempt < THRESHHOLD:
                        time.sleep(5)
                        continue
                    else:
                        code_mix_sents = []
            if len(code_mix_sents) > 0:
                writeSentences(output_file,src_sent,code_mix_sents)




def main():

    if len(sys.argv) < 2:
        print "Usage <input_file> <output_file> <column_number=0>  <base_lang='hi'> <mix_lang='en'>"
        exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if len(sys.argv) == 2:
        generateCodemixSentence(input_file, output_file)
        exit(0)
    elif len(sys.argv) < 5:
        print "Usage <input_file> <output_file> <column_number=0>  <base_lang='hi'> <mix_lang='en'>"
        exit(1)
    column_number = int(sys.argv[3])
    base = sys.argv[4]
    mix_lang = sys.argv[5]
    generateCodemixSentence(input_file, output_file, column_number, base, mix_lang)

    # tokenize_vocab(output_file)


if __name__ == '__main__':
    main()