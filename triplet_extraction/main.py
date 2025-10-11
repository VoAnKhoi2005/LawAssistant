from triplet_extraction.src.db import *
from triplet_extraction.src.triplet_extraction import *


def main():
    conn, cursor = init_sqlite(r"./law.db")
    gpt_client = init_gpt()
    vncorenlp_client = init_vncorenlp(r"E:\Github\LawAssistant\triplet_extraction\VnCoreNLP-master")

    rows = extract_random_from_sqlite(cursor, True)
    law = ""
    title = ""
    for r in rows:
        title += r['title'] + " "
        if not (r['title'].strip().startswith("Chương") or r['title'].strip().startswith("Điều")):
            law += r['content'] + "\n"

    so_hieu = r['so_hieu']
    id = r['id']
    print(id)
    print(so_hieu + " " + title)
    print(clean_text(law))

    system_prompt_rewrite, user_prompt_rewrite = law_sentence_completion_prompt(law, so_hieu)
    rewrite_sentence = generate_response_gpt_4_1_mini(system_prompt_rewrite, user_prompt_rewrite, gpt_client)

    print("Rewrite sentence: ")
    print(rewrite_sentence)
    print()

    print("Processing sentence...")
    result = extract_triplet(rewrite_sentence, vncorenlp_client, True)
    for r in result:
        print(r)
    pass

if __name__ == "__main__":
    main()