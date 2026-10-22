
from pathlib import Path
from collections import Counter
import regex as re

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

def merge_pair(tokens, pair):
    result = []
    i = 0

    while i < len(tokens):
        if (
            i + 1 < len(tokens)
            and (tokens[i], tokens[i + 1]) == pair
        ):
            result.append(pair[0] + pair[1])
            i += 2
        else:
            result.append(tokens[i])
            i += 1

    return tuple(result)


def train_bpe(input_path, vocab_size, special_tokens):
    # Step 1: Initialize vocabulary
    vocab = {i: bytes([i]) for i in range(256)}

    # Step 2: Add special tokens
    for token in special_tokens:
        vocab[len(vocab)] = token.encode("utf-8")

    # Step 3: Read corpus and pre-tokenize
    text = Path(input_path).read_text(encoding="utf-8")

    # Split corpus by special tokens
    if special_tokens:
        pattern = "|".join(
            re.escape(token)
            for token in sorted(special_tokens, key=len, reverse=True)
        )
        chunks = re.split(pattern, text)
    else:
        chunks = [text]

    # Count pre-tokens from each chunk
    pretoken_counts = Counter()

    for chunk in chunks:
        for m in re.finditer(PAT, chunk):
            pretoken_counts[m.group()] += 1

    # Step 4: Convert pre-tokens into byte token sequences
    byte_token_counts = Counter()

    for token, freq in pretoken_counts.items():
        byte_tokens = tuple(
            bytes([b]) for b in token.encode("utf-8")
        )
        byte_token_counts[byte_tokens] += freq
    # print(byte_token_counts.most_common(10))
    # Step 5-7: Iterative BPE training
    merges = []

    while len(vocab) < vocab_size:

        # Step 5: Count adjacent token pairs
        pair_counts = Counter()

        for tokens, freq in byte_token_counts.items():
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                pair_counts[pair] += freq

        # Stop if no more pairs can be merged
        if not pair_counts:
            break

        # Step 6.1: Select the most frequent pair
        best_pair = max(
            pair_counts,
            key=lambda pair: (pair_counts[pair], pair)
        )

        # Step 6.2: Add merged token to vocabulary
        new_token = best_pair[0] + best_pair[1]
        # print(f"Current vocab size: {len(vocab)}")
        # print(f"Merging pair: {best_pair} -> {new_token}")
        vocab[len(vocab)] = new_token
        merges.append(best_pair)

        # Step 6.3: Apply merge to all pre-tokens
        new_counts = Counter()

        for tokens, freq in byte_token_counts.items():
            new_tokens = merge_pair(tokens, best_pair)
            new_counts[new_tokens] += freq

        byte_token_counts = new_counts

    return vocab, merges


if __name__ == "__main__":
    vocab, merges = train_bpe(
        input_path="tests/fixtures/corpus.en",
        vocab_size=260,
        special_tokens=["<|endoftext|>"]
    )

    print("Vocabulary size:", len(vocab))
    print("Number of merges:", len(merges))
    print("Merges:", merges)

    print("New tokens:")
    for i in range(len(vocab)):
        print(i, vocab[i])
