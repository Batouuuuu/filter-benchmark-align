from opusfilter.word_alignment import WordAlignFilter

word_align_filter = WordAlignFilter(
    src_threshold=0.2,
    tgt_threshold=0.2,
    src_tokenizer=("moses", "es"),
    tgt_tokenizer=("moses", "fr"),
    model=3
)

src_file = "../data/aligned/spanish/es.txt"
tgt_file = "../data/aligned/spanish/fr.txt"


accepted_src = "./accepted_fr.txt"
accepted_tgt = "./accepted_es.txt"  

accepted_count = 0
total_count = 0

with open(src_file, 'r', encoding='utf-8') as f_src, \
     open(tgt_file, 'r', encoding='utf-8') as f_tgt, \
     open(accepted_src, 'w', encoding='utf-8') as out_src, \
     open(accepted_tgt, 'w', encoding='utf-8') as out_tgt:

    for src_line, tgt_line in zip(f_src, f_tgt):
        total_count += 1

        src_line = src_line.strip()
        tgt_line = tgt_line.strip()

        segment_pair = (src_line, tgt_line)

        if word_align_filter.filter(segment_pair):
            accepted_count += 1
            out_src.write(src_line + '\n')
            out_tgt.write(tgt_line + '\n')


print(f"Paires totales : {total_count}")
print(f"Paires acceptées : {accepted_count}")
print(f"Taux d'acceptation : {accepted_count / total_count:.2%}")
